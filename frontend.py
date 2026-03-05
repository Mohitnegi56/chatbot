import streamlit as st
from backend_tool_langgraph import chatbot, retrieve_chat_history
from langchain_core.messages import HumanMessage
import uuid
from datetime import datetime


st.set_page_config(
    page_title="LangGraph AI",
    page_icon="🤖",
    layout="wide"
)

# ---------------------------
# UI Styling
# ---------------------------

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#0f172a,#1e293b);
    color:white;
}

section[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(12px);
}

.typing {
    font-size:14px;
    opacity:0.7;
    animation: blink 1s infinite;
}

@keyframes blink {
  50% { opacity:0.2; }
}

.toolmsg{
    background:#111827;
    padding:6px 10px;
    border-radius:6px;
    margin-bottom:5px;
    font-size:13px;
    color:#38bdf8;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------
# Helpers
# ---------------------------

def generate_thread_id():
    return str(uuid.uuid4())[:8]


def reset_chat():
    thread_id = generate_thread_id()
    st.session_state.thread_id = thread_id
    st.session_state.message_history = []
    st.session_state.chat_threads.append(thread_id)
    st.session_state.titles[thread_id] = "New Chat"


def delete_thread(thread_id):

    if thread_id in st.session_state.chat_threads:
        st.session_state.chat_threads.remove(thread_id)

    if thread_id in st.session_state.titles:
        del st.session_state.titles[thread_id]

    if st.session_state.thread_id == thread_id:
        reset_chat()


def load_conversation(thread_id):

    state = chatbot.get_state(
        config={"configurable": {"thread_id": thread_id}}
    )

    if not state:
        return []

    messages = state.values.get("messages", [])

    formatted = []

    for msg in messages:

        if msg.type == "human":
            role = "user"

        elif msg.type == "ai":
            role = "assistant"

        else:
            continue

        formatted.append({
            "role": role,
            "content": msg.content,
            "time": datetime.now().strftime("%H:%M")
        })

    return formatted


# ---------------------------
# Session State
# ---------------------------

if "thread_id" not in st.session_state:
    st.session_state.thread_id = generate_thread_id()

if "message_history" not in st.session_state:
    st.session_state.message_history = []

if "titles" not in st.session_state:
    st.session_state.titles = {}

if "chat_threads" not in st.session_state:

    threads = retrieve_chat_history()

    if threads:
        st.session_state.chat_threads = threads
    else:
        st.session_state.chat_threads = [st.session_state.thread_id]


# ---------------------------
# Sidebar
# ---------------------------

with st.sidebar:

    st.markdown("## 🤖 LangGraph AI")
    st.caption("Tool Enabled Agent")

    if st.button("➕ New Chat", use_container_width=True):
        reset_chat()

    st.markdown("### 💬 Conversations")

    for thread in list(st.session_state.chat_threads):

        col1, col2 = st.columns([4,1])

        title = st.session_state.titles.get(thread, thread)

        if col1.button(title, key=f"thread_{thread}"):

            st.session_state.thread_id = thread
            st.session_state.message_history = load_conversation(thread)

        if col2.button("🗑", key=f"delete_{thread}"):

            delete_thread(thread)
            st.rerun()


# ---------------------------
# Chat UI
# ---------------------------

st.markdown("## ✨ LangGraph AI Assistant")
st.divider()

for msg in st.session_state.message_history:

    with st.chat_message(msg["role"]):

        st.markdown(msg["content"])
        st.caption(msg.get("time",""))


# ---------------------------
# Chat Input
# ---------------------------

user_input = st.chat_input("Ask something...")

if user_input:

    timestamp = datetime.now().strftime("%H:%M")

    st.session_state.message_history.append({
        "role":"user",
        "content":user_input,
        "time":timestamp
    })

    with st.chat_message("user"):
        st.markdown(user_input)
        st.caption(timestamp)

    CONFIG = {
        "configurable":{
            "thread_id":st.session_state.thread_id
        }
    }

    if st.session_state.thread_id not in st.session_state.titles:
        st.session_state.titles[st.session_state.thread_id] = user_input[:30]

    with st.chat_message("assistant"):

        placeholder = st.empty()
        full_response = ""

        placeholder.markdown(
            "<div class='typing'>AI is typing...</div>",
            unsafe_allow_html=True
        )

        stream = chatbot.stream(
            {"messages": [HumanMessage(content=user_input)]},
            config=CONFIG,
            stream_mode="messages"
        )

        for msg, metadata in stream:

            # Skip tool/system events
            if msg.type != "ai":
                continue

            # Skip empty chunks
            if not msg.content:
                continue

            full_response += msg.content
            placeholder.markdown(full_response + "▌")

        # 🔹 Always fetch final message from LangGraph state
        state = chatbot.get_state(CONFIG)

        messages = state.values.get("messages", [])

        for m in reversed(messages):
            if m.type == "ai":
                full_response = m.content
                break

        placeholder.markdown(full_response)
        st.caption(timestamp)

    st.session_state.message_history.append({
        "role":"assistant",
        "content":full_response,
        "time":timestamp
    })
