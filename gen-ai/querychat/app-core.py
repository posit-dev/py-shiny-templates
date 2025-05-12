import querychat
from chatlas import ChatAnthropic
from seaborn import load_dataset
from shiny import App, render, ui

titanic = load_dataset("titanic")


def create_chat_callback(system_prompt):
    return ChatAnthropic(system_prompt=system_prompt)


# Configure querychat
querychat_config = querychat.init(
    titanic,
    "titanic",
    create_chat_callback=create_chat_callback,
)

# Create UI
app_ui = ui.page_sidebar(
    # 2. Place the chat component in the sidebar
    querychat.sidebar("chat", width=600),
    # Main panel with data viewer
    ui.card(
        ui.card_header("Titanic dataset"),
        ui.output_data_frame("data_table"),
    ),
    title="querychat with Python",
    fillable=True,
)


# Define server logic
def server(input, output, session):
    # 3. Initialize querychat server with the config from step 1
    chat = querychat.server("chat", querychat_config)

    # 4. Display the filtered dataframe
    @render.data_frame
    def data_table():
        # Access filtered data via chat.df() reactive
        return chat["df"]()


# Create Shiny app
app = App(app_ui, server)
