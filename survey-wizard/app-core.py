from pathlib import Path

from shiny import App, reactive, render, ui
from shiny_validate import InputValidator, check

# Define the wizard steps
# "title" is the title of the step
# "contents" is any collection of Shiny UI/inputs
# "input_checks" is a list of tuples (each tuple defines a rule for the InputValidator.add_rule() )
STEPS = [
    {
        "title": "Personal Information",
        "contents": [
            ui.input_text("name", "Name"),
            ui.input_text("email", "Email (Optional)"),
        ],
        "input_checks": [("name", check.required())],
    },
    {
        "title": "Demographics",
        "contents": [
            ui.input_numeric("age", "Age", None),
            ui.input_numeric("income", "Income (Optional)", None, step=1000),
        ],
        "input_checks": [("age", check.required())],
    },
]

app_ui = ui.page_fixed(
    ui.include_css(Path(__file__).parent / "styles.css"),
    ui.panel_title("Wizard Demo"),
    # A card which holds wizard steps in a hidden navset (so that panels can be
    # controlled via action buttons)
    ui.card(
        ui.card_header(ui.output_text("title")),
        ui.navset_hidden(
            *[
                ui.nav_panel(step["title"], *step["contents"], value=str(i))
                for i, step in enumerate(STEPS)
            ],
            id="tabs",
        ),
    ),
    # Action buttons provide navigation between steps
    # (conditional panels are used to show/hide the buttons when appropriate)
    ui.div(
        ui.panel_conditional(
            "input.tabs !== '0'", ui.input_action_button("prev", "Previous")
        ),
        ui.panel_conditional(
            f"input.tabs !== '{len(STEPS)-1}'",
            ui.input_action_button("next", "Next", class_="btn btn-primary"),
        ),
        ui.panel_conditional(
            f"input.tabs === '{len(STEPS)-1}'",
            ui.input_action_button("submit", "Submit", class_="btn btn-primary"),
        ),
        class_="d-flex justify-content-end gap-3",
    ),
)


def server(input, output, session):
    # Update card title to reflect the current step
    @render.text
    def title():
        return STEPS[int(input.tabs())]["title"]

    # Create an input validator for each step
    validators: list[InputValidator] = []
    for step in STEPS:
        v = InputValidator()
        for chk in step["input_checks"]:
            v.add_rule(chk[0], chk[1])
        validators.append(v)

    # When next is pressed, first validate the current step,
    # then move to the next step
    @reactive.effect
    @reactive.event(input.next)
    def _():
        tab = int(input.tabs())
        v = validators[tab]
        v.enable()
        if not v.is_valid():
            return
        ui.update_navs("tabs", selected=str(tab + 1))

    # When prev is pressed, move to the previous step
    @reactive.effect
    @reactive.event(input.prev)
    def _():
        tab = int(input.tabs())
        ui.update_navs("tabs", selected=str(tab - 1))

    # See the survey template to learn how to record the form data
    @reactive.effect
    @reactive.event(input.submit)
    def _():
        ui.modal_show(ui.modal("Form submitted, thank you!"))


app = App(app_ui, server)
