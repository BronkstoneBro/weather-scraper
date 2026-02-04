from datetime import datetime
from typing import Optional

from src.models.weather import WeatherData
from src.storage.json_storage import JSONStorage
from src.storage.csv_storage import CSVStorage
from src.utils.logger import logger


class StoragePipeline:
    def __init__(self):
        self.json_storage = JSONStorage()
        self.csv_storage = CSVStorage()
        self.storage_format: Optional[str] = None
        self.output_filename: Optional[str] = None

    def open_spider(self, spider):
        self.storage_format = getattr(spider, "storage_format", "json")
        self.output_filename = getattr(spider, "output_filename", None)

        logger.info(
            f"Storage pipeline initialized with format: {self.storage_format}"
        )

    async def process_item(self, item: WeatherData, spider):
        try:
            if not self.output_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                location_slug = item.location_name.lower().replace(" ", "_")
                self.output_filename = f"weather_{location_slug}_{timestamp}"

            if self.storage_format == "csv":
                filepath = await self.csv_storage.save(item, self.output_filename)
            else:
                filepath = await self.json_storage.save(item, self.output_filename)

            logger.info(f"Saved weather data to: {filepath}")

            return item

        except Exception as e:
            logger.error(f"Failed to save weather data: {e}")
            raise

    def close_spider(self, spider):
        logger.info("Storage pipeline closed")
