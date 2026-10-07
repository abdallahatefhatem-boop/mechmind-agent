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
                    thread_id TEXT REFERENCES ui_chat_sessions(thread_id),
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


# --- Response Formatting Helpers ---
def format_raw_calc_table(calc_result: Dict[str, Any]) -> str:
    """Formats raw calculation dictionaries into a clean Markdown table."""
    if not calc_result:
        return ""
    
    table_lines = [
        "### 📊 Calculation Summary\n",
        "| Parameter / Metric | Calculated Value |",
        "| :--- | :--- |"
    ]
    for key, val in calc_result.items():
        formatted_key = key.replace("_", " ").title()
        formatted_val = f"`{val:,.6g}`" if isinstance(val, (int, float)) else f"`{val}`"
        table_lines.append(f"| **{formatted_key}** | {formatted_val} |")
        
    return "\n".join(table_lines)


def build_chatgpt_response(explanation: str, calc_result: Optional[Dict[str, Any]]) -> str:
    """Combines explanation text and calculation tables into a clean, ChatGPT-style output."""
    explanation_clean = explanation.strip() if explanation else ""
    
    if explanation_clean:
        return explanation_clean
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

# Custom UI styling for ChatGPT-like readability
st.markdown("""
    <style>
        .stChatMessage { padding: 12px 16px; border-radius: 8px; }
        .stMarkdown table { width: 100% !important; margin: 15px 0; }
        .stMarkdown th { background-color: #f0f2f6; }
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
            
            if st.button(f"💬 {title}", key=session_id, use_container_width=True, type=btn_style):
                st.session_state.thread_id = session_id
                st.session_state.messages = get_messages(session_id)
                st.rerun()
    except Exception as e:
        st.caption("Unable to load chat history.")


# --- Main Chat Area ---
st.title("MechMind Engineering Assistant")
st.caption("AI-powered mechanical calculations, kinematics, and structural analysis.")

# Render existing chat message history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

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

                # Format output cleanly
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