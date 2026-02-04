import scrapy
from typing import Optional
from scrapy_playwright.page import PageMethod

from src.models.location import Location
from src.models.weather import WeatherData
from src.parsers.bbc_parser import BBCWeatherParser
from src.utils.config import settings
from src.utils.logger import logger


class BBCWeatherSpider(scrapy.Spider):
    name = "bbc_weather"

    custom_settings = {
        "PLAYWRIGHT_PROCESS_REQUEST_HEADERS": None,
    }

    def __init__(self, location: Optional[Location] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.location = location
        self.parser = BBCWeatherParser()

    def start_requests(self):
        if not self.location:
            logger.error("No location provided to spider")
            return

        url = settings.get_weather_url(self.location.location_id)

        logger.info(
            f"Starting scrape for {self.location.name} (ID: {self.location.location_id})"
        )

        yield scrapy.Request(
            url=url,
            callback=self.parse,
            meta={
                "playwright": True,
                "playwright_include_page": False,
                "playwright_page_methods": [
                    PageMethod("wait_for_timeout", settings.page_load_wait),
                ],
            },
            errback=self.errback_close_page,
        )

    def parse(self, response):
        try:
            html_content = response.text
            logger.debug(f"Retrieved HTML content ({len(html_content)} characters)")

            logger.info(f"Parsing weather data for {self.location.name}...")
            weather_data = self.parser.parse_html(html_content, self.location.name)

            weather_data.location_id = self.location.location_id
            weather_data.location_name = self.location.name

            logger.info(f"Successfully scraped weather for {self.location.name}")
            logger.debug(f"Found {len(weather_data.hourly_forecast)} hourly reports")

            yield weather_data

        except Exception as e:
            logger.error(f"Failed to parse weather data: {e}")
            raise

    def errback_close_page(self, failure):
        logger.error(f"Request failed: {failure.value}")
