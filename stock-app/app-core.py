from shiny import Inputs, Outputs, Session, App, reactive, render, req, ui
from stocks import stocks
from shinywidgets import render_widget, output_widget

import pandas as pd
import plotly.express as px
import yfinance as yf
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
    ui.layout_columns(
        ui.output_ui("price_boxes", fill=True, fillable=True).add_class("gap-2"),
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
        col_widths=[3, 9],
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

    @render.ui
    def price_boxes():
        latest_prices = (
            prices().groupby("Ticker").last().reset_index()[["Ticker", "Price"]]
        )
        # Format price as a dollar value
        latest_prices["Price"] = latest_prices["Price"].map("${:,.2f}".format)
        # Assuming 'df' is your DataFrame
        list_of_tuples = [tuple(row) for row in latest_prices.itertuples(index=False)]
        return [
            ui.value_box(title=ticker, value=price, theme="gradient-orange-indigo")
            for ticker, price in list_of_tuples
        ]


def get_stock_data(ticker: str, start: str, end: str):
    data = yf.download(ticker, start, end)
    data["Ticker"] = ticker
    data.reset_index(inplace=True)
    data.rename(columns={"High": "Price"}, inplace=True)
    return data


app = App(app_ui, server)
