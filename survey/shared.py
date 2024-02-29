from shiny import ui

INPUTS = {
    "name": ui.input_text("name", "Enter your name"),
    "country": ui.input_select(
        "country",
        "Country",
        choices=["", "USA", "Canada", "Portugal"],
    ),
    "age": ui.input_numeric("age", "Age", None, min=0, max=120, step=1),
    "income": ui.input_numeric("income", "Annual income", None, step=1000),
    "avengers": ui.input_radio_buttons(
        "avengers",
        "How would you rate: 'Avengers'?",
        choices=[1, 2, 3, 4, 5],
        selected=[],
        inline=True,
    ),
    "spotlight": ui.input_radio_buttons(
        "spotlight",
        "How would you rate: 'Spotlight'?",
        choices=[1, 2, 3, 4, 5],
        selected=[],
        inline=True,
    ),
    "the_big_short": ui.input_radio_buttons(
        "the_big_short",
        "How would you rate: 'The Big Short'?",
        choices=[1, 2, 3, 4, 5],
        selected=[],
        inline=True,
    ),
}
