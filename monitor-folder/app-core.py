from datetime import datetime
from pathlib import Path
import io
import random
import subprocess

import pandas as pd
import faicons

from shiny import Inputs, Outputs, Session, App, reactive, render, req, ui

app_dir = Path(__file__).parent

# The directory to watch for changes
watch_folder = app_dir / "watch_folder"
# The file to update when a change is detected (DO NOT PUT THIS INSIDE `watch_folder`!)
last_change = app_dir / "last_change.txt"

# Start a background process to watch the `watch_folder` directory
# and update the `last_change` file when a change is detected
process = subprocess.Popen([
    "python", app_dir / "watch_folder.py",
    str(watch_folder), str(last_change)
])

app_ui = ui.page_fillable(
    ui.layout_columns(
        ui.card(
            ui.card_header(
                "Select log file",
                ui.popover(
                    faicons.icon_svg("plus"),
                    ui.input_action_button("add", "Add new logs"),
                    title="Generate new log file",
                    placement="left"
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
    
    # Get filenames and last edited times within the `watch_folder`
    # (when a change is detected)
    @reactive.file_reader(last_change)
    def files():
        files_info = []
        for file in watch_folder.glob("*"):
            mtime = datetime.fromtimestamp(file.stat().st_mtime)
            info = (file.name, mtime.strftime("%Y-%m-%d %H:%M:%S"))
            files_info.append(info)
            
        return pd.DataFrame(files_info, columns=["File Name", "Last Edited"])

    @render.data_frame
    def file_list():
        return render.DataGrid(files(), row_selection_mode="single")

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
                ui.download_link("download", "Download", icon=faicons.icon_svg("download")),
                class_="d-flex justify-content-between align-items-center",
            ),
            ui.output_data_frame("data_grid"),
        )

    @reactive.calc
    def selected_file():
        idx = req(input.file_list_selected_rows())
        file = files()["File Name"][idx[0]]
        return pd.read_csv(watch_folder / file)

    @render.data_frame
    def data_grid():
        return render.DataGrid(selected_file())

    @reactive.effect
    @reactive.event(input.add)
    def sim_logs():
        logs = pd.read_csv(watch_folder / files()["File Name"][0])
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
