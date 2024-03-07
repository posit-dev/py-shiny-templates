import pandas as pd
from faicons import icon_svg

# Import the reactive file reader (logs) and the process the external
# process that generates the logs
from shared import logs_df, process
from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fillable(
    ui.layout_columns(
        ui.value_box(
            "Current Message",
            ui.output_text("cur_message"),
            showcase=icon_svg("comment-dots"),
        ),
        ui.value_box(
            "Current Status",
            ui.output_text("cur_status"),
            showcase=icon_svg("check"),
        ),
        ui.value_box(
            "Last update",
            ui.output_text("last_update"),
            showcase=icon_svg("clock"),
        ),
        ui.value_box(
            "Number of Messages",
            ui.output_text("n_messages"),
            showcase=icon_svg("envelope"),
        ),
        col_widths=[6, 2, 2, 2],
        fill=False,
    ),
    ui.layout_columns(
        ui.card(
            ui.card_header("Logs"),
            ui.output_data_frame("df"),
        ),
        ui.card(
            ui.card_header("Log Summary"),
            ui.output_data_frame("message_counts"),
        ),
        col_widths=[8, 4],
    ),
    class_="bslib-page-dashboard"
)


def server(input: Inputs, output: Outputs, session: Session):
    @render.data_frame
    def df():
        return logs_df().sort_values("date", ascending=False)

    @reactive.calc
    def current():
        return logs_df().iloc[-1]

    @render.text
    def last_update():
        dates = pd.to_datetime(current()["date"])
        return dates.strftime("%H:%M:%S")

    @render.text
    def n_messages():
        return len(logs_df())

    @render.text
    def cur_status():
        return current()["status"]

    @render.text
    def cur_message():
        return current()["message"]

    @render.data_frame
    def message_counts():
        counts = logs_df()["message"].value_counts().reset_index()
        counts.columns = ["message", "count"]
        counts = counts.sort_values("count", ascending=False)
        return render.DataGrid(counts, filters=True)

    session.on_ended(process.kill)


app = App(app_ui, server)
