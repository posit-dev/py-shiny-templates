import llm
from dotenv import load_dotenv
from shiny.express import ui

# Load environment variables from .env file
_ = load_dotenv()

model = llm.get_model("gpt-4o-mini")
model.system_prompt = "You are a helpful assistant."

conversation = model.conversation()

ui.page_opts(
    title="Basic llm package Chat Example",
    fillable=True,
    fillable_mobile=True,
)

chat = ui.Chat(
    id="chat",
)
chat.ui(
    messages=[
        {
            "content": "Hello! Im your AI assistant for capital cities of the world and their countries. Ask me about the capital city of any country, and Ill provide the answer. How can I assist you today?",
            "role": "assistant",
        }
    ]
)


@chat.on_user_submit
async def handle_user_input(user_input: str):
    response = conversation.prompt(user_input, stream=True)

    async def stream_generator():
        for chunk in response:
            yield chunk

    await chat.append_message_stream(stream_generator())
