from playwright.sync_api import Page, expect

PAGE_LOAD_TIMEOUT = 60_000
SHINY_INIT_TIMEOUT = 30_000
ERROR_ELEMENT_TIMEOUT = 1_000
POST_INIT_WAIT = 5_000


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

        page.evaluate("""
            async () => {
                return window.Shiny.initializedPromise;
            }
            """)

    except Exception as e:
        error_msg = f"Shiny initialization failed or timed out for {page.url}: {str(e)}"
        raise AssertionError(error_msg)


def detect_errors_in_page(page: Page, url: str) -> None:
    expect(page.locator(".shiny-busy")).to_have_count(0, timeout=SHINY_INIT_TIMEOUT)
    error_locator = page.locator(".shiny-output-error")
    expect(error_locator).to_have_count(0, timeout=ERROR_ELEMENT_TIMEOUT)


def test_shiny_app_for_errors(page: Page, url: str) -> None:
    page.goto(url, timeout=PAGE_LOAD_TIMEOUT)
    # Wait for shiny to init
    wait_for_shiny_initialization(page, timeout=SHINY_INIT_TIMEOUT)
    # Wait too long for output to load
    page.wait_for_timeout(POST_INIT_WAIT)
    detect_errors_in_page(page, url=url)
