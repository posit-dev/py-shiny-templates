from shiny import Inputs, Outputs, Session, App, reactive, render, req, ui
from stocks import stocks
from shinywidgets import render_widget, output_widget

import pandas as pd
import plotly.express as px
from helpers import get_stock_data
from faicons import icon_svg

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_selectize(
            "tickers", "Select Stocks", choices=stocks, selected="AAPL", multiple=True
        ),
        ui.input_date_range(
            "dates", "Select dates", start="2023-01-01", end="2023-12-31"
        ),
        width="300px",
    ),
    ui.card(
        ui.card_header(
            "Historical price (Click gear for plot options)",
            ui.popover(
                ui.span(
                    icon_svg("gear"),
                    style="position:absolute; top: 5px; right: 7px;",
                ),
                ui.h3("Modify plot"),
                ui.input_select(
                    "metric",
                    "Select Metric",
                    choices=["Price", "Volume"],
                    selected="Price",
                ),
                ui.input_checkbox("log_scale", "Log Scale"),
                placement="right",
                id="card_popover",
            ),
        ),
        output_widget("price_comp"),
    ),
    title="Stock price app",
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.calc
    def prices():
        res = [
            get_stock_data(req(stock), input.dates()[0], input.dates()[1])
            for stock in input.tickers()
        ]
        return pd.concat(res)

    @render_widget
    def price_comp():
        fig = px.line(prices(), x="Date", y=input.metric(), color="Ticker")
        fig.update_layout(
            yaxis_title="Price in Dollars",
            yaxis=dict(
                tickprefix="$",
                showgrid=True,
                showline=True,
                showticklabels=True,
            ),
            template="plotly_white",  # Apply the 'plotly_dark' theme
        )

        if input.log_scale():
            fig = fig.update_yaxes(type="log")

        return fig


app = App(app_ui, server)
