# ------------------------------------------------------------------------------------
# A basic Shiny Chat example powered by Anthropic's Claude model.
# ------------------------------------------------------------------------------------
from chatlas import ChatAnthropic
from dotenv import load_dotenv
from shiny.express import ui

# ChatAnthropic() requires an API key from Anthropic.
# See the docs for more information on how to obtain one.
# https://posit-dev.github.io/chatlas/reference/ChatAnthropic.html
_ = load_dotenv()
chat_client = ChatAnthropic(
    system_prompt="You are a helpful assistant.",
)

# Set some Shiny page options
ui.page_opts(
    fillable=True,
    fillable_mobile=True,
    class_="bg-light-subtle",
)

# Initialize Shiny chat component
chat = ui.Chat(id="chat")

# Display the chat in a card, with welcome message
with ui.card(style="width:min(680px, 100%)", class_="mx-auto"):
    ui.card_header("Hello Anthropic Claude Chat")
    chat.ui(
        messages=["Hello! How can I help you today?"],
        width="100%",
    )


# Generate a response when the user submits a message
@chat.on_user_submit
async def handle_user_input(user_input: str):
    response = await chat_client.stream_async(user_input)
    await chat.append_message_stream(response)
