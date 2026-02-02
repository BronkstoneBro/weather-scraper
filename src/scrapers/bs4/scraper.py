from typing import Optional
from playwright.async_api import Page

from src.models.weather import WeatherData
from src.models.location import Location
from src.models.exceptions import ScraperException
from src.services.browser_service import BrowserService
from src.parsers.bbc_parser import BBCWeatherParser
from src.utils.config import settings
from src.utils.logger import logger
from src.utils.rate_limiter import rate_limiter
from src.utils.retry import retry_on_browser_error
from ..base import BaseScraper


class BBCWeatherScraper(BaseScraper):
    def __init__(self):
        self.browser_service = BrowserService()
        self.parser = BBCWeatherParser()
        self._page: Optional[Page] = None

    async def initialize(self):
        try:
            logger.info("Initializing BBC Weather scraper...")
            await self.browser_service.initialize()
            logger.info("Scraper initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize scraper: {e}")
            raise ScraperException(f"Scraper initialization failed: {str(e)}") from e

    @retry_on_browser_error(max_attempts=3)
    async def scrape(self, location: Location) -> WeatherData:
        if not self.browser_service.is_initialized:
            raise ScraperException("Scraper not initialized. Call initialize() first.")

        try:
            await rate_limiter.acquire()

            url = settings.get_weather_url(location.location_id)
            logger.info(
                f"Scraping weather for {location.name} (ID: {location.location_id})"
            )

            page = await self.browser_service.new_page()
            self._page = page

            try:
                await self.browser_service.goto(page, url)

                title = await page.title()
                logger.debug(f"Page title: {title}")

                html_content = await self.browser_service.get_content(page)
                logger.debug(f"Retrieved HTML content ({len(html_content)} characters)")

                logger.info("Parsing weather data...")
                weather_data = self.parser.parse_html(html_content, location.name)

                weather_data.location_id = location.location_id
                weather_data.location_name = location.name

                logger.info(f"Successfully scraped weather for {location.name}")
                logger.debug(
                    f"Found {len(weather_data.hourly_forecast)} hourly reports"
                )

                return weather_data

            finally:
                await self.browser_service.close_page(page)
                self._page = None

        except Exception as e:
            logger.error(f"Failed to scrape weather for {location.name}: {e}")
            raise ScraperException(
                f"Scraping failed for {location.name}: {str(e)}"
            ) from e

    async def take_screenshot(self, path: str):
        if self._page:
            await self.browser_service.take_screenshot(self._page, path)

    async def cleanup(self):
        logger.info("Cleaning up scraper...")
        await self.browser_service.cleanup()
        logger.info("Scraper cleanup complete")
