from shiny import Inputs, Outputs, Session, module, reactive, render, ui
from typing import Callable

# ============================================================
# Module: Demographics
# ============================================================


@module.ui
def demo_ui(title):
    return ui.nav(
        title,
        ui.card(
            ui.input_text("name", "What is your name?"),
            ui.input_text("age", "What is your age?"),
            ui.input_radio_buttons(
                "gender",
                "What is your gender identity?",
                {"M": "Male", "F": "Female", "NB": "Non-Binary", "O": "Other"},
            ),
            ui.input_text("occupation", "What is your occupation?"),
            ui.input_text("country", "What is your country of residence?"),
        ),
    )


@module.server
def demo_server(
    input: Inputs, output: Outputs, session: Session, starting_value: int = 0
) -> Callable[[], dict]:
    @reactive.Calc
    def responses() -> dict:
        return {
            "name": input.name(),
            "age": input.age(),
            "gender": input.gender(),
            "occupation": input.occupation(),
            "country": input.country(),
        }

    return responses


# ============================================================
# Module: Contraindications
# ============================================================


@module.ui
def contra_ui(title: str):
    return ui.nav(
        title,
        ui.card(
            ui.input_text("allergies", "Do you have any allergies?"),
            ui.input_text("medications", "Are you currently taking any medication?"),
            ui.input_selectize(
                "immune_diseases",
                "Do you have any of the following diseases?",
                choices=[
                    "Rheumatoid arthritis",
                    "Psoriasis",
                    "Crohn's disease",
                    "Multiple sclerosis",
                    "Systemic lupus erythematosus",
                ],
                multiple=True,
            ),
            ui.input_select(
                "pregnant",
                "Are you pregnant or planning to become pregnant?",
                choices=["Not pregnant", "Pregnant", "Planning to become pregnant"],
            ),
            ui.input_text(
                "other_health",
                "Do you have any other health conditions we should know about?",
            ),
        ),
    )


@module.server
def contra_server(
    input: Inputs, output: Outputs, session: Session, starting_value: int = 0
) -> Callable[[], dict]:
    @reactive.Calc
    def responses() -> dict:
        return {
            "allergies": input.allergies(),
            "medications": input.medications(),
            "immune_diseases": input.immune_diseases(),
            "pregnant": input.pregnant(),
            "other_health": input.other_health(),
        }

    return responses


# ============================================================
# Module: Consent
# ============================================================


@module.ui
def consent_ui(title: str):
    return ui.nav(
        title,
        ui.card(
            ui.markdown(
                """
            ## Consent Form
            By clicking 'I Agree', you confirm that you have read and 
            understood the information provided about the clinical study, 
            and you agree to participate. You understand that your 
            participation is voluntary and you are free to withdraw at any time, 
            without giving any reason, and without affecting yourlegal rights.
            """
            ),
            ui.input_checkbox("consent", "I Agree"),
        ),
    )


@module.server
def consent_server(
    input: Inputs, output: Outputs, session: Session, starting_value: int = 0
) -> Callable:
    return input.consent
