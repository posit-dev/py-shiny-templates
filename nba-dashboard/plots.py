import numpy as np
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go

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
    vals = careers_df[stat]
    vals = vals[~vals.isnull()]
    fig = ff.create_distplot(
        [vals],
        ["Overall"],
        rug_text=[careers_df["player_name"]],
        colors=["black"],
        show_hist=False,
    )
    # Clean up some defaults (1st trace is the density plot, 2nd is the rug plot)
    fig.data[0].hoverinfo = "none"
    fig.data[0].showlegend = False
    fig.data[1].hoverinfo = "text+x"
    fig.data[1].customdata = careers_df["person_id"]
    # Use height of the density plot to inform the vertical lines
    ymax = fig.data[0].y.max()
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
