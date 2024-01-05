from shiny import Inputs, Outputs, Session, App, reactive, render, req, ui
from pathlib import Path
import os
import pandas as pd
import faicons
import io
import random
from datetime import datetime

app_ui = ui.page_fillable(
    ui.layout_columns(
        ui.card(
            ui.card_header(
                "Select log file",
                ui.popover(
                    ui.span(
                        faicons.icon_svg("plus"),
                        style="position:absolute; top: 5px; right: 7px;",
                    ),
                    "Generate new log file",
                    ui.input_action_button("add", "Add new logs"),
                    id="card_popover",
                    placement="left",
                ),
            ),
            ui.output_data_frame("file_list"),
        ),
        ui.output_ui("log_output", fill=True, fillable=True),
        col_widths=[4, 8],
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    log_folder = Path(__file__).parent / "watch_folder"

    def check_func(folder: Path = log_folder):
        return os.stat(folder).st_mtime

    def list_files(folder: Path) -> pd.DataFrame:
        return pd.DataFrame(
            [
                (
                    file.name,
                    datetime.fromtimestamp(file.stat().st_mtime).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                )
                for file in folder.glob("*")
            ],
            columns=["File Name", "Last Edited"],
        )

    @reactive.poll(check_func)
    def files():
        return list_files(log_folder)

    @render.data_frame
    def file_list():
        return render.DataGrid(
            files(),
            row_selection_mode="single",
        )

    @render.ui
    def log_output():
        idx = input.file_list_selected_rows()
        if not idx:
            return ui.card(ui.card_header("Select log file"))

        return ui.card(
            ui.card_header(
                "Log output",
                ui.popover(
                    ui.span(
                        faicons.icon_svg("download"),
                        style="position:absolute; top: 5px; right: 7px;",
                    ),
                    ui.download_button("download", "Download File"),
                    id="card_popover",
                ),
            ),
            ui.output_data_frame("data_grid"),
        )

    @reactive.Calc
    def selected_file():
        idx = req(input.file_list_selected_rows())
        file = files()["File Name"][idx[0]]
        return pd.read_csv(log_folder / file)

    @render.data_frame
    def data_grid():
        return render.DataGrid(selected_file(), height="95%", width="95%")

    @reactive.effect
    @reactive.event(input.add)
    def sim_logs():
        logs = pd.read_csv(log_folder / "logs.csv")
        sampled_logs = logs.sample(n=1000, replace=True)
        sampled_logs.to_csv(log_folder / f"logs-{random.randint(100, 999)}.csv")

    @session.download(filename="logs.csv")
    def download():
        csv = selected_file()
        with io.StringIO() as buf:
            csv.to_csv(buf)
            yield buf.getvalue().encode()


app = App(app_ui, server)
