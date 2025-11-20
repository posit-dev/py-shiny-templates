from querychat import QueryChat
from seaborn import load_dataset
from shiny import App, render, ui

titanic = load_dataset("titanic")

qc = QueryChat(
    titanic,
    "titanic",
    client="anthropic/claude-sonnet-4-5",
)

app_ui = ui.page_fluid(
    qc.sidebar(),
    ui.output_data_frame("data_table"),
)


def server(input, output, session):
    qc.server()

    @render.data_frame
    def data_table():
        return qc.df()


app = App(app_ui, server)
