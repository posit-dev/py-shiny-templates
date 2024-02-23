from shiny import Inputs, Outputs, Session, module, render, ui
import shinywidgets as sw
import pandas as pd
import plotly.express as px

# ============================================================
# Module: stat_box
# ============================================================


@module.ui
def stat_box_ui(stat):
    return ui.value_box(
        title=stat,
        value=ui.output_text("season_average"),
        showcase=sw.output_widget("sparkline"),
        theme="bg-gradient-red-indigo",
        showcase_layout=ui.showcase_bottom(width="80%", height="50%"),
    )


@module.server
def stat_box_server(
    input: Inputs, output: Outputs, session: Session, stat: str, game_logs: pd.DataFrame
):
    @render.text
    def season_average():
        mean_value = game_logs()[stat].fillna(0).mean()
        return round(mean_value) if pd.notnull(mean_value) else 0

    @sw.render_widget
    def sparkline():
        rolling_avg = game_logs()[stat].rolling(window=7).mean().tail(30)
        fig = px.line(rolling_avg)

        fig.update_traces(
            line_color="rgba(255, 255, 255, 0.8)",
            line_width=1,
            fill="tozeroy",
            fillcolor="rgba(255, 255, 255, 0.8)",
            hoverinfo="y",
        )
        fig.update_xaxes(visible=False, showgrid=False)
        fig.update_yaxes(visible=False, showgrid=False)
        fig.update_layout(
            height=60,
            hovermode="x",
            margin=dict(t=0, r=0, l=0, b=0),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
        )
        return fig
