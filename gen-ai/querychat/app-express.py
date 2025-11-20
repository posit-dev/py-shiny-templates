from querychat.express import QueryChat
from seaborn import load_dataset
from shiny.express import render, ui

titanic = load_dataset("titanic")

qc = QueryChat(
    titanic,
    "titanic",
    client="anthropic/claude-sonnet-4-5",
)
qc.sidebar()

with ui.card(fill=True):
    with ui.card_header():

        @render.text
        def title():
            return qc.title() or "Titanic Dataset"

    @render.data_frame
    def data_table():
        return qc.df()
