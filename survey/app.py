from shiny import Inputs, Outputs, Session, App, reactive, render, ui
from htmltools import Tag
import pandas as pd
from pathlib import Path
from typing import Dict, List

output_path = Path(__file__).parent / "output.csv"


def make_likart(id: str, movie: str) -> Tag:
    return ui.input_slider(
        id,
        f"On a scale of 1-5 how would you rate: '{movie}'?",
        1,
        5,
        3,
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
        "ids": ["name", "country"],
        "elements": [
            ui.tooltip(ui.input_text("name", "Enter your name"), "Enter your name"),
            ui.tooltip(
                ui.input_select(
                    "country",
                    "Country",
                    choices=["USA", "Canada", "Portugal"],
                ),
                "Your primary residence",
            ),
            ui.input_numeric("age", "Age", value=0),
        ],
    },
    "Income": {
        "ids": ["income"],
        "elements": [ui.input_slider("income", "Annual income", 0, 400000, 70000)],
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
    ui.card(
        ui.input_action_button("save_button", "Submit"),
    ),
)


def server(input: Inputs, output, session):
    @reactive.Effect
    @reactive.event(input.save_button)
    def save_to_csv():
        all_ids = [
            id
            for sublist in [questions[category]["ids"] for category in questions]
            for id in sublist
        ]
        to_save = {id: input[id]() for id in all_ids}
        df = pd.DataFrame([to_save])
        if not output_path.exists():
            df.to_csv(output_path, mode="a", header=True)
        else:
            df.to_csv(output_path, mode="a", header=False)


app = App(app_ui, server)
