from abc import ABC, abstractmethod
from typing import Optional

from src.models.weather import WeatherData, BBCWeatherResponse


class BaseParser(ABC):

    @abstractmethod
    def parse_html(
        self, html_content: str, location_name: Optional[str] = None
    ) -> WeatherData:
        pass

    @abstractmethod
    def extract_json(self, html_content: str) -> BBCWeatherResponse:
        pass

    def validate_response(self, response: BBCWeatherResponse) -> bool:
        if not response.data.forecasts:
            return False

        has_data = any(
            forecast.detailed and forecast.detailed.reports
            for forecast in response.data.forecasts
        )

        return has_data
