import io
import random

import faicons
import pandas as pd
from shared import files_df, process, watch_folder
from shiny import App, Inputs, Outputs, Session, reactive, render, req, ui

app_ui = ui.page_fillable(
    ui.layout_columns(
        ui.card(
            ui.card_header(
                "Select log file",
                ui.popover(
                    faicons.icon_svg("plus"),
                    ui.input_action_button("add", "Add new logs"),
                    title="Generate new log file",
                    placement="left",
                ),
                class_="d-flex justify-content-between align-items-center",
            ),
            ui.output_data_frame("file_list"),
        ),
        ui.output_ui("log_output", fill=True, fillable=True),
        col_widths=[4, 8],
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    # When the session ends, end the folder watching process
    session.on_ended(process.kill)

    @render.data_frame
    def file_list():
        return render.DataGrid(files_df(), row_selection_mode="single")

    @render.ui
    def log_output():
        idx = input.file_list_selected_rows()
        if not idx:
            return ui.card(
                ui.card_header("Select log file"),
                "Select a log file from the list to view its contents",
            )

        return ui.card(
            ui.card_header(
                "Log output",
                ui.download_link(
                    "download", "Download", icon=faicons.icon_svg("download")
                ),
                class_="d-flex justify-content-between align-items-center",
            ),
            ui.output_data_frame("data_grid"),
        )

    @reactive.calc
    def selected_file():
        idx = req(input.file_list_selected_rows())
        file = files_df()["File Name"][idx[0]]
        return pd.read_csv(watch_folder / file)

    @render.data_frame
    def data_grid():
        return render.DataGrid(selected_file())

    @reactive.effect
    @reactive.event(input.add)
    def sim_logs():
        logs = pd.read_csv(watch_folder / files_df()["File Name"][0])
        sampled_logs = logs.sample(n=1000, replace=True)
        id = random.randint(100, 999)
        sampled_logs.to_csv(watch_folder / f"logs-{id}.csv")

    @render.download(filename="logs.csv")
    def download():
        csv = selected_file()
        with io.StringIO() as buf:
            csv.to_csv(buf)
            yield buf.getvalue().encode()


app = App(app_ui, server)
