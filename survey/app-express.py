from pathlib import Path

import pandas as pd
from shared import INPUTS
from shiny import reactive
from shiny.express import input, ui
from shiny_validate import InputValidator, check

app_dir = Path(__file__).parent
ui.include_css(app_dir / "styles.css")

ui.page_opts(title="Movie survey")

with ui.card():
    ui.card_header("Demographics")
    INPUTS["name"]
    INPUTS["country"]
    INPUTS["age"]

with ui.card():
    ui.card_header("Income")
    INPUTS["income"]

with ui.card():
    ui.card_header("Ratings")
    INPUTS["avengers"]
    INPUTS["spotlight"]
    INPUTS["the_big_short"]

ui.div(
    ui.input_action_button("submit", "Submit", class_="btn btn-primary"),
    class_="d-flex justify-content-end",
)

# Unfortunate workaround to get InputValidator to work in Express
input_validator = None


@reactive.effect
def _():
    # Add validation rules for each input that requires validation
    global input_validator
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
