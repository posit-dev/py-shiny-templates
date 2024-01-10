from shiny import App, ui, reactive, render
from shinywidgets import render_widget, output_widget
import ipyleaflet as ipyl
from ipyleaflet import basemaps
from geopy.geocoders import Nominatim
from geopy.distance import great_circle, geodesic
from cities import cities
from faicons import icon_svg


geolocator = Nominatim(user_agent="city_locator")

city_names = sorted(list(cities.keys()))

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_selectize("city_1", "City 1", choices=city_names, selected="New York"),
        ui.input_selectize("city_2", "City 2", choices=city_names, selected="London"),
    ),
    ui.layout_columns(
        ui.value_box(
            "Great Circle Distance",
            ui.output_text("great_circle_dist"),
            theme="gradient-blue-indigo",
            showcase=icon_svg("globe", width="50px"),
        ),
        ui.value_box(
            "Geodisic Distance",
            ui.output_text("geo_dist"),
            theme="gradient-blue-indigo",
            showcase=icon_svg("ruler", width="50px"),
        ),
        ui.value_box(
            "Altitude Difference",
            ui.output_text("altitude"),
            theme="gradient-blue-indigo",
            showcase=icon_svg("mountain", width="50px"),
        ),
    ),
    ui.card(output_widget("map"), fill=True),
)


def server(input, output, session):
    @reactive.Calc()
    def city_1_stats():
        return (
            cities[input.city_1()]["latitude"],
            cities[input.city_1()]["longitude"],
        )

    @reactive.Calc()
    def city_2_stats():
        return (
            cities[input.city_2()]["latitude"],
            cities[input.city_2()]["longitude"],
        )

    @render.text()
    def great_circle_dist():
        return (
            f"{great_circle(city_1_stats(), city_2_stats()).kilometers.__round__(2)} km"
        )

    @render.text()
    def geo_dist():
        return f"{geodesic(city_1_stats(), city_2_stats()).kilometers.__round__(2)} km"

    @render.text()
    def altitude():
        city_1_alt = cities[input.city_1()]["altitude"]
        city_2_alt = cities[input.city_2()]["altitude"]

        return f"{abs(city_1_alt - city_2_alt)} m"

    @render_widget
    def map():
        m = ipyl.Map(basemap=basemaps.Gaode.Satellite, zoom=4)
        m.add_layer(ipyl.Marker(location=city_1_stats()))
        m.add_layer(ipyl.Marker(location=city_2_stats()))
        m.add_layer(
            ipyl.Polyline(
                locations=[city_1_stats(), city_2_stats()],
                color="blue",
                weight=2,
            )
        )

        # Calculate the bounds
        bounds = [
            [
                min(city_1_stats()[0], city_2_stats()[0]),
                min(city_1_stats()[1], city_2_stats()[1]),
            ],
            [
                max(city_1_stats()[0], city_2_stats()[0]),
                max(city_1_stats()[1], city_2_stats()[1]),
            ],
        ]

        # Fit the map to the bounds
        m.fit_bounds(bounds)

        return m


app = App(app_ui, server)
