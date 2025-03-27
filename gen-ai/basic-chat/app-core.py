# ------------------------------------------------------------------------------------
# A basic Shiny Chat example powered by Anthropic's Claude model.
# ------------------------------------------------------------------------------------
from chatlas import ChatAnthropic
from dotenv import load_dotenv
from shiny import App, ui

# Set some Shiny page options
app_ui = ui.page_fillable(
    ui.card(
        ui.card_header("Hello Anthropic Claude Chat"),
        ui.chat_ui("chat", messages=["Hello! How can I help you today?"], width="100%"),
        style="width:min(680px, 100%)",
        class_="mx-auto",
    ),
    fillable_mobile=True,
    class_="bg-light-subtle",
)


def server(input, output, session):
    # ChatAnthropic() requires an API key from Anthropic.
    # See the docs for more information on how to obtain one.
    # https://posit-dev.github.io/chatlas/reference/ChatAnthropic.html
    _ = load_dotenv()
    chat_client = ChatAnthropic(
        system_prompt="You are a helpful assistant.",
    )

    chat = ui.Chat(id="chat")

    # Generate a response when the user submits a message
    @chat.on_user_submit
    async def handle_user_input(user_input: str):
        response = await chat_client.stream_async(user_input)
        await chat.append_message_stream(response)


app = App(app_ui, server)
