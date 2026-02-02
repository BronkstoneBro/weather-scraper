import json
from pathlib import Path
from datetime import datetime

from src.models.weather import WeatherData
from src.models.exceptions import StorageException
from src.utils.config import settings
from src.utils.logger import logger
from .base import BaseStorage


class JSONStorage(BaseStorage):

    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or settings.output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def save(self, weather_data: WeatherData, filename: str = None) -> Path:
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                location_name = weather_data.location_name or weather_data.location_id
                location_safe = location_name.lower().replace(" ", "_")
                filename = f"weather_{location_safe}_{timestamp}"

            if not filename.endswith(".json"):
                filename = f"{filename}.json"

            filepath = self.output_dir / filename
            data_dict = weather_data.model_dump(mode="json")
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data_dict, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"Weather data saved to: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Failed to save weather data to JSON: {e}")
            raise StorageException(f"JSON save failed: {str(e)}") from e

    async def load(self, filepath: Path) -> WeatherData:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data_dict = json.load(f)

            weather_data = WeatherData(**data_dict)
            logger.info(f"Weather data loaded from: {filepath}")
            return weather_data

        except Exception as e:
            logger.error(f"Failed to load weather data from JSON: {e}")
            raise StorageException(f"JSON load failed: {str(e)}") from e
