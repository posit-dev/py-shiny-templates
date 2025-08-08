import subprocess
import sys
import time
from pathlib import Path

import requests
from shiny import App, Inputs, Outputs, Session, reactive, render, req, ui

BASE_PATH = Path(__file__).parent.resolve()
DEFAULT_PORT = 8081
STARTUP_DELAY = 5
REQUEST_TIMEOUT = 5
GITHUB_REPO_URL = "https://github.com/posit-dev/py-shiny-templates"
GITHUB_BRANCH = "main"
STARTUP_TIMEOUT = 10
STARTUP_POLL_INTERVAL = 0.2

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
        ui.input_select(
            "main_category",
            "🤖 AI Framework",
            choices={"": "Choose a framework..."}
            | {k: k.title() for k in FOLDER_STRUCTURE.keys()},
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


current_process = None


def server(input: Inputs, output: Outputs, session: Session):
    current_app_path = None

    def is_process_running() -> bool:
        return current_process is not None and current_process.poll() is None

    def start_app_process(app_path: Path, port: int = DEFAULT_PORT) -> bool:
        nonlocal current_app_path
        global current_process

        if current_app_path == app_path and is_process_running():
            return True

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
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                text=True,
            )

            start_time = time.time()
            url = f"http://127.0.0.1:{port}"
            while time.time() - start_time < STARTUP_TIMEOUT:
                if current_process.poll() is not None:
                    return False
                try:
                    resp = requests.get(url, timeout=REQUEST_TIMEOUT)
                    if resp.status_code == 200:
                        current_app_path = app_path
                        return True
                except Exception:
                    pass
                time.sleep(STARTUP_POLL_INTERVAL)

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
    @reactive.event(input.main_category, input.sub_category)
    def stop_on_clear_selection():
        nonlocal current_app_path
        app_path = get_selected_app_path()
        if not app_path and is_process_running():
            stop_current_process()
            current_app_path = None

    @reactive.effect
    @reactive.event(input.main_category)
    def update_sub_category():
        main_cat = input.main_category()

        if main_cat and main_cat in FOLDER_STRUCTURE:
            choices = {
                sub: sub.replace("_", " ").title() for sub in FOLDER_STRUCTURE[main_cat]
            }
            ui.update_select("sub_category", choices=choices)

    @reactive.calc
    def get_selected_app_path():
        main_cat = req(input.main_category())
        sub_cat = req(input.sub_category())
        if main_cat and sub_cat:
            return BASE_PATH / main_cat / sub_cat / "app-core.py"
        return None

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

        app_path = get_selected_app_path()

        if not app_path.exists():
            return ui.div(
                ui.h4("❌ App Not Found"),
                ui.p(f"The app file was not found at: {app_path}"),
                class_="text-center text-danger p-3",
            )

        try:
            app_started = start_app_process(app_path, DEFAULT_PORT)

            if app_started:
                return ui.card(
                    ui.card_header(
                        "Example App",
                        ui.input_action_link("view_source", ""),
                        class_="d-flex justify-content-between align-items-center",
                    ),
                    ui.output_ui("card_body", fill=True, fillable=True),
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
    def card_body():
        app_path = get_selected_app_path()

        if not app_path.exists():
            return ui.notification_show(f"# Error: File not found at {app_path}")

        rel_path = app_path.relative_to(BASE_PATH.parent)
        github_url = f"{GITHUB_REPO_URL}/blob/{GITHUB_BRANCH}/{rel_path}"

        if (input.view_source() % 2) == 0:
            ui.update_action_link("view_source", label="📝 View Source Code")

            return ui.tags.iframe(
                src=f"http://127.0.0.1:{DEFAULT_PORT}",
                frameborder="0",
                class_="html-fill-item html-fill-container",
                style="min-height: 500px;",
            )
        else:
            ui.update_action_link("view_source", label="👀 View App")

            code = app_path.read_text()
            content = f"[View on GitHub]({github_url})\n\n```python\n{code}\n```\n"
            return ui.markdown(content)


app = App(app_ui, server)
