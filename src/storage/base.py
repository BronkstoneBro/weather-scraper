from abc import ABC, abstractmethod
from pathlib import Path

from src.models.weather import WeatherData


class BaseStorage(ABC):

    @abstractmethod
    async def save(self, weather_data: WeatherData, filename: str) -> Path:
        pass

    @abstractmethod
    async def load(self, filepath: Path) -> WeatherData:
        pass
