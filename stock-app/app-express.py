from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from faicons import icon_svg
from shiny import reactive
from shiny.express import input, render, ui
from shiny.ui import output_ui
from shinywidgets import render_plotly
from stocks import stocks

# Default to the last 6 months
end = pd.Timestamp.now()
start = end - pd.Timedelta(weeks=26)


ui.page_opts(title="Stock explorer", fillable=True)

with ui.sidebar():
    ui.input_selectize("ticker", "Select Stocks", choices=stocks, selected="AAPL")
    ui.input_date_range("dates", "Select dates", start=start, end=end)


with ui.layout_column_wrap(fill=False):
    with ui.value_box(showcase=icon_svg("dollar-sign")):
        "Current Price"

        @render.ui
        def price():
            close = get_data()["Close"]
            return f"{close.iloc[-1]:.2f}"

    with ui.value_box(showcase=output_ui("change_icon")):
        "Change"

        @render.ui
        def change():
            return f"${get_change():.2f}"

    with ui.value_box(showcase=icon_svg("percent")):
        "Percent Change"

        @render.ui
        def change_percent():
            return f"{get_change_percent():.2f}%"


with ui.layout_columns(col_widths=[9, 3]):
    with ui.card(full_screen=True):
        ui.card_header("Price history")

        @render_plotly
        def price_history():
            df = get_data().reset_index()
            fig = go.Figure(
                data=[
                    go.Candlestick(
                        x=df["Date"],
                        open=df["Open"],
                        high=df["High"],
                        low=df["Low"],
                        close=df["Close"],
                        increasing_line_color="#44bb70",
                        decreasing_line_color="#040548",
                        name=input.ticker(),
                    )
                ]
            )
            df["SMA"] = df["Close"].rolling(window=20).mean()
            fig.add_scatter(
                x=df["Date"],
                y=df["SMA"],
                mode="lines",
                name="SMA (20)",
                line={"color": "orange", "dash": "dash"},
            )
            fig.update_layout(
                hovermode="x unified",
                legend={
                    "orientation": "h",
                    "yanchor": "top",
                    "y": 1,
                    "xanchor": "right",
                    "x": 1,
                },
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            return fig

    with ui.card():
        ui.card_header("Latest data")

        @render.data_frame
        def latest_data():
            x = get_data()[:1].T.reset_index()
            x.columns = ["Category", "Value"]
            x["Value"] = x["Value"].apply(lambda v: f"{v:.1f}")
            return x


ui.include_css(Path(__file__).parent / "styles.css")


@reactive.calc
def get_ticker():
    return yf.Ticker(input.ticker())


@reactive.calc
def get_data():
    dates = input.dates()
    return get_ticker().history(start=dates[0], end=dates[1])


@reactive.calc
def get_change():
    close = get_data()["Close"]
    if len(close) < 2:
        return 0.0
    return close.iloc[-1] - close.iloc[-2]


@reactive.calc
def get_change_percent():
    close = get_data()["Close"]
    if len(close) < 2:
        return 0.0
    change = close.iloc[-1] - close.iloc[-2]
    return change / close.iloc[-2] * 100


with ui.hold():

    @render.ui
    def change_icon():
        change = get_change()
        icon = icon_svg("arrow-up" if change >= 0 else "arrow-down")
        icon.add_class(f"text-{('success' if change >= 0 else 'danger')}")
        return icon
