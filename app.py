import streamlit as st
import requests
import json
import os
import uuid

# ─── Page Config & CSS ──────────────────────────────────────────────────────────
st.set_page_config(page_title="MechMind Agent", page_icon="⚙️")

# Add spacing between messages to make it easy to read (not stuck together)
st.markdown("""
<style>
    .stChatMessage {
        margin-bottom: 3rem !important; 
        line-height: 1.8 !important;
    }
    /* Add some visual separation for the markdown */
    hr {
        margin-top: 1.5rem;
        margin-bottom: 1.5rem;
        border: 0;
        border-top: 1px solid rgba(255,255,255,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ─── Constants ──────────────────────────────────────────────────────────────────
API_BASE = "http://localhost:8000/api/v1"
HISTORY_FILE = "chat_history.json"

NODE_LABELS = {
    "extract_problem":       "Analyzing problem type",
    "extract_equation_name": "Identifying equations",
    "tool_node":             "Executing calculations",
    "chat_node":             "Reasoning",
    "format_output_node":    "Formatting final response",
    "general_chat_node":     "Chatting",
}

# ─── History Management ──────────────────────────────────────────────────────────
def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = load_history()

if "current_thread_id" not in st.session_state:
    st.session_state.current_thread_id = str(uuid.uuid4())
    
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am your Engineering AI Assistant. How can I help you today?"}
    ]

# ─── Sidebar ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ MechMind")
    
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        st.session_state.current_thread_id = str(uuid.uuid4())
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I am your Engineering AI Assistant. How can I help you today?"}
        ]
        st.rerun()
        
    st.divider()
    st.caption("Chat History")
    
    # Show history in sidebar
    for t_id, chat_data in reversed(st.session_state.chat_history.items()):
        title = chat_data.get("title", "Empty Chat")
        if st.button(f"💬 {title}", key=f"hist_{t_id}", use_container_width=True):
            st.session_state.current_thread_id = t_id
            st.session_state.messages = chat_data.get("messages", [])
            st.rerun()

# ─── Main Chat Interface ────────────────────────────────────────────────────────
st.title("MechMind Assistant")

# Display chat history for current session
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

# ─── Streaming Logic ─────────────────────────────────────────────────────────────
def stream_query(query_text: str, thread_id: str):
    params = {"query": query_text, "thread_id": thread_id}
    try:
        with requests.get(
            f"{API_BASE}/ask/stream",
            params=params,
            stream=True,
            timeout=120,
            headers={"Accept": "text/event-stream"},
        ) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines(decode_unicode=True):
                if line.startswith("data: "):
                    try:
                        yield json.loads(line[6:])
                    except json.JSONDecodeError:
                        continue
    except requests.exceptions.RequestException as e:
        yield {"event": "error", "message": str(e)}

def format_final_answer(explanation, calc_result, tools) -> str:
    # Adding line breaks and separators so the answer isn't clustered together
    ans = f"{explanation}\n\n"
    
    if calc_result:
        ans += "---\n\n### 📊 Calculation Results\n\n"
        for k, v in calc_result.items():
            ans += f"- **{k}**: `{v}`\n"
        ans += "\n"
        
    if tools:
        ans += f"\n*🔧 Tools used: {', '.join(tools)}*\n"
        
    return ans

# Handle user input
if prompt := st.chat_input("Enter your engineering question here..."):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Save title if it's the first user message
    if st.session_state.current_thread_id not in st.session_state.chat_history:
        st.session_state.chat_history[st.session_state.current_thread_id] = {
            "title": prompt[:35] + "...",
            "messages": st.session_state.messages.copy()
        }
    else:
        st.session_state.chat_history[st.session_state.current_thread_id]["messages"] = st.session_state.messages.copy()
    
    save_history(st.session_state.chat_history)
    
    with st.chat_message("user"):
        st.markdown(prompt)

    # Show assistant response
    with st.chat_message("assistant"):
        status_placeholder = st.empty()
        content_placeholder = st.empty()
        
        final_text = ""
        final_result = None
        
        for event in stream_query(prompt, st.session_state.current_thread_id):
            ev = event.get("event")
            
            if ev == "start":
                status_placeholder.caption("⏳ Starting processing...")
                
            elif ev == "node":
                node = event.get("node", "")
                label = NODE_LABELS.get(node, node)
                status_placeholder.caption(f"🔄 {label}...")
                
            elif ev == "result":
                final_result = event.get("data", {})
                
            elif ev == "error":
                status_placeholder.error(f"Error: {event.get('message', '')}")
                break
                
            elif ev == "end":
                status_placeholder.empty()
                break
        
        # Display final response
        if final_result:
            final_text = format_final_answer(
                final_result.get("explanation", ""),
                final_result.get("calculation_result", {}),
                final_result.get("selected_tool", [])
            )
            content_placeholder.markdown(final_text)
            
            # Save assistant message to history
            st.session_state.messages.append({"role": "assistant", "content": final_text})
            st.session_state.chat_history[st.session_state.current_thread_id]["messages"] = st.session_state.messages.copy()
            save_history(st.session_state.chat_history)
