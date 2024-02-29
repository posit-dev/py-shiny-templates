import io
import random

import faicons
import pandas as pd
from shared import files_df, process, watch_folder
from shiny import reactive, req
from shiny.express import input, render, session, ui

ui.page_opts(fillable=True)

with ui.layout_columns(col_widths=[4, 8]):
    with ui.card():
        with ui.card_header(class_="d-flex justify-content-between align-items-center"):
            "Select log file"
            with ui.popover(title="Generate new log file", placement="left"):
                faicons.icon_svg("plus")
                ui.input_action_button("add", "Add new logs")

        @render.data_frame
        def file_list():
            return render.DataGrid(files_df(), row_selection_mode="single")

    @render.express
    def log_output():
        idx = input.file_list_selected_rows()
        if not idx:
            with ui.card():
                ui.card_header("Select log file")
                "Select a log file from the list to view its contents"

        else:
            with ui.card():
                with ui.card_header(
                    class_="d-flex justify-content-between align-items-center"
                ):
                    "Log output"

                    @render.download(filename="logs.csv")
                    def download():
                        csv = selected_file()
                        with io.StringIO() as buf:
                            csv.to_csv(buf)
                            yield buf.getvalue().encode()

                @render.data_frame
                def data_grid():
                    return render.DataGrid(selected_file())


@reactive.calc
def selected_file():
    idx = req(input.file_list_selected_rows())
    file = files_df()["File Name"][idx[0]]
    return pd.read_csv(watch_folder / file)


@reactive.effect
@reactive.event(input.add)
def sim_logs():
    logs = pd.read_csv(watch_folder / files_df()["File Name"][0])
    sampled_logs = logs.sample(n=1000, replace=True)
    id = random.randint(100, 999)
    sampled_logs.to_csv(watch_folder / f"logs-{id}.csv")


# When the session ends, end the folder watching process
_ = session.on_ended(process.kill)
