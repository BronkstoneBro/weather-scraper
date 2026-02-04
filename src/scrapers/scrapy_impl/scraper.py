import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional
import scrapy.signals
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from src.models.weather import WeatherData
from src.models.location import Location
from src.models.exceptions import ScraperException
from src.utils.logger import logger
from ..base import BaseScraper
from .spiders.bbc_spider import BBCWeatherSpider


class ScrapyWeatherScraper(BaseScraper):
    def __init__(self, storage_format: str = "json", output_filename: Optional[str] = None):
        self.storage_format = storage_format
        self.output_filename = output_filename
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.collected_items = []

    async def initialize(self):
        try:
            logger.info("Initializing Scrapy weather scraper...")
            logger.info("Scrapy scraper initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Scrapy scraper: {e}")
            raise ScraperException(f"Scraper initialization failed: {str(e)}") from e

    async def scrape(self, location: Location) -> WeatherData:
        try:
            logger.info(f"Starting Scrapy scrape for {location.name}")

            self.collected_items = []

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor, self._run_spider, location
            )

            if result:
                logger.info(f"Successfully scraped weather for {location.name}")
                return result
            else:
                raise ScraperException("No data collected from spider")

        except Exception as e:
            logger.error(f"Failed to scrape weather for {location.name}: {e}")
            raise ScraperException(
                f"Scraping failed for {location.name}: {str(e)}"
            ) from e

    def _run_spider(self, location: Location) -> Optional[WeatherData]:
        settings = get_project_settings()
        settings.setmodule("src.scrapers.scrapy_impl.settings")

        process = CrawlerProcess(settings)

        spider_cls = BBCWeatherSpider
        spider_cls.storage_format = self.storage_format
        spider_cls.output_filename = self.output_filename

        def collect_item(item, response, spider):
            self.collected_items.append(item)

        crawler = process.create_crawler(spider_cls)
        crawler.signals.connect(collect_item, signal=scrapy.signals.item_scraped)

        process.crawl(crawler, location=location)
        process.start()

        return self.collected_items[0] if self.collected_items else None

    async def cleanup(self):
        logger.info("Cleaning up Scrapy scraper...")
        self.executor.shutdown(wait=True)
        logger.info("Scrapy scraper cleanup complete")
