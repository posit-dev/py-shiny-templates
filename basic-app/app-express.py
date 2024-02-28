from shiny import render, ui
from shiny.express import input

ui.panel_title("Hello Shiny!")
ui.input_slider("n", "N", 0, 100, 20)


@render.code
def txt():
    return f"n*2 is {input.n() * 2}"
