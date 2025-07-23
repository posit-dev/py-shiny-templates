from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from faicons import icon_svg
from shiny import App, Inputs, Outputs, Session, reactive, render, ui
from shinywidgets import output_widget, render_plotly
from stocks import stocks

# Default to the last 6 months
end = pd.Timestamp.now()
start = end - pd.Timedelta(weeks=26)

app_dir = Path(__file__).parent

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_selectize("ticker", "Select Stocks", choices=stocks, selected="AAPL"),
        ui.input_date_range("dates", "Select dates", start=start, end=end),
    ),
    ui.layout_column_wrap(
        ui.value_box(
            "Current Price",
            ui.output_ui("price"),
            showcase=icon_svg("dollar-sign"),
        ),
        ui.value_box(
            "Change",
            ui.output_ui("change"),
            showcase=ui.output_ui("change_icon"),
        ),
        ui.value_box(
            "Percent Change",
            ui.output_ui("change_percent"),
            showcase=icon_svg("percent"),
        ),
        fill=False,
    ),
    ui.layout_columns(
        ui.card(
            ui.card_header("Price history"),
            output_widget("price_history"),
            full_screen=True,
        ),
        ui.card(
            ui.card_header("Latest data"),
            ui.output_data_frame("latest_data"),
        ),
        col_widths=[9, 3],
    ),
    ui.include_css(app_dir / "styles.css"),
    title="Stock explorer",
    fillable=True,
)


def server(input: Inputs, output: Outputs, session: Session):
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
        return close.iloc[-1] - close.iloc[-2]

    @reactive.calc
    def get_change_percent():
        close = get_data()["Close"]
        change = close.iloc[-1] - close.iloc[-2]
        return change / close.iloc[-2] * 100

    @render.ui
    def price():
        close = get_data()["Close"]
        return f"{close.iloc[-1]:.2f}"

    @render.ui
    def change():
        return f"${get_change():.2f}"

    @render.ui
    def change_icon():
        change = get_change()
        icon = icon_svg("arrow-up" if change >= 0 else "arrow-down")
        icon.add_class(f"text-{('success' if change >= 0 else 'danger')}")
        return icon

    @render.ui
    def change_percent():
        return f"{get_change_percent():.2f}%"

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

    @render.data_frame
    def latest_data():
        data = get_data()[:1]  # Get latest row

        data.index = data.index.astype(str)
        data = data.T

        result = pd.DataFrame(
            {
                "Category": data.index,
                "Value": data.values.flatten(),  # Flatten to 1D array
            }
        )

        # Format values
        result["Value"] = result["Value"].apply(lambda v: f"{v:.1f}")
        return result


app = App(app_ui, server)
