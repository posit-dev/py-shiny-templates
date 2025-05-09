from typing import Any, Dict

import pytest
from playwright.sync_api import Page

PAGE_LOAD_TIMEOUT = 60000
SHINY_INIT_TIMEOUT = 30000
ERROR_ELEMENT_TIMEOUT = 1000
POST_INIT_WAIT = 3000


def wait_for_shiny_initialization(
    page: Page, timeout: int = SHINY_INIT_TIMEOUT
) -> None:
    """Wait for Shiny app to complete initialization.

    Args:
            page: Playwright Page object
            timeout: Maximum time to wait in milliseconds

    Raises:
            AssertionError: If initialization fails or times out
    """
    try:
        init_check = (
            "() => window.Shiny && "
            "(window.Shiny.initializedPromise && "
            "typeof window.Shiny.initializedPromise.then === 'function')"
        )
        page.wait_for_function(init_check, timeout=timeout)

        result = page.evaluate(
            """
            async () => {
                if (!window.Shiny) {
                    return { success: false, error: 'Shiny not found' };
                }
                if (
                    window.Shiny.initializedPromise &&
                    typeof window.Shiny.initializedPromise.then === 'function'
                ) {
                    try {
                        await window.Shiny.initializedPromise;
                        return { success: true };
                    } catch (e) {
                        return { success: false, error: e.message || 'Promise rejected' };
                    }
                }
                return { success: false, error: 'Shiny not properly initialized' };
            }
            """
        )

        if not result.get("success", False):
            error = result.get("error", "Unknown error during Shiny initialization")
            raise AssertionError(f"Shiny initialization failed for {page.url}: {error}")

    except Exception as e:
        error_msg = f"Shiny initialization failed or timed out for {page.url}: {str(e)}"
        raise AssertionError(error_msg)


def detect_errors_in_page(page: Page) -> Dict[str, Any]:
    error_locator = page.locator(".shiny-output-error")
    total_errors_found = error_locator.count()
    critical_count = 0
    for i in range(total_errors_found):
        element = error_locator.nth(i)
        try:
            if not element.is_visible(timeout=ERROR_ELEMENT_TIMEOUT):
                continue
            text_content = element.text_content()
            text = (text_content or "").strip().lower()
            if text and "placeholder" not in text:
                critical_count += 1
        except Exception:
            continue
    return {"total_found_on_page": total_errors_found, "critical": critical_count}


def test_shiny_app_for_errors(page: Page, url: str) -> None:
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=PAGE_LOAD_TIMEOUT)
        wait_for_shiny_initialization(page, timeout=SHINY_INIT_TIMEOUT)
        page.wait_for_timeout(POST_INIT_WAIT)
        error_data = detect_errors_in_page(page)
        assert error_data["critical"] == 0, (
            f"Found {error_data['critical']} critical error(s) (out of {error_data['total_found_on_page']} potential errors) "
            f"on {url}."
        )
    except Exception as e:
        pytest.fail(f"Test failed for URL {url}: {str(e)}")
