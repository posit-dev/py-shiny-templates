from pathlib import Path

import pandas as pd
from shared import INPUTS
from shiny import App, Inputs, Outputs, Session, reactive, ui
from shiny_validate import InputValidator, check

app_dir = Path(__file__).parent

app_ui = ui.page_fixed(
    ui.include_css(app_dir / "styles.css"),
    ui.panel_title("Movie survey"),
    ui.card(
        ui.card_header("Demographics"),
        INPUTS["name"],
        INPUTS["country"],
        INPUTS["age"],
    ),
    ui.card(
        ui.card_header("Income"),
        INPUTS["income"],
    ),
    ui.card(
        ui.card_header("Ratings"),
        INPUTS["avengers"],
        INPUTS["spotlight"],
        INPUTS["the_big_short"],
    ),
    ui.div(
        ui.input_action_button("submit", "Submit", class_="btn btn-primary"),
        class_="d-flex justify-content-end",
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    input_validator = InputValidator()
    input_validator.add_rule("name", check.required())
    input_validator.add_rule("country", check.required())
    input_validator.add_rule("age", check.required())
    input_validator.add_rule("income", check.required())

    @reactive.effect
    @reactive.event(input.submit)
    def save_to_csv():
        input_validator.enable()
        if not input_validator.is_valid():
            return

        df = pd.DataFrame([{k: input[k]() for k in INPUTS.keys()}])

        responses = app_dir / "responses.csv"
        if not responses.exists():
            df.to_csv(responses, mode="a", header=True)
        else:
            df.to_csv(responses, mode="a", header=False)

        ui.modal_show(ui.modal("Form submitted, thank you!"))


app = App(app_ui, server)
