import urllib.request
from pathlib import Path

import duckdb
from query import query_output_server, query_output_ui
from shiny import App, reactive, ui

app_dir = Path(__file__).parent
db_file = app_dir / "weather.db"


def load_csv(con, csv_name, table_name):
    csv_url = f"https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2022/2022-12-20/{csv_name}.csv"
    local_file_path = app_dir / f"{csv_name}.csv"
    urllib.request.urlretrieve(csv_url, local_file_path)
    con.sql(
        f"CREATE TABLE {table_name} AS SELECT * FROM read_csv_auto('{local_file_path}')"
    )


if not Path.exists(db_file):
    con = duckdb.connect(str(db_file), read_only=False)
    load_csv(con, "weather_forecasts", "weather")
    load_csv(con, "cities", "cities")
    con.close()

con = duckdb.connect(str(db_file), read_only=True)

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_action_button("add_query", "Add Query", class_="btn btn-primary"),
        ui.input_action_button(
            "show_meta", "Show Metadata", class_="btn btn-secondary"
        ),
        ui.markdown(
            """
            This app lets you explore a dataset using SQL and duckdb.
            The data is stored in an on-disk [duckdb](https://duckdb.org/) database,
            which leads to extremely fast queries.
            """
        ),
    ),
    ui.tags.div(
        query_output_ui("initial_query", remove_id="initial_query"),
        id="module_container",
    ),
    title="DuckDB query explorer",
    class_="bslib-page-dashboard",
)


def server(input, output, session):
    mod_counter = reactive.value(0)

    query_output_server("initial_query", con=con, remove_id="initial_query")

    @reactive.effect
    @reactive.event(input.add_query)
    def _():
        counter = mod_counter.get() + 1
        mod_counter.set(counter)
        id = "query_" + str(counter)
        ui.insert_ui(
            selector="#module_container",
            where="afterBegin",
            ui=query_output_ui(id, remove_id=id),
        )
        query_output_server(id, con=con, remove_id=id)

    @reactive.effect
    @reactive.event(input.show_meta)
    def _():
        counter = mod_counter.get() + 1
        mod_counter.set(counter)
        id = "query_" + str(counter)
        ui.insert_ui(
            selector="#module_container",
            where="afterBegin",
            ui=query_output_ui(
                id, qry="SELECT * from information_schema.columns", remove_id=id
            ),
        )
        query_output_server(id, con=con, remove_id=id)


app = App(app_ui, server)
