from chatlas import ChatAnthropic
from dotenv import load_dotenv
from faicons import icon_svg
from shiny import App, Inputs, reactive, render, ui

_ = load_dotenv()
chat_client = ChatAnthropic(
    system_prompt="""
    You are a helpful AI fitness coach.
    Give detailed workout plans to users based on their fitness goals and experience level.
    Before getting into details, give a brief introduction to the workout plan.
    Keep the overall tone encouraging and professional yet friendly.
    Generate the response in Markdown format and avoid using h1, h2, or h3.
    """,
)

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_select(
            "goal",
            "Fitness Goal",
            ["Strength", "Cardio", "Flexibility", "General Fitness"],
        ),
        ui.input_selectize(
            "equipment",
            "Available Equipment",
            ["Dumbbells", "Barbell", "Resistance Bands", "Bodyweight"],
            multiple=True,
            selected=["Bodyweight", "Barbell"],
        ),
        ui.input_slider("experience", "Experience Level", min=1, max=10, value=5),
        ui.input_slider(
            "duration", "Duration (mins)", min=15, max=90, step=5, value=45
        ),
        ui.input_select(
            "daysPerWeek",
            "Days per Week",
            [str(i) for i in range(1, 8)],
            selected="3",
        ),
        ui.input_task_button(
            "generate", "Get Workout", icon=icon_svg("person-running")
        ),
        ui.output_ui("download_ui"),
        open={"mobile": "always-above"},
    ),
    ui.output_markdown_stream(
        "workout_stream",
        content=(
            "Hi there! 👋 I'm your AI fitness coach. 💪"
            "\n\n"
            "Fill out the form in the sidebar to get started. 📝 🏋️‍♂ ️"
        ),
    ),
    title="Personalized Workout Plan Generator",
)


def server(input: Inputs):

    workout_stream = ui.MarkdownStream("workout_stream")

    # When the user clicks the "Generate Workout" button, generate a workout plan
    @reactive.effect
    @reactive.event(input.generate)
    async def _():
        prompt = f"""
        Generate a brief {input.duration()}-minute workout plan for a {input.goal()} fitness goal.
        On a scale of 1-10, I have a level  {input.experience()} experience,
        works out {input.daysPerWeek()} days per week, and have access to:
        {", ".join(input.equipment()) if input.equipment() else "no equipment"}.
        Format the response in Markdown.
        """

        await workout_stream.stream(await chat_client.stream_async(prompt))

    @render.ui
    def download_ui():
        _ = workout_stream.latest_stream.result()
        return ui.download_button("download", "Download Workout")

    @render.download(filename="workout_plan.md", label="Download Workout")
    def download():
        yield workout_stream.latest_stream.result()


app = App(app_ui, server)
