from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_ai import Agent
from shiny.express import ui


class CityLocation(BaseModel):
    city: str
    county: str
    state: str


_ = load_dotenv()
chat_client = Agent(
    "openai:o4-mini",
    system_prompt="You are a helpful assistant.",
    output_type=CityLocation,
)


# Set some Shiny page options
ui.page_opts(
    title="Pydantic AI Chat with Structured Output",
    fillable=True,
    fillable_mobile=True,
)


# Create and display a Shiny chat component
chat = ui.Chat(
    id="chat",
)
chat.ui(
    messages=[
        {
            "role": "assistant",
            "content": """
Hello! Ask me where the superbowl was held in any year and I can tell the state, county, and city.
For example, you can ask:
- <span class="suggestion"> Where was the superbowl in 2020? </span>
- <span class="suggestion"> What city hosted the superbowl in 2015? </span>
- <span class="suggestion"> Where was the superbowl in 2018? </span>
""",
        }
    ],
)


@chat.on_user_submit
async def handle_user_input(user_input: str):
    result = await chat_client.run(user_input)
    city_info = result.output
    message = (
        f"City: {city_info.city}, County: {city_info.county}, State: {city_info.state}"
    )
    await chat.append_message(message)
