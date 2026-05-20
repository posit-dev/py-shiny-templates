import os
from datetime import datetime

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from shiny.express import ui

_ = load_dotenv()


@tool
def get_current_time() -> str:
    """Get the current time in HH:MM:SS format."""
    return datetime.now().strftime("%H:%M:%S")


@tool
def get_current_date() -> str:
    """Get the current date in YYYY-MM-DD format."""
    return datetime.now().strftime("%Y-%m-%d")


@tool
def get_current_weather(city: str) -> str:
    """Get the current weather for a given city."""
    return f"The current weather in {city} is sunny with a temperature of 25°C."


@tool
def calculator(expression: str) -> str:
    """Evaluate mathematical expressions"""
    return str(eval(expression))


tools = [get_current_time, get_current_date, calculator, get_current_weather]

llm = ChatOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    model="gpt-4.1-nano-2025-04-14",
)

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="You are a helpful assistant",
    checkpointer=InMemorySaver(),
)

ui.page_opts(
    title="Shiny Chat with LangChain Agent",
    fillable=True,
    fillable_mobile=True,
)

chat = ui.Chat(
    id="chat",
)
chat.ui(
    messages=[
        {
            "content": (
                "Hello! I'm a chatbot with tools. I can get the time, date, "
                "weather, or do calculations. I'll also remember our "
                "conversation. How can I help?"
            ),
            "role": "assistant",
        }
    ],
)


@chat.on_user_submit
async def handle_user_input(user_input: str):
    """
    Handles user input by streaming the agent's response.
    """
    config: RunnableConfig = {"configurable": {"thread_id": "shiny_session_tools_1"}}

    async def stream_response():
        async for chunk, metadata in agent.astream(
            {"messages": [{"role": "user", "content": user_input}]},
            config=config,
            stream_mode="messages",
        ):
            if not isinstance(metadata, dict):
                continue
            if metadata.get("langgraph_node") != "model":
                continue
            content = getattr(chunk, "content", None)
            if content:
                yield content

    await chat.append_message_stream(stream_response())
