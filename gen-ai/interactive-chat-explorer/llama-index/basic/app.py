from dotenv import load_dotenv
from llama_index.core.agent.workflow import AgentStream, FunctionAgent
from llama_index.core.workflow import Context
from llama_index.llms.openai import OpenAI
from shiny.express import ui

_ = load_dotenv()

llm = OpenAI(
    model="gpt-4.1-nano-2025-04-14",
)

ui.page_opts(
    title="Shiny Chat with LlamaIndex",
    fillable=True,
    fillable_mobile=True,
)

agent = FunctionAgent(
    tools=[],
    llm=llm,
    system_prompt="You are a pirate with a colorful personality.",
)

ctx = Context(agent)

chat = ui.Chat(
    id="chat",
)
chat.ui(
    messages=[
        {
            "role": "assistant",
            "content": "Arrr, they call me Captain Cog, the chattiest pirate on the seven seas! Ask me anything, matey!",
        },
    ],
)


async def stream_response_from_agent(user_message: str, context: Context):
    handler = agent.run(user_msg=user_message, ctx=context)

    async for event in handler.stream_events():
        if isinstance(event, AgentStream):
            if event.delta:
                yield event.delta

    await handler


@chat.on_user_submit
async def handle_user_input(user_input: str):
    async def stream_generator():
        async for chunk in stream_response_from_agent(user_input, ctx):
            yield chunk

    await chat.append_message_stream(stream_generator())
