from pathlib import Path

from chatlas import ChatAnthropic
from dotenv import load_dotenv
from faicons import icon_svg
from shiny import reactive
from shiny.express import input, ui

# Create a ChatAnthropic client with a system prompt
app_dir = Path(__file__).parent
with open(app_dir / "prompt.md") as f:
    system_prompt = f.read()

_ = load_dotenv()
chat_client = ChatAnthropic(
    system_prompt=system_prompt,
)

# Set some page level Shiny options
ui.page_opts(
    title="Choose your own data science adventure",
    fillable=True,
    fillable_mobile=True,
)

# Create a sidebar with inputs that control the "starting" user prompt
with ui.sidebar(id="sidebar"):
    ui.input_selectize(
        "company_role",
        "You are a...",
        choices=[
            "Machine Learning Engineer",
            "Data Analyst",
            "Research Scientist",
            "MLOps Engineer",
            "Data Science Generalist",
        ],
        selected="Data Analyst",
    )

    ui.input_selectize(
        "company_size",
        "who works for...",
        choices=[
            "yourself",
            "a startup",
            "a university",
            "a small business",
            "a medium-sized business",
            "a large business",
            "an enterprise corporation",
        ],
        selected="a medium-sized business",
    )

    ui.input_selectize(
        "company_industry",
        "in the ... industry",
        choices=[
            "Healthcare and Pharmaceuticals",
            "Banking, Financial Services, and Insurance",
            "Technology and Software",
            "Retail and E-commerce",
            "Media and Entertainment",
            "Telecommunications",
            "Automotive and Manufacturing",
            "Energy and Oil & Gas",
            "Agriculture and Food Production",
            "Cybersecurity and Defense",
        ],
        selected="Healthcare and Pharmaceuticals",
    )

    ui.input_action_button(
        "go",
        "Start adventure",
        icon=icon_svg("play"),
        class_="btn btn-primary",
    )


# Create and display chat
welcome = """
Welcome to a choose-your-own learning adventure in data science!
Please pick your role, the size of the company you work for, and the industry you're in.
Then click the "Start adventure" button to begin.
"""
chat = ui.Chat(id="chat")
chat.ui(messages=[welcome])


# The 'starting' user prompt is a function of the inputs
@reactive.calc
def starting_prompt():
    return (
        f"I want a story that features a {input.company_role()} "
        f"who works for {input.company_size()} in the {input.company_industry()} industry."
    )


# Has the adventure started?
has_started: reactive.value[bool] = reactive.value(False)


# When the user clicks the 'go' button, start/restart the adventure
@reactive.effect
@reactive.event(input.go)
async def _():
    if has_started():
        await chat.clear_messages()
        await chat.append_message(welcome)
    chat.update_user_input(value=starting_prompt(), submit=True)
    chat.update_user_input(value="", focus=True)
    has_started.set(True)


@reactive.effect
async def _():
    if has_started():
        ui.update_action_button(
            "go", label="Restart adventure", icon=icon_svg("repeat")
        )
        ui.update_sidebar("sidebar", show=False)
    else:
        chat.update_user_input(value=starting_prompt())


@chat.on_user_submit
async def _(user_input: str):
    n_msgs = len(chat.messages())
    if n_msgs == 1:
        user_input += (
            " Please jump right into the story without any greetings or introductions."
        )
    elif n_msgs == 4:
        user_input += ". Time to nudge this story toward its conclusion. Give one more scenario (like creating a report, dashboard, or presentation) that will let me wrap this up successfully."
    elif n_msgs == 5:
        user_input += ". Time to wrap this up. Conclude the story in the next step and offer to summarize the chat or create example scripts in R or Python. Consult your instructions for the correct format. If the user asks for code, remember that you'll need to create simulated data that matches the story."

    response = chat_client.stream(user_input)
    await chat.append_message_stream(response)
