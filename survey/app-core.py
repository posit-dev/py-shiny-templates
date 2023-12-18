from shiny import Inputs, Outputs, Session, App, reactive, render, ui
from htmltools import Tag
import pandas as pd
from pathlib import Path
from typing import Dict

output_path = Path(__file__).parent / "output.csv"


def make_likart(id: str, movie: str) -> Tag:
    return ui.input_slider(
        id,
        f"On a scale of 1-5 how would you rate: '{movie}'?",
        1,
        5,
        value=None,
        ticks=True,
        step=1,
    )


def make_section(section: str, question_dict: Dict):
    out = ui.accordion_panel(
        section,
        question_dict[section]["elements"],
    )
    return out


movies = ["The Avengers", "Spotlight", "The Big Short", "The Phantom Thread"]
ids = [movie.lower().replace(" ", "_") for movie in movies]

questions = {
    "Demographics": {
        "ids": ["name", "country", "age"],
        "elements": [
            ui.tooltip(
                ui.input_text("name", "Enter your name"),
                "Enter your name",
                value=None,
            ),
            ui.tooltip(
                ui.input_select(
                    "country",
                    "Country",
                    choices=["USA", "Canada", "Portugal"],
                    selectize=True,
                    selected=None,
                ),
                "Your primary residence",
            ),
            ui.input_numeric("age", "Age", value=None),
        ],
    },
    "Income": {
        "ids": ["income"],
        "elements": [ui.input_numeric("income", "Annual income", value=None)],
    },
    "Ratings": {
        "ids": ids,
        "elements": [make_likart(id, movie) for id, movie in zip(ids, movies)],
    },
}


app_ui = ui.page_fluid(
    ui.panel_title("Movie survey"),
    ui.card(
        ui.accordion(
            *[make_section(key, questions) for key in questions.keys()],
        ),
    ),
    ui.card(ui.output_ui("submit_card")),
)


def server(input: Inputs, output: Outputs, session: Session):
    all_ids = [
        id
        for sublist in [questions[category]["ids"] for category in questions]
        for id in sublist
    ]

    @render.ui
    @reactive.event(*[input[id] for id in all_ids])
    def submit_card():
        def none_or_empty(x) -> bool:
            return x == "" or x is None

        incomplete = [none_or_empty(input[id]()) for id in all_ids]

        if any(incomplete):
            incomplete_ids = [id for id in all_ids if none_or_empty(input[id]())]
            return ui.h4(
                f" Mandatory fields still incomplete: {', '.join(incomplete_ids)}"
            )

        return ui.input_action_button(
            "submit",
            "Submit",
            _class="btn btn-success",
        )

    @reactive.Effect
    @reactive.event(input.submit)
    def save_to_csv():
        to_save = {id: input[id]() for id in all_ids}
        df = pd.DataFrame([to_save])
        if not output_path.exists():
            df.to_csv(output_path, mode="a", header=True)
        else:
            df.to_csv(output_path, mode="a", header=False)
        ui.modal_show(ui.modal("Form submitted!"))


app = App(app_ui, server)
