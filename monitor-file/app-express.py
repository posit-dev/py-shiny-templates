import pandas as pd
from faicons import icon_svg

# Import the reactive file reader (logs) and the process the external
# process that generates the logs
from shared import logs_df, process
from shiny import reactive
from shiny.express import render, session, ui

ui.page_opts(fillable=True)

{"class": "bslib-page-dashboard"}

with ui.layout_columns(col_widths=[6, 2, 2, 2], fill=False):
    with ui.value_box(showcase=icon_svg("comment-dots")):
        "Current Message"

        @render.text
        def cur_message():
            return current()["message"]

    with ui.value_box(showcase=icon_svg("check")):
        "Current Status"

        @render.text
        def cur_status():
            return current()["status"]

    with ui.value_box(showcase=icon_svg("clock")):
        "Last update"

        @render.text
        def last_update():
            dates = pd.to_datetime(current()["date"])
            return dates.strftime("%H:%M:%S")

    with ui.value_box(showcase=icon_svg("envelope")):
        "Number of Messages"

        @render.text
        def n_messages():
            return len(logs_df())


with ui.layout_columns(col_widths=[8, 4]):
    with ui.card():
        ui.card_header("Logs")

        @render.data_frame
        def df():
            return logs_df().sort_values("date", ascending=False)

    with ui.card():
        ui.card_header("Log Summary")

        @render.data_frame
        def message_counts():
            counts = logs_df()["message"].value_counts().reset_index()
            counts.columns = ["message", "count"]
            counts = counts.sort_values("count", ascending=False)
            return render.DataGrid(counts, filters=True)


@reactive.calc
def current():
    return logs_df().iloc[-1]


_ = session.on_ended(process.kill)
