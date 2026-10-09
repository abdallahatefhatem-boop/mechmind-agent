import re
import uuid
from typing import Any, Dict, List, Optional
import psycopg
import requests
import streamlit as st

# --- Configuration ---
API_URL = "http://localhost:8000/api/v1/ask"
DB_URI = "postgresql://postgres:postgres@localhost:5432/engineering_db"


# --- Database Helpers ---
def init_db():
    """Initialize PostgreSQL tables for chat sessions and history."""
    with psycopg.connect(DB_URI) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS ui_chat_sessions (
                    thread_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS ui_chat_messages (
                    id SERIAL PRIMARY KEY,
                    thread_id TEXT REFERENCES ui_chat_sessions(thread_id) ON DELETE CASCADE,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        conn.commit()


def get_sessions() -> List[tuple]:
    """Retrieve all chat sessions ordered by creation date."""
    with psycopg.connect(DB_URI) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT thread_id, title FROM ui_chat_sessions ORDER BY created_at DESC")
            return cur.fetchall()


def get_messages(thread_id: str) -> List[Dict[str, str]]:
    """Retrieve message history for a specific thread."""
    with psycopg.connect(DB_URI) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT role, content FROM ui_chat_messages WHERE thread_id = %s ORDER BY created_at ASC",
                (thread_id,),
            )
            return [{"role": row[0], "content": row[1]} for row in cur.fetchall()]


def save_session(thread_id: str, title: str):
    """Save new session record."""
    with psycopg.connect(DB_URI) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO ui_chat_sessions (thread_id, title) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                (thread_id, title),
            )
        conn.commit()


def save_message(thread_id: str, role: str, content: str):
    """Save message record to thread history."""
    with psycopg.connect(DB_URI) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO ui_chat_messages (thread_id, role, content) VALUES (%s, %s, %s)",
                (thread_id, role, content),
            )
        conn.commit()


def delete_session(thread_id: str):
    """Delete a chat session and its associated messages from the database."""
    with psycopg.connect(DB_URI) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM ui_chat_messages WHERE thread_id = %s", (thread_id,))
            cur.execute("DELETE FROM ui_chat_sessions WHERE thread_id = %s", (thread_id,))
        conn.commit()


# --- Formatting & Text Cleaning Helpers (ChatGPT Style) ---
def format_latex_for_streamlit(text: str) -> str:
    """
    Converts raw LaTeX delimiters and common commands to Streamlit-compatible
    Markdown / KaTeX so the output renders correctly.
    """
    if not text:
        return ""

    # Block math:  \[ ... \]  →  $$ ... $$
    text = re.sub(r'\\\[\s*', '\n$$\n', text)
    text = re.sub(r'\s*\\\]', '\n$$\n', text)

    # Inline math:  \( ... \)  →  $ ... $
    text = re.sub(r'\\\(\s*', ' $', text)
    text = re.sub(r'\s*\\\)', '$ ', text)

    # \boxed{x}  →  **x**
    text = re.sub(r'\\boxed\{([^}]+)\}', r'**\1**', text)

    # \frac{a}{b}  →  (a/b)
    text = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'(\1/\2)', text)

    # \cdot  →  ·
    text = text.replace(r'\cdot', '·')

    # \times  →  ×
    text = text.replace(r'\times', '×')

    # \pi  →  π
    text = text.replace(r'\pi', 'π')

    # \approx  →  ≈
    text = text.replace(r'\approx', '≈')

    # \leq / \geq  →  ≤ / ≥
    text = text.replace(r'\leq', '≤').replace(r'\geq', '≥')

    # \sqrt{x}  →  √(x)
    text = re.sub(r'\\sqrt\{([^}]+)\}', r'√(\1)', text)

    return text


def clean_explanation(text: str) -> str:
    """
    Aggressively cleans raw LLM explanation text for neat Streamlit rendering.

    Handles these specific artifact patterns observed in production:
      A. Raw asterisk sequences  ∗∗Ftext∗∗  →  **Ftext**
      B. Orphan subscript lines  (lone word after formula, e.g. "total" / "bolt")
      C. Duplicate rendered equations  (LLM outputs formula twice in diff formats)
      D. Blank lines before headings / step labels / bullets / $$ fences
      E. Collapses 3+ consecutive blank lines → 2
    """
    if not text:
        return ""

    # ── Pass 1: character-level artifact removal ────────────────────────────

    # A. Replace Unicode asterisk  ∗  with plain  *  so ** bold works
    text = text.replace('∗', '*')

    # Remove stray LaTeX subscript/superscript leftovers like "_ total" or "^ 2"
    # that appear as isolated text after rendering artifacts
    text = re.sub(r'(?<![\w])_\s*([\w]+)', r'\1', text)   # lone _word → word
    text = re.sub(r'(?<![\w])\^\s*([\w]+)', r'\1', text)  # lone ^word → word

    # ── Pass 2: line-level cleanup ──────────────────────────────────────────
    lines = text.splitlines()
    result: List[str] = []

    # Heuristic: an "orphan subscript line" is a line that is:
    #   - 1-3 words, all word-chars (no math operators)
    #   - immediately follows a line that ends with a number or unit
    #   - AND the same token(s) already appear in the previous non-empty line
    def _is_orphan_subscript(line: str, prev_non_empty: str) -> bool:
        s = line.strip()
        if not s or len(s) > 40:
            return False
        # Must be short alpha/digit words only
        if not re.fullmatch(r'[\w\s]+', s):
            return False
        # All tokens must already appear (in any order) in the previous line
        tokens = s.lower().split()
        prev_lower = prev_non_empty.lower()
        return all(tok in prev_lower for tok in tokens)

    prev_non_empty = ""
    for i, line in enumerate(lines):
        stripped = line.strip()

        # Skip orphan subscript lines (duplicate rendering artifact)
        if stripped and _is_orphan_subscript(stripped, prev_non_empty):
            continue

        # Track last non-empty line for the heuristic above
        if stripped:
            prev_non_empty = stripped

        prev_result = result[-1].strip() if result else ""

        # Rule 1 – blank line before Markdown headings (##, ###)
        if re.match(r'^#{1,4}\s', stripped) and prev_result != "":
            result.append("")

        # Rule 2 – blank line before bold step/section labels
        elif re.match(r'^\*\*(?:Step|Part|Section|Result|Note|Warning|Given|Final|Summary)\b',
                      stripped, re.IGNORECASE) and prev_result != "":
            result.append("")

        # Rule 3 – blank line before first item of a bullet/numbered list
        elif (re.match(r'^[-*•]\s|^\d+[.):]\s', stripped)
              and prev_result != ""
              and not re.match(r'^[-*•]\s|^\d+[.):]\s', prev_result)):
            result.append("")

        # Rule 4 – blank line before / after $$ math fences
        elif stripped == "$$":
            if prev_result != "":
                result.append("")
            result.append(line)
            next_stripped = lines[i + 1].strip() if i + 1 < len(lines) else ""
            if next_stripped != "":
                result.append("")
            continue

        result.append(line)

    # ── Pass 3: collapse 3+ blank lines → 2, strip edges ───────────────────
    joined = "\n".join(result)
    cleaned = re.sub(r'\n{3,}', '\n\n', joined)

    return cleaned.strip()


def format_raw_calc_table(calc_result: Dict[str, Any]) -> str:
    """Formats raw calculation dictionaries into a clean Markdown table."""
    if not calc_result:
        return ""

    table_lines = [
        "### 📊 Calculation Summary\n",
        "| Parameter / Metric | Calculated Value |",
        "| :--- | :--- |",
    ]
    for key, val in calc_result.items():
        formatted_key = key.replace("_", " ").title()
        formatted_val = f"`{val:,.6g}`" if isinstance(val, (int, float)) else f"`{val}`"
        table_lines.append(f"| **{formatted_key}** | {formatted_val} |")

    return "\n".join(table_lines)


def build_chatgpt_response(explanation: str, calc_result: Optional[Dict[str, Any]]) -> str:
    """
    Builds a clean, ChatGPT-style Markdown response:
    - Runs LaTeX delimiter conversion first.
    - Then applies spacing / readability cleanup.
    - Falls back to a calculation table when there is no explanation.
    """
    if explanation:
        latex_fixed = format_latex_for_streamlit(explanation.strip())
        return clean_explanation(latex_fixed)
    elif calc_result and isinstance(calc_result, dict):
        return format_raw_calc_table(calc_result)
    else:
        return "⚠️ No calculation output or explanation was returned for this request."


# --- Streamlit Application Setup ---
st.set_page_config(
    page_title="MechMind Engineering Assistant",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom UI styling for ChatGPT-like readability and clean LaTeX math blocks
st.markdown("""
    <style>
        .stChatMessage { padding: 14px 18px; border-radius: 10px; margin-bottom: 10px; }
        .stMarkdown table { width: 100% !important; margin: 15px 0; border-collapse: collapse; }
        .stMarkdown th { background-color: #2b2c36; color: #ffffff; }
        .katex-display { margin: 1em 0; overflow-x: auto; overflow-y: hidden; }
    </style>
""", unsafe_allow_html=True)

# Initialize database
try:
    init_db()
except Exception as e:
    st.error(f"Failed to connect to PostgreSQL database: {e}")

# Initialize session state for current chat thread
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.messages = []


# --- Sidebar: Chat History Management ---
with st.sidebar:
    st.title("⚙️ MechMind AI")
    
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()
        
    st.divider()
    st.subheader("Chat History")
    
    try:
        sessions = get_sessions()
        for session_id, title in sessions:
            is_active = (session_id == st.session_state.thread_id)
            btn_style = "primary" if is_active else "secondary"
            
            col1, col2 = st.columns([0.82, 0.18])
            
            with col1:
                if st.button(f"💬 {title}", key=f"select_{session_id}", use_container_width=True, type=btn_style):
                    st.session_state.thread_id = session_id
                    st.session_state.messages = get_messages(session_id)
                    st.rerun()
            
            with col2:
                if st.button("🗑️", key=f"del_{session_id}", use_container_width=True):
                    delete_session(session_id)
                    
                    if session_id == st.session_state.thread_id:
                        st.session_state.thread_id = str(uuid.uuid4())
                        st.session_state.messages = []
                    st.rerun()

    except Exception as e:
        st.caption("Unable to load chat history.")


# --- Main Chat Area ---
st.title("MechMind Engineering Assistant")
st.caption("AI-powered mechanical calculations, kinematics, and structural analysis.")

# Render existing chat message history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(format_latex_for_streamlit(msg["content"]))

# User Input Handling
if prompt := st.chat_input("Ask an engineering question or enter calculation values..."):
    
    # 1. Initialize session title on first query
    if not st.session_state.messages:
        title = prompt[:32] + "..." if len(prompt) > 32 else prompt
        save_session(st.session_state.thread_id, title)
        
    # 2. Render & store user prompt
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_message(st.session_state.thread_id, "user", prompt)
    
    with st.chat_message("user"):
        st.markdown(prompt)

    # 3. Call MechMind Backend & Render Assistant Output
    with st.chat_message("assistant"):
        with st.spinner("Analyzing problem and computing mechanics..."):
            try:
                payload = {
                    "query": prompt,
                    "thread_id": st.session_state.thread_id
                }
                
                response = requests.post(API_URL, json=payload, timeout=60)
                response.raise_for_status()
                data = response.json()

                explanation = data.get("explanation", "")
                selected_tool = data.get("selected_tool", [])
                calc_result = data.get("calculation_result")
                validation_result = data.get("validation_result")

                # Format output cleanly into ChatGPT layout
                formatted_response = build_chatgpt_response(explanation, calc_result)
                
                # Render primary formatted response
                st.markdown(formatted_response)
                
                # Keep technical execution metadata organized in a collapsible drawer
                with st.expander("🛠️ Execution Details & Tool Outputs"):
                    if selected_tool:
                        st.write(f"**Tools Executed:** `{', '.join(selected_tool)}`")
                    if validation_result:
                        st.write("**Validation Result:**")
                        st.json(validation_result)
                    if calc_result:
                        st.write("**Raw Tool Output:**")
                        st.json(calc_result)

                # Save formatted markdown response to database and session state
                st.session_state.messages.append({"role": "assistant", "content": formatted_response})
                save_message(st.session_state.thread_id, "assistant", formatted_response)

            except requests.exceptions.RequestException as e:
                error_msg = f"❌ **Connection Error:** Could not reach the MechMind API. Ensure backend is running at `{API_URL}`."
                st.error(error_msg)