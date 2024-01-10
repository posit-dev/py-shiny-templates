from shiny import Inputs, Outputs, Session, App, reactive, render, req, ui
from modules import (
    demo_ui,
    demo_server,
    contra_ui,
    contra_server,
    consent_ui,
    consent_server,
)
from pathlib import Path
import csv
import uuid


titles = ["Demographics", "Contraindications", "Consent"]
ids = [title.replace(" ", "_").lower() for title in titles]

uis = [demo_ui, contra_ui, consent_ui]
servers = [demo_server, contra_server, consent_server]

app_ui = ui.page_navbar(
    [mod(id, title) for mod, id, title in zip(uis, ids, titles)],
    sidebar=ui.sidebar(
        ui.layout_columns(
            ui.input_action_button(
                "back",
                "Back",
                width="100%",
            ),
            ui.input_action_button(
                "next", "Next", width="100%", class_="btn bg-primary"
            ),
        ),
        ui.output_ui("submit_ui"),
        open="always",
    ),
    id="tabs",
)


def server(input: Inputs, output: Outputs, session: Session):
    m = ui.modal(
        "This is an example clinical trial intake app",
        title="MOCK: Medical Operational Case Knowledge",
        easy_close=True,
        size="l",
    )
    ui.modal_show(m)

    @reactive.effect
    @reactive.event(input.next)
    def next_tab():
        if input.tabs() != "Consent":
            next_title_index = (titles.index(input.tabs()) + 1) % len(titles)
            next_title = titles[next_title_index]
            ui.update_navs("tabs", selected=next_title)

    @reactive.effect
    @reactive.event(input.back)
    def previous():
        if input.tabs() != "Demographics":
            next_title_index = (titles.index(input.tabs()) - 1) % len(titles)
            next_title = titles[next_title_index]
            ui.update_navs("tabs", selected=next_title)

    demos = demo_server(ids[0])
    contraindications = contra_server(ids[1])
    consent = consent_server(ids[2])

    @render.ui
    def submit_ui():
        if consent():
            return ui.input_action_button(
                "submit",
                "Submit",
                width="100%",
                class_="btn bg-secondary",
            )

    @reactive.effect
    @reactive.event(input.submit)
    def write_response():
        out = {"id": str(uuid.uuid4())}
        out.update(demos())
        out.update(contraindications())

        file = Path(__file__).parent / "responses.csv"
        if file.is_file():
            with open(file, "a") as f:
                writer = csv.writer(f)
                writer.writerow(list(out.values()))
        else:
            with open(file, "w") as f:
                writer = csv.writer(f)
                writer.writerow(list(out.keys()))
                writer.writerow(list(out.values()))

        m = ui.modal(
            "Thank you for applying to the study, you may close this page.",
            title="Application submitted!",
            easy_close=False,
        )
        ui.modal_show(m)


app = App(app_ui, server)
