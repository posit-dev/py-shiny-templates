from shiny import App, Inputs, Outputs, Session, reactive, render, req, ui

FOLDER_STRUCTURE = {
    "langchain": ["basic", "structured-output", "tool-calling"],
    "llama-index": [
        "basic",
        "structured-output",
        "tool-calling",
    ],
    "llm-package": ["basic", "structured-output", "tool-calling"],
    "pydantic-ai": ["basic", "structured-output", "tool-calling"],
}

FRAMEWORK_LABELS = {
    "langchain": "LangChain",
    "llama-index": "LlamaIndex",
    "llm-package": "llm package",
    "pydantic-ai": "Pydantic AI",
}

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_select(
            "main_category",
            "🤖 AI Framework",
            choices={"": "Choose a framework..."}
            | {k: FRAMEWORK_LABELS.get(k, k) for k in FOLDER_STRUCTURE.keys()},
            selected="",
        ),
        ui.panel_conditional(
            "input.main_category != ''",
            ui.input_select(
                "sub_category",
                "📂 Example category",
                choices=[],
            ),
        ),
        open={"mobile": "always-above"},
    ),
    ui.output_ui("embedded_app", fill=True, fillable=True),
    title="Shiny Chat + AI Framework Chooser",
    fillable=True,
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.effect
    @reactive.event(input.main_category)
    def update_sub_category():
        main_cat = input.main_category()

        if main_cat and main_cat in FOLDER_STRUCTURE:
            choices = {
                sub: sub.replace("-", " ").title() for sub in FOLDER_STRUCTURE[main_cat]
            }
            ui.update_select("sub_category", choices=choices)

    @render.ui
    def embedded_app():
        if not input.main_category():
            return ui.div(
                ui.h4("Select an AI framework"),
                ui.p("This framework will power the chat responses."),
                class_="text-center text-muted p-5",
            )

        if not input.sub_category():
            return ui.div(
                ui.h4("Select an example category"),
                ui.p("This will load a specific example app."),
                class_="text-center text-muted p-5",
            )

        main_cat = req(input.main_category())
        sub_cat = req(input.sub_category())
        url = f"https://posit-ai-{main_cat}-{sub_cat}.share.connect.posit.cloud/"
        return ui.tags.iframe(
            src=url,
            frameborder="0",
            class_="html-fill-item html-fill-container",
            style="min-height: 500px;",
        )


app = App(app_ui, server)
