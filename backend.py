from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.messages import BaseMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
import sqlite3

load_dotenv()

hf_endpoint = HuggingFaceEndpoint(
    repo_id="mistralai/Mistral-7B-Instruct-v0.2",
    task="conversational",
    max_new_tokens=300,
    temperature=0.7
)

chat_llm = ChatHuggingFace(llm=hf_endpoint)

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):
    messages = state["messages"]
    response = chat_llm.invoke(messages)
    return {"messages": [response]}

conn = sqlite3.connect(database='chatbot_history.db', check_same_thread=False)

checkpoint = SqliteSaver(conn=conn)

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)

graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpoint)

def get_all_threads():
    thread_ids = set()

    for thread in checkpoint.list(None):
        config = thread.config
        if "configurable" in config:
            thread_ids.add(config["configurable"].get("thread_id"))

    return list(thread_ids)

def clear_database():
    conn.execute("DELETE FROM checkpoints")
    conn.commit()