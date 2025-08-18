from pathlib import Path

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
    ui.head_content(
        ui.tags.link(
            rel="stylesheet",
            href=(
                "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/"
                "styles/github.min.css"
            ),
        ),
        ui.tags.script(
            src=(
                "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/"
                "highlight.min.js"
            )
        ),
    ),
    title="Shiny Chat + AI Framework Chooser",
    fillable=True,
)


def server(input: Inputs, output: Outputs, session: Session):
    show_source = reactive.Value(False)

    @reactive.effect
    @reactive.event(input.main_category)
    def update_sub_category():
        main_cat = input.main_category()
        if main_cat and main_cat in FOLDER_STRUCTURE:
            choices = {
                sub: sub.replace("-", " ").title() for sub in FOLDER_STRUCTURE[main_cat]
            }
            ui.update_select("sub_category", choices=choices)

    @reactive.effect
    @reactive.event(input.main_category, input.sub_category)
    def reset_view_mode():
        show_source.set(False)

    @reactive.effect
    @reactive.event(input.toggle_view)
    def _toggle_view():
        show_source.set(not show_source())

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
        url = f"https://posit-ai-{main_cat}-{sub_cat}." "share.connect.posit.cloud/"

        toggle_label = "▶️ View App" if show_source() else "📝 View Source Code"
        header = ui.card_header(
            ui.div(
                ui.div("Example App", class_="fw-semibold"),
                ui.div(
                    ui.input_action_link(
                        "toggle_view",
                        toggle_label,
                        class_="text-decoration-none",
                    ),
                    class_="ms-auto",
                ),
                class_=("d-flex justify-content-between " "align-items-center w-100"),
            )
        )

        if show_source():
            base_dir = Path(__file__).parent
            source_path = base_dir / f"{main_cat}-{sub_cat}" / "app-express.py"
            try:
                code_text = source_path.read_text(encoding="utf-8")
            except Exception as e:
                code_text = "Could not load source: " f"{source_path}\n\nError: {e}"

            title_txt = (
                f"{FRAMEWORK_LABELS.get(main_cat, main_cat)} "
                f"· {sub_cat.replace('-', ' ').title()}"
            )
            code_id = f"source_code_{main_cat}_{sub_cat}"
            copy_js = (
                "(function(btn){\n"
                f"  var el = document.getElementById('{code_id}');\n"
                "  if (!el) return;\n"
                "  navigator.clipboard.writeText(el.innerText)\n"
                "    .then(function(){\n"
                "    var old = btn.innerText;\n"
                "    btn.innerText = 'Copied';\n"
                "    setTimeout(function(){ btn.innerText = old; }, 1500);\n"
                "  });\n"
                "})(this); return false;"
            )
            toolbar = ui.div(
                ui.tags.span(title_txt, class_="fw-semibold"),
                ui.tags.button(
                    "Copy code",
                    class_="btn btn-sm btn-outline-secondary",
                    onclick=copy_js,
                ),
                class_=("d-flex justify-content-between align-items-center mb-2"),
            )
            code_block = ui.tags.pre(
                ui.tags.code(
                    code_text,
                    id=code_id,
                    class_="language-python",
                ),
                class_="mb-0",
            )
            highlight_script = ui.tags.script(
                (
                    "(function(){\n"
                    f"  var el = document.getElementById('{code_id}');\n"
                    "  if (el && window.hljs) {\n"
                    "    window.hljs.highlightElement(el);\n"
                    "  }\n"
                    "})();"
                )
            )
            body = ui.card_body(
                toolbar,
                code_block,
                highlight_script,
                class_="overflow-auto",
            )
        else:
            body = ui.card_body(
                ui.tags.iframe(
                    src=url,
                    frameborder="0",
                    class_="html-fill-item html-fill-container",
                    style="min-height: 600px;",
                )
            )

        return ui.card(
            header,
            body,
            class_="html-fill-item html-fill-container",
        )


app = App(app_ui, server)
