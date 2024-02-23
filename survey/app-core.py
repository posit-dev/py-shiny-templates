import pandas as pd
from pathlib import Path
from shiny import Inputs, Outputs, Session, App, reactive, ui
from shiny_validate import InputValidator, check


app_dir = Path(__file__).parent

app_ui = ui.page_fixed(
    ui.include_css(app_dir / "styles.css"),
    ui.panel_title("Movie survey"),
    ui.card(
        ui.card_header("Demographics"),
        ui.input_text("name", "Enter your name"),
        ui.input_select(
            "country", "Country",
            choices=["", "USA", "Canada", "Portugal"],
        ),
        ui.input_numeric("age", "Age", None, min=0, max=120, step=1),
    ),
    ui.card(
        ui.card_header("Income"),
        ui.input_numeric("income", "Annual income", None, step=1000),
    ),
    ui.card(
        ui.card_header("Ratings"),
        # TODO: Can we get rid of the no response option??
        ui.input_radio_buttons(
            "avengers",
            "How would you rate: 'Avengers'?",
            choices=["No response", 1, 2, 3, 4, 5],
            inline=True,
        ),
        ui.input_radio_buttons(
            "spotlight",
            "How would you rate: 'Spotlight'?",
            choices=["No response", 1, 2, 3, 4, 5],
            inline=True,
        ),
        ui.input_radio_buttons(
            "the_big_short",
            "How would you rate: 'The Big Short'?",
            choices=["No response", 1, 2, 3, 4, 5],
            inline=True,
        ),
    ),
    ui.input_action_button("submit", "Submit", class_="btn btn-primary")
)


def server(input: Inputs, output: Outputs, session: Session):
    
    iv = InputValidator()

    iv.add_rule("name", check.required())
    iv.add_rule("country", check.required())
    iv.add_rule("age", check.required())
    iv.add_rule("income", check.required())

    @reactive.effect
    @reactive.event(input.submit)
    def save_to_csv():
        iv.enable()
        if not iv.is_valid():
            return

        all_ids = ["name", "country", "age", "income", "avengers", "spotlight", "the_big_short"]
        df = pd.DataFrame([{k: input[k]() for k in all_ids}])

        responses = app_dir / "responses.csv"
        if not responses.exists():
            df.to_csv(responses, mode="a", header=True)
        else:
            df.to_csv(responses, mode="a", header=False)

        ui.modal_show(
            ui.modal("Form submitted, thank you!")
        )


app = App(app_ui, server)
