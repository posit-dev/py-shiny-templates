import llm
from dotenv import load_dotenv
from shiny.express import ui

# Load environment variables from .env file
_ = load_dotenv()


def get_current_time() -> str:
    """Returns the current date and time as a string."""
    from datetime import datetime

    return str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


model = llm.get_model("gpt-4o-mini")
model.system_prompt = "You are a helpful assistant."


ui.page_opts(
    title="Tool Calling Example using llm package",
    fillable=True,
    fillable_mobile=True,
)

chat = ui.Chat(
    id="chat",
)
chat.ui(
    messages=[
        {
            "content": "Hello! I'm a chatbot that can help you with the current time. How can I assist you today?",
            "role": "assistant",
        }
    ],
)


@chat.on_user_submit
async def handle_user_input(user_input: str):
    response = model.chain(user_input, tools=[get_current_time])

    # Stream the response to the chat window
    await chat.append_message_stream(response)
