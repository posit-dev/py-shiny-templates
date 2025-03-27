from pathlib import Path

import shinyswatch
from chatlas import ChatOpenAI
from dotenv import load_dotenv
from faicons import icon_svg
from pydantic import BaseModel
from shiny import reactive
from shiny.express import input, render, ui

# Load the system prompt for the cooking assistant
app_dir = Path(__file__).parent
with open(app_dir / "prompt.md") as f:
    system_prompt = f.read()

# Connect to OpenAI
_ = load_dotenv()
chat_client = ChatOpenAI(system_prompt=system_prompt)

# Page level UI options
ui.page_opts(
    fillable=True,
    fillable_mobile=True,
    theme=shinyswatch.theme.minty,
    class_="bg-primary-subtle",
)

# Bump up link color contrast (for Minty theme)
ui.tags.style(":root { --bs-link-color: #4e7e71; }")

chat = ui.Chat(id="chat")

welcome_message = """
Hello! I'm here to help you find something to cook for dinner, or really any other meal you're planning.
When you're ready, click the "Extract recipe" button to receive a structured form of the recipe.

Here are some examples of what you can ask me:

- <span class="suggestion"> What can I make with chicken, broccoli, and rice? </span>
- <span class="suggestion"> What ingredients do I need to make lasagna? </span>
- <span class="suggestion"> How do I make chocolate chip cookies? </span>
"""


# Display chat in a card
with ui.card(full_screen=True, style="width:min(720px, 100%)", class_="mx-auto"):
    ui.card_header("What's for dinner?", class_="bg-primary fs-4 lead")
    chat.ui(
        messages=[welcome_message],
        placeholder="What are you in the mood for?",
        width="min(900px, 100%)",
        icon_assistant=icon_svg("utensils"),
    )
    with ui.card_footer(class_="d-flex gap-3"):
        ui.input_action_button(
            "clear",
            "Clear chat",
            class_="btn-outline-danger btn-sm",
            icon=icon_svg("trash"),
            disabled=True,
        )
        ui.input_action_button(
            "extract_recipe",
            "Extract recipe",
            icon=icon_svg("download"),
            disabled=True,
            class_="btn-outline-primary btn-sm",
        )


# Respond to user input
@chat.on_user_submit
async def _(user_input: str):
    response = await chat_client.stream_async(user_input)
    await chat.append_message_stream(response)


# Clear the chat via "Clear chat" button
@reactive.effect
@reactive.event(input.clear)
async def _():
    chat_client.set_turns([])
    await chat.clear_messages()
    await chat.append_message(welcome_message)


# Enable the action buttons when we get our first result
@reactive.effect
def _():
    if not chat.latest_message_stream.result():
        return
    ui.update_action_button("extract_recipe", disabled=False)
    ui.update_action_button("clear", disabled=False)


# Define the recipe schema using Pydantic
class Ingredient(BaseModel):
    name: str
    amount: str
    unit: str


class RecipeStep(BaseModel):
    step_number: int
    instruction: str


class Recipe(BaseModel):
    name: str
    description: str
    ingredients: list[Ingredient]
    steps: list[RecipeStep]
    prep_time: str
    cook_time: str
    servings: int


_ = Recipe.model_rebuild()


# Extract a recipe from the latest response
@reactive.calc
@reactive.event(input.extract_recipe)
async def parsed_recipe():
    return await chat_client.extract_data_async(
        chat.latest_message_stream.result(),
        data_model=Recipe,
    )


@reactive.calc
async def recipe_message():
    recipe = await parsed_recipe()

    if not recipe:
        return "Unable to extract a recipe from the chat. Please try again."

    ingredients = [
        ui.tags.li(f'{ing["amount"]} {ing["unit"]} {ing["name"]}')
        for ing in recipe["ingredients"]
    ]

    instructions = [
        ui.tags.li(
            step["instruction"], style="list-style-type: decimal; margin-left: 20px;"
        )
        for step in recipe["steps"]
    ]

    return f"""
Gather your ingredients and let's get started! 🍳

### {recipe["name"]}

{recipe["description"]}

#### Ingredients:

{ui.tags.ul(ingredients)}

#### Instructions:

{ui.tags.ol(instructions)}

Prep time: {recipe["prep_time"]}
Cook time: {recipe["cook_time"]}
Servings: {recipe["servings"]}

Enjoy your meal! 🍽️

Want to save this recipe? Click the "Save recipe" button below.

{download_recipe}
"""


@reactive.effect
@reactive.event(input.extract_recipe)
async def _():
    async with chat.message_stream_context() as stream:
        await stream.append("Cooking up a recipe for you!")
        await stream.replace(await recipe_message())


with ui.hold() as download_recipe:

    @render.download(filename="recipe.json", label="Download recipe")
    async def download_handler():
        import json

        recipe = await parsed_recipe()
        yield json.dumps(recipe, indent=2)
