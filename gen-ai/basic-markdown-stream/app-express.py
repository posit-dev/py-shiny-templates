# ------------------------------------------------------------------------------------
# A basic Shiny MarkdownStream example powered by Anthropic.
# ------------------------------------------------------------------------------------
from dotenv import load_dotenv
from chatlas import ChatAnthropic

from shiny import App, reactive, ui
from shiny.types import ImgData

# Define the UI
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_select(
            "comic",
            "Choose a comedian",
            choices=["Jerry Seinfeld", "Ali Wong", "Mitch Hedberg"],
        ),
        ui.input_action_button("go", "Tell me a joke", class_="btn-primary"),
    ),
    ui.chat_ui("my_stream"),
    title="Comedian Joke Generator",
)


# Define the server logic
def server(input, output, session):
    # ChatAnthropic() requires an API key from Anthropic.
    # See the docs for more information on how to obtain one.
    # https://posit-dev.github.io/chatlas/reference/ChatAnthropic.html
    _ = load_dotenv()
    chat_client = ChatAnthropic()

    # Initialize the MarkdownStream with default content
    ui.update_chat(
        "my_stream",
        content="Press the button and I'll tell you a joke.",
    )

    # Clicking the button triggers the streaming joke generation
    @reactive.effect
    @reactive.event(input.go)
    async def do_joke():
        prompt = f"Pretend you are {input.comic()} and tell me a funny joke."
        response = await chat_client.stream_async(prompt)
        await ui.update_chat.stream("my_stream", response)


# Create the Shiny app
app = App(app_ui, server)
