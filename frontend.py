import streamlit as st
from backend import chatbot, get_all_threads
from langchain_core.messages import HumanMessage
import uuid
from datetime import datetime

st.set_page_config(
    page_title="LangGraph AI",
    page_icon="🤖",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    color: white;
}

section[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(12px);
}

.typing {
    font-size: 14px;
    opacity: 0.7;
    animation: blink 1s infinite;
}

@keyframes blink {
  50% { opacity: 0.2; }
}

code {
    background-color: #111827 !important;
    color: #38bdf8 !important;
    padding: 4px 6px !important;
    border-radius: 5px !important;
}

pre {
    background-color: #111827 !important;
    padding: 12px !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

def generate_thread_id():
    return str(uuid.uuid4())[:8]

def add_thread(thread_id):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)

def reset_chat():
    new_thread = generate_thread_id()
    st.session_state["thread_id"] = new_thread
    add_thread(new_thread)
    st.session_state["message_history"] = []
    st.session_state["titles"][new_thread] = "New Chat"

def delete_thread(thread_id):
    if thread_id in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].remove(thread_id)

    if thread_id in st.session_state["titles"]:
        del st.session_state["titles"][thread_id]

def load_conversation(thread_id):
    state = chatbot.get_state(
        config={"configurable": {"thread_id": thread_id}}
    )

    if state and "messages" in state.values:
        return state.values["messages"]

    return []

if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = get_all_threads()

if "titles" not in st.session_state:
    st.session_state["titles"] = {}

add_thread(st.session_state["thread_id"])

with st.sidebar:
    st.markdown("## 🤖 LangGraph AI")
    st.caption("Persistent Multi-Thread Chat")

    if st.button("➕ New Chat", use_container_width=True):
        reset_chat()

    st.markdown("### 💬 Conversations")

    for thread in list(st.session_state["chat_threads"]):

        col1, col2 = st.columns([4,1])
        title = st.session_state["titles"].get(thread, thread)

        if col1.button(title, key=f"btn_{thread}"):
            st.session_state["thread_id"] = thread

            messages = load_conversation(thread)

            formatted = []
            for message in messages:
                role = "user" if message.type == "human" else "assistant"

                formatted.append({
                    "role": role,
                    "content": message.content,
                    "time": datetime.now().strftime("%H:%M")
                })

            st.session_state["message_history"] = formatted

        if col2.button("🗑", key=f"del_{thread}"):
            delete_thread(thread)
            st.rerun()

st.markdown("## ✨ LangGraph AI Assistant")
st.divider()

for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        st.caption(message.get("time", ""))

user_input = st.chat_input("Type your message...")

if user_input:

    timestamp = datetime.now().strftime("%H:%M")

    st.session_state["message_history"].append({
        "role": "user",
        "content": user_input,
        "time": timestamp
    })

    with st.chat_message("user"):
        st.markdown(user_input)
        st.caption(timestamp)

    CONFIG = {
        "configurable": {
            "thread_id": st.session_state["thread_id"]
        }
    }

    if st.session_state["thread_id"] not in st.session_state["titles"]:
        st.session_state["titles"][st.session_state["thread_id"]] = user_input[:25]

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        placeholder.markdown("<div class='typing'>AI is typing...</div>", unsafe_allow_html=True)

        stream = chatbot.stream(
            {"messages": [HumanMessage(content=user_input)]},
            config=CONFIG,
            stream_mode="messages",
        )

        for message_chunk, metadata in stream:
            if message_chunk.content:
                full_response += message_chunk.content
                placeholder.markdown(full_response + "▌")

        placeholder.markdown(full_response)
        st.caption(timestamp)

    st.session_state["message_history"].append({
        "role": "assistant",
        "content": full_response,
        "time": timestamp
    })