from langgraph.graph import StateGraph, START
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.sqlite import SqliteSaver
import time
from groq import RateLimitError

from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool

import requests
from dotenv import load_dotenv
import sqlite3
import os
from langgraph.checkpoint.sqlite import SqliteSaver

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    max_tokens=512
)

search_tool = DuckDuckGoSearchRun()


@tool
def calculator(first_num: float, second_num: float, operation: str) -> str:
    """
    Perform arithmetic operations.
    Operations supported: add, subtract, multiply, divide.
    """

    if operation == "add":
        return str(first_num + second_num)

    elif operation == "subtract":
        return str(first_num - second_num)

    elif operation == "multiply":
        return str(first_num * second_num)

    elif operation == "divide":
        if second_num == 0:
            return "Cannot divide by zero"
        return str(first_num / second_num)

    else:
        return "Invalid operation"


@tool
def get_stock_price(symbol: str) -> str:
    """
    Get the latest stock price using Alpha Vantage API.
    Example symbol: AAPL, TSLA, MSFT
    """

    api_key = st.secrets["ALPHAVANTAGE_API_KEY"]

    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
    r = requests.get(url)
    data = r.json()

    try:
        price = data["Global Quote"]["05. price"]
        return f"Current price of {symbol} is ${price}"
    except:
        return "Stock data not found"
    
tools = [calculator, get_stock_price, search_tool]
llm_with_tools = llm.bind_tools(tools)

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

SYSTEM_PROMPT = """
You are an AI assistant.

Use tools whenever information requires real-time data.

Use:
- search tool for news or current events
- calculator for math
- get_stock_price for stocks
"""

def chat_node(state: ChatState):

    messages = state["messages"]

    for attempt in range(3):
        try:
            response = llm_with_tools.invoke(messages)
            return {"messages": [response]}

        except RateLimitError:
            time.sleep(2)

    return {"messages": [{"role": "assistant", "content": "⚠️ Rate limit reached. Please try again in a few seconds."}]}

tool_node = ToolNode(tools)

conn = sqlite3.connect("chat_history.db", check_same_thread=False)

checkpointer = SqliteSaver(conn)   

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chat_node")
graph.add_conditional_edges(
    "chat_node",
    tools_condition
)
graph.add_edge("tools", "chat_node")

chatbot = graph.compile(checkpointer=checkpointer)

def retrieve_chat_history():
    threads = set()

    for checkpoint in checkpointer.list(None):
        threads.add(checkpoint.config["configurable"]["thread_id"])

    return list(threads)
