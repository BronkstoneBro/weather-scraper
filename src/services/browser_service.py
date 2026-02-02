from typing import Optional
from playwright.async_api import (
    async_playwright,
    Browser,
    BrowserContext,
    Page,
    Playwright,
)

from src.utils.config import settings
from src.utils.logger import logger
from src.models.exceptions import BrowserException


class BrowserService:
    def __init__(self):
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._initialized = False

    async def initialize(self):
        if self._initialized:
            logger.debug("Browser service already initialized")
            return

        try:
            logger.info("Initializing browser service...")

            self._playwright = await async_playwright().start()

            self._browser = await self._playwright.chromium.launch(
                headless=settings.headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                ],
            )

            logger.info(f"Browser launched (headless={settings.headless})")

            self._context = await self._browser.new_context(
                viewport={
                    "width": settings.viewport_width,
                    "height": settings.viewport_height,
                },
                user_agent=settings.user_agent,
                locale=settings.locale,
                timezone_id=settings.timezone,
                extra_http_headers={
                    "Accept-Language": f"{settings.locale},en;q=0.9",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                },
            )

            logger.debug(
                f"Browser context created (locale={settings.locale}, timezone={settings.timezone})"
            )

            self._initialized = True
            logger.info("Browser service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize browser service: {e}")
            await self.cleanup()
            raise BrowserException(f"Browser initialization failed: {str(e)}") from e

    async def new_page(self) -> Page:
        if not self._initialized or not self._context:
            raise BrowserException(
                "Browser service not initialized. Call initialize() first."
            )

        try:
            page = await self._context.new_page()
            logger.debug("New page created")
            return page

        except Exception as e:
            logger.error(f"Failed to create new page: {e}")
            raise BrowserException(f"Page creation failed: {str(e)}") from e

    async def goto(
        self,
        page: Page,
        url: str,
        wait_until: str = "domcontentloaded",
        timeout: Optional[int] = None,
    ) -> None:
        timeout = timeout or settings.browser_timeout

        try:
            logger.info(f"Navigating to: {url}")
            response = await page.goto(url, wait_until=wait_until, timeout=timeout)

            if response:
                logger.debug(f"Response status: {response.status}")

            # Additional wait for dynamic content
            if settings.page_load_wait > 0:
                logger.debug(
                    f"Waiting {settings.page_load_wait}ms for dynamic content..."
                )
                await page.wait_for_timeout(settings.page_load_wait)

            logger.info("Navigation completed successfully")

        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            raise BrowserException(f"Failed to navigate to {url}: {str(e)}") from e

    async def get_content(self, page: Page) -> str:
        try:
            content = await page.content()
            logger.debug(f"Retrieved HTML content ({len(content)} characters)")
            return content

        except Exception as e:
            logger.error(f"Failed to get page content: {e}")
            raise BrowserException(f"Content extraction failed: {str(e)}") from e

    async def take_screenshot(
        self, page: Page, path: str, full_page: bool = False
    ) -> None:
        try:
            await page.screenshot(path=path, full_page=full_page)
            logger.debug(f"Screenshot saved to: {path}")

        except Exception as e:
            logger.warning(f"Failed to take screenshot: {e}")

    async def close_page(self, page: Page):
        try:
            await page.close()
            logger.debug("Page closed")

        except Exception as e:
            logger.warning(f"Failed to close page: {e}")

    async def cleanup(self):
        logger.info("Cleaning up browser service...")

        try:
            if self._context:
                await self._context.close()
                logger.debug("Browser context closed")

            if self._browser:
                await self._browser.close()
                logger.debug("Browser closed")

            if self._playwright:
                await self._playwright.stop()
                logger.debug("Playwright stopped")

        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")

        finally:
            self._context = None
            self._browser = None
            self._playwright = None
            self._initialized = False
            logger.info("Browser service cleanup complete")

    @property
    def is_initialized(self) -> bool:
        return self._initialized

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()
