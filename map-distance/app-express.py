import ipyleaflet as L
from faicons import icon_svg
from geopy.distance import geodesic, great_circle
from shared import BASEMAPS, CITIES
from shiny import reactive
from shiny.express import input, render, ui
from shinywidgets import render_widget

city_names = sorted(list(CITIES.keys()))

ui.page_opts(title="Location Distance Calculator", fillable=True)
{"class": "bslib-page-dashboard"}

with ui.sidebar():
    ui.input_selectize("loc1", "Location 1", choices=city_names, selected="New York")
    ui.input_selectize("loc2", "Location 2", choices=city_names, selected="London")
    ui.input_selectize(
        "basemap",
        "Choose a basemap",
        choices=list(BASEMAPS.keys()),
        selected="WorldImagery",
    )
    ui.input_dark_mode(mode="dark")

with ui.layout_column_wrap(fill=False):
    with ui.value_box(showcase=icon_svg("globe"), theme="gradient-blue-indigo"):
        "Great Circle Distance"

        @render.text
        def great_circle_dist():
            circle = great_circle(loc1xy(), loc2xy())
            return f"{circle.kilometers.__round__(1)} km"

    with ui.value_box(showcase=icon_svg("ruler"), theme="gradient-blue-indigo"):
        "Geodisic Distance"

        @render.text
        def geo_dist():
            dist = geodesic(loc1xy(), loc2xy())
            return f"{dist.kilometers.__round__(1)} km"

    with ui.value_box(showcase=icon_svg("mountain"), theme="gradient-blue-indigo"):
        "Altitude Difference"

        @render.text
        def altitude():
            try:
                return f'{loc1()["altitude"] - loc2()["altitude"]} m'
            except TypeError:
                return "N/A (altitude lookup failed)"


with ui.card():
    ui.card_header("Map (drag the markers to change locations)")

    @render_widget
    def map():
        return L.Map(zoom=4, center=(0, 0))


# Reactive values to store location information
loc1 = reactive.value()
loc2 = reactive.value()


# Update the reactive values when the selectize inputs change
@reactive.effect
def _():
    loc1.set(CITIES.get(input.loc1(), loc_str_to_coords(input.loc1())))
    loc2.set(CITIES.get(input.loc2(), loc_str_to_coords(input.loc2())))


# When a marker is moved, the input value gets updated to "lat, lon",
# so we decode that into a dict (and also look up the altitude)
def loc_str_to_coords(x: str) -> dict:
    latlon = x.split(", ")
    if len(latlon) != 2:
        return {}

    lat = float(latlon[0])
    lon = float(latlon[1])

    try:
        import requests

        query = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}"
        r = requests.get(query).json()
        altitude = r["results"][0]["elevation"]
    except Exception:
        altitude = None

    return {"latitude": lat, "longitude": lon, "altitude": altitude}


# Convenient way to get the lat/lons as a tuple
@reactive.calc
def loc1xy():
    return loc1()["latitude"], loc1()["longitude"]


@reactive.calc
def loc2xy():
    return loc2()["latitude"], loc2()["longitude"]


# Add marker for first location
@reactive.effect
def _():
    update_marker(map.widget, loc1xy(), on_move1, "loc1")


# Add marker for second location
@reactive.effect
def _():
    update_marker(map.widget, loc2xy(), on_move2, "loc2")


# Add line and fit bounds when either marker is moved
@reactive.effect
def _():
    update_line(map.widget, loc1xy(), loc2xy())


# If new bounds fall outside of the current view, fit the bounds
@reactive.effect
def _():
    l1 = loc1xy()
    l2 = loc2xy()

    lat_rng = [min(l1[0], l2[0]), max(l1[0], l2[0])]
    lon_rng = [min(l1[1], l2[1]), max(l1[1], l2[1])]
    new_bounds = [
        [lat_rng[0], lon_rng[0]],
        [lat_rng[1], lon_rng[1]],
    ]

    b = map.widget.bounds
    if len(b) == 0:
        map.widget.fit_bounds(new_bounds)
    elif (
        lat_rng[0] < b[0][0]
        or lat_rng[1] > b[1][0]
        or lon_rng[0] < b[0][1]
        or lon_rng[1] > b[1][1]
    ):
        map.widget.fit_bounds(new_bounds)


# Update the basemap
@reactive.effect
def _():
    update_basemap(map.widget, input.basemap())


# ---------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------


def update_marker(map: L.Map, loc: tuple, on_move: object, name: str):
    remove_layer(map, name)
    m = L.Marker(location=loc, draggable=True, name=name)
    m.on_move(on_move)
    map.add_layer(m)


def update_line(map: L.Map, loc1: tuple, loc2: tuple):
    remove_layer(map, "line")
    map.add_layer(
        L.Polyline(locations=[loc1, loc2], color="blue", weight=2, name="line")
    )


def update_basemap(map: L.Map, basemap: str):
    for layer in map.layers:
        if isinstance(layer, L.TileLayer):
            map.remove_layer(layer)
    map.add_layer(L.basemap_to_tiles(BASEMAPS[input.basemap()]))


def remove_layer(map: L.Map, name: str):
    for layer in map.layers:
        if layer.name == name:
            map.remove_layer(layer)


def on_move1(**kwargs):
    return on_move("loc1", **kwargs)


def on_move2(**kwargs):
    return on_move("loc2", **kwargs)


# When the markers are moved, update the selectize inputs to include the new
# location (which results in the locations() reactive value getting updated,
# which invalidates any downstream reactivity that depends on it)
def on_move(id, **kwargs):
    loc = kwargs["location"]
    loc_str = f"{loc[0]}, {loc[1]}"
    choices = city_names + [loc_str]
    ui.update_selectize(id, selected=loc_str, choices=choices)
