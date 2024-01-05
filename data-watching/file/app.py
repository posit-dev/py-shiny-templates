from shiny import Inputs, Outputs, Session, App, render, ui, reactive
from pathlib import Path
import pandas as pd
from faicons import icon_svg

log_path = Path(__file__).parent / "logs.csv"


@reactive.file_reader(log_path)
def logs():
    return pd.read_csv(log_path)


app_ui = ui.page_fillable(
    ui.row(
        ui.layout_columns(
            ui.value_box(
                "Current Message",
                ui.output_text("cur_message"),
                theme="bg-gradient-indigo-purple",
                showcase=icon_svg("comment-dots", width="50px"),
            ),
            ui.value_box(
                "Current Status",
                ui.output_text("cur_status"),
                theme="bg-gradient-indigo-purple",
                showcase=icon_svg("check", width="50px"),
            ),
            ui.value_box(
                "Last update",
                ui.output_text("last_update"),
                theme="bg-gradient-indigo-purple",
                showcase=icon_svg("clock", width="50px"),
            ),
            ui.value_box(
                "Number of Messages",
                ui.output_text("n_messages"),
                theme="bg-gradient-indigo-purple",
                showcase=icon_svg("envelope", width="50px"),
            ),
            col_widths=[6, 2, 2, 2],
        ),
    ),
    ui.row(
        ui.layout_columns(
            ui.card(
                ui.card_header("Logs"),
                ui.output_data_frame("df"),
                max_height="100%",
            ),
            ui.card(
                ui.card_header("Log Summary"),
                ui.output_data_frame("message_counts"),
            ),
            col_widths=[8, 4],
        )
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    @render.data_frame
    def df():
        out = logs().sort_values("date", ascending=False)
        return render.DataTable(out, width="100%", height="100%")

    @reactive.calc
    def current():
        return logs().iloc[-1]

    @render.text
    def last_update():
        dates = pd.to_datetime(current()["date"])
        return dates.strftime("%H:%M:%S")

    @render.text
    def n_messages():
        return len(logs())

    @render.text
    def cur_status():
        return current()["status"]

    @render.text
    def cur_message():
        return current()["message"]

    @render.data_frame
    def message_counts():
        message_counts = logs()["message"].value_counts().reset_index()
        message_counts.columns = ["message", "count"]
        return render.DataTable(message_counts, summary=False, width="100%")


app = App(app_ui, server)
