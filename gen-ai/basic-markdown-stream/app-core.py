# ------------------------------------------------------------------------------------
# A basic Shiny MarkdownStream example powered by Anthropic.
# ------------------------------------------------------------------------------------
from chatlas import ChatAnthropic
from dotenv import load_dotenv
from shiny import App, Inputs, Outputs, Session, reactive, ui

# Define UI
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_select(
            "comic",
            "Choose a comedian",
            choices=["Jerry Seinfeld", "Ali Wong", "Mitch Hedberg"],
        ),
        ui.input_action_button("go", "Tell me a joke", class_="btn-primary"),
    ),
    ui.output_markdown_stream(
        "my_stream", content="Press the button and I'll tell you a joke."
    ),
    title="AI Joke Generator",
)


# Define server
def server(input: Inputs, output: Outputs, session: Session):
    # ChatAnthropic() requires an API key from Anthropic.
    # See the docs for more information on how to obtain one.
    # https://posit-dev.github.io/chatlas/reference/ChatAnthropic.html
    _ = load_dotenv()
    chat_client = ChatAnthropic()

    # Create a MarkdownStream
    stream = ui.MarkdownStream(id="my_stream")

    # Clicking the button triggers the streaming joke generation
    @reactive.effect
    @reactive.event(input.go)
    async def do_joke():
        prompt = f"Pretend you are {input.comic()} and tell me a funny joke."
        response = await chat_client.stream_async(prompt)
        await stream.stream(response)


# Create the Shiny app
app = App(app_ui, server)
