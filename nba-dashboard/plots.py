import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import gaussian_kde

color_palette = px.colors.qualitative.D3


def radar_chart(percs_df, stats_df, stats):
    fig = go.Figure()

    for _, row in percs_df.iterrows():
        id = row["person_id"]
        r = [row[x] for x in stats]
        vals = stats_df[stats_df["person_id"] == id][stats].values[0]
        text = np.round(vals, 2).astype(str).tolist()
        fig.add_trace(
            go.Scatterpolar(
                r=r + r[:1],
                theta=stats + stats[:1],
                text=text + text[:1],
                name=row["player_name"],
                hoverinfo="text+name",
                line=dict(width=1, color=row["color"]),
            )
        )

    fig.update_layout(
        margin=dict(l=30, r=30, t=30, b=30),
        polar=dict(radialaxis=dict(range=[0, 1])),
        showlegend=True,
        legend=dict(orientation="h", y=-0.1, yanchor="top", x=0.5, xanchor="center"),
    )

    return fig


def density_plot(careers_df, stats_df, stat, players_dict, on_rug_click):
    vals = careers_df[stat].dropna().to_numpy()
    kde = gaussian_kde(vals)
    x_range = np.linspace(vals.min(), vals.max(), 500)
    y_density = kde(x_range)

    fig = go.Figure()
    # 1. Density line trace
    fig.add_trace(
        go.Scatter(
            x=x_range,
            y=y_density,
            mode="lines",
            name="Overall",
            line=dict(color="black"),
            hoverinfo="none",
            showlegend=False,
        )
    )
    # 2. Rug plot trace
    fig.add_trace(
        go.Scatter(
            x=vals,
            y=[0] * len(vals),
            mode="markers",
            marker=dict(symbol="line-ns-open", color="black"),
            text=careers_df["player_name"],
            customdata=careers_df["person_id"],
            hoverinfo="text+x",
            showlegend=False,
        )
    )

    ymax = y_density.max()
    # Arrange rows from highest to lowest value so that legend order is correct
    stats_df = stats_df.sort_values(stat, ascending=False)
    # Add vertical lines for each player
    for _, row in stats_df.iterrows():
        x = row[stat]
        fig.add_scatter(
            x=[x, x],
            y=[0, ymax],
            mode="lines",
            name=players_dict[row["person_id"]],
            line=dict(color=row["color"], width=1),
            hoverinfo="x+name",
        )

    fig.update_layout(
        hovermode="x",
        xaxis=dict(title=stat + " per game (career average)", hoverformat=".1f"),
        legend=dict(orientation="h", y=1.03, yanchor="bottom", x=0.5, xanchor="center"),
    )

    # Convert Figure to FigureWidget so we can add click events
    fig = go.FigureWidget(fig.data, fig.layout)
    fig.data[1].on_click(on_rug_click)

    return fig
