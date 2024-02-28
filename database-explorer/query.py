import duckdb
from shiny import module, reactive, render, ui


@module.ui
def query_output_ui(remove_id, qry="SELECT * from weather LIMIT 10"):
    return (
        ui.card(
            {"id": remove_id},
            ui.card_header(f"{remove_id}"),
            ui.layout_columns(
                [
                    ui.input_text_area(
                        "sql_query",
                        "",
                        value=qry,
                        width="100%",
                        height="200px",
                    ),
                    ui.layout_columns(
                        ui.input_action_button("run", "Run", class_="btn btn-primary"),
                        ui.input_action_button(
                            "rmv", "Remove", class_="btn btn-warning"
                        ),
                    ),
                ],
                ui.output_data_frame("results"),
                col_widths={"xl": [3, 9], "lg": [4, 8], "md": [6, 6], "sm": [12, 12]},
            ),
        ),
    )


@module.server
def query_output_server(
    input, output, session, con: duckdb.DuckDBPyConnection, remove_id
):
    @render.data_frame
    @reactive.event(input.run)
    def results():
        qry = input.sql_query().replace("\n", " ")
        return con.query(qry).to_df()

    @reactive.effect
    @reactive.event(input.rmv)
    def _():
        ui.remove_ui(selector=f"div#{remove_id}")
