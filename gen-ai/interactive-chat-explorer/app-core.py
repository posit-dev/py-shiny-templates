import subprocess
import sys
import time
from pathlib import Path

import requests
from shiny import App, Inputs, Outputs, Session, reactive, render, ui

BASE_PATH = Path(__file__).parent.resolve()
DEFAULT_PORT = 8081
STARTUP_DELAY = 5
REQUEST_TIMEOUT = 5
GITHUB_REPO_URL = "https://github.com/posit-dev/py-shiny-templates"
GITHUB_BRANCH = "main"

FOLDER_STRUCTURE = {
    "langchain": ["basic", "structured_output", "tool_calling"],
    "llama-index": [
        "basic",
        "rag_with_chatlas",
        "structured_output",
        "tool_calling",
    ],
    "llm_package": ["basic", "structured_output", "tool_calling"],
    "pydantic-ai": ["basic", "structured_output", "tool_calling"],
}

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h3("Interactive Chat Explorer"),
        ui.br(),
        ui.input_select(
            "main_category",
            "📁 Select Category:",
            choices={"": "Choose a category..."}
            | {k: k.title() for k in FOLDER_STRUCTURE.keys()},
            selected="",
        ),
        ui.br(),
        ui.input_select(
            "sub_category",
            "📂 Select Subcategory:",
            choices={"": "First select a category..."},
            selected="",
        ),
        ui.br(),
        width=350,
    ),
    ui.h1("Shiny Chat Preview with Different Providers"),
    ui.p(
        "Select a category and subcategory to run the app " "and view its source code."
    ),
    ui.div(
        ui.output_ui("embedded_app"),
        ui.br(),
        ui.h3("📋 Source Code"),
        ui.output_ui("app_source"),
        id="main_content",
    ),
    title="Shiny Interactive Chat Explorer",
)


current_process = None


def server(input: Inputs, output: Outputs, session: Session):
    def start_app_process(app_path: Path, port: int = DEFAULT_PORT) -> bool:
        global current_process
        stop_current_process()

        try:
            cmd = [
                sys.executable,
                "-m",
                "shiny",
                "run",
                "app-core.py",
                "--port",
                str(port),
                "--host",
                "127.0.0.1",
            ]

            current_process = subprocess.Popen(
                cmd,
                cwd=str(app_path.parent),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            time.sleep(STARTUP_DELAY)

            try:
                response = requests.get(
                    f"http://127.0.0.1:{port}", timeout=REQUEST_TIMEOUT
                )
                return response.status_code == 200
            except Exception:
                return False

        except Exception as e:
            print(f"Error starting app: {e}")
            return False

    def stop_current_process():
        global current_process
        if current_process:
            try:
                current_process.terminate()
                current_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                current_process.kill()
            except Exception:
                pass
            finally:
                current_process = None

    session.on_ended(lambda: stop_current_process())

    @reactive.effect
    @reactive.event(input.main_category)
    def update_sub_category():
        main_cat = input.main_category()

        if main_cat and main_cat in FOLDER_STRUCTURE:
            sub_choices = {
                sub: sub.replace("_", " ").title() for sub in FOLDER_STRUCTURE[main_cat]
            }
            choices = {"": "Choose a subcategory..."} | sub_choices
        else:
            choices = {"": "First select a category..."}

        ui.update_select("sub_category", choices=choices, selected="")

    @reactive.calc
    def get_selected_app_path():
        main_cat = input.main_category()
        sub_cat = input.sub_category()
        if main_cat and sub_cat:
            return BASE_PATH / main_cat / sub_cat / "app-core.py"
        return None

    def format_title(main_cat: str, sub_cat: str) -> str:
        formatted_sub = sub_cat.replace("_", " ").title()
        return f"🤖 Running: {main_cat.title()} - {formatted_sub}"

    @render.ui
    def embedded_app():
        app_path = get_selected_app_path()
        main_cat = input.main_category()
        sub_cat = input.sub_category()

        if not app_path:
            return ui.div(
                ui.h4("Select an App to Run"),
                ui.p(
                    "Choose a category and subcategory from the sidebar "
                    "to run a chat app."
                ),
                class_="text-center text-muted p-5",
            )

        if not app_path.exists():
            return ui.div(
                ui.h4("❌ App Not Found"),
                ui.p(f"The app file was not found at: {app_path}"),
                class_="text-center text-danger p-3",
            )

        try:
            app_started = start_app_process(app_path, DEFAULT_PORT)

            if app_started:
                return ui.div(
                    ui.h4(format_title(main_cat, sub_cat)),
                    ui.p(f"📍 Path: {app_path.relative_to(BASE_PATH.parent)}"),
                    ui.hr(),
                    ui.div(
                        ui.HTML(
                            f"""
                            <iframe
                                src="http://127.0.0.1:{DEFAULT_PORT}"
                                width="100%"
                                height="600px"
                                frameborder="0"
                                style="border: 1px solid #ddd;
                                       border-radius: 8px;">
                            </iframe>
                        """
                        ),
                        class_="mb-3",
                    ),
                    class_="bg-light p-3 rounded",
                )
            else:
                return ui.div(
                    ui.h4("⚠️ Failed to Start App"),
                    ui.p(
                        "The app could not be started. This might be due to "
                        "missing dependencies or configuration issues."
                    ),
                    ui.p(f"App path: {app_path}"),
                    class_="text-center text-warning p-3",
                )

        except Exception as e:
            return ui.div(
                ui.h4("⚠️ Error Starting App"),
                ui.p(f"Error: {str(e)}"),
                ui.pre(f"Details: {type(e).__name__}"),
                class_="text-center text-warning p-3",
            )

    @render.ui
    def app_source():
        app_path = get_selected_app_path()

        if not app_path:
            return ui.p("# Select a category and subcategory to view the source code")

        if not app_path.exists():
            return ui.p(f"# Error: File not found at {app_path}")

        rel_path = app_path.relative_to(BASE_PATH.parent)
        github_url = f"{GITHUB_REPO_URL}/blob/{GITHUB_BRANCH}/{rel_path}"

        return ui.p(
            ui.a(
                f"View source: {rel_path}",
                href=github_url,
                target="_blank",
                style="font-weight: bold;",
            )
        )


app = App(app_ui, server)
