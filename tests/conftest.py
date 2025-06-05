import json
from pathlib import Path
from typing import Any, Dict, Generator, List

import pytest
from playwright.sync_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    sync_playwright,
)


def load_test_urls() -> List[str]:
    base_dir = Path(__file__).parent.parent
    config_path = base_dir / "deployments.json"
    urls: List[str] = []
    try:
        if not config_path.exists():
            print(
                f"Warning: Configuration file {config_path} not found. No URLs will be loaded."
            )
            return urls
        with config_path.open(encoding="utf-8") as f:
            data: Dict[str, Any] = json.load(f)
        urls = [
            item["url"]
            for item in data.get("include", [])
            if isinstance(item, dict) and "url" in item
        ]
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {config_path}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while loading test URLs: {e}")
    if not urls:
        print(
            "Warning: No URLs were loaded. Ensure deployments.json is correctly formatted and contains URLs."
        )
    return urls


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    if (
        "url" in metafunc.fixturenames
        and metafunc.function.__name__ == "test_shiny_app_for_errors"
    ):
        test_urls = load_test_urls()
        metafunc.parametrize("url", test_urls)


@pytest.fixture(scope="session")
def playwright_instance() -> Generator[Playwright, None, None]:
    with sync_playwright() as playwright:
        yield playwright


@pytest.fixture(scope="function")
def browser_context(
    playwright_instance: Playwright,
) -> Generator[BrowserContext, None, None]:
    browser: Browser = playwright_instance.chromium.launch(headless=True)
    context: BrowserContext = browser.new_context(
        viewport={"width": 1280, "height": 800}
    )
    yield context
    context.close()
    browser.close()


@pytest.fixture(scope="function")
def page(browser_context: BrowserContext) -> Generator[Page, None, None]:
    test_page: Page = browser_context.new_page()
    yield test_page
    test_page.close()
