from abc import ABC, abstractmethod
from typing import Optional

from src.models.weather import WeatherData
from src.models.location import Location


class BaseScraper(ABC):

    @abstractmethod
    async def initialize(self):
        pass

    @abstractmethod
    async def scrape(self, location: Location) -> WeatherData:
        pass

    @abstractmethod
    async def cleanup(self):
        pass

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()
