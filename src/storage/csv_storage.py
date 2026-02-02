import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict

from src.models.weather import WeatherData, HourlyReport
from src.models.exceptions import StorageException
from src.utils.config import settings
from src.utils.logger import logger
from .base import BaseStorage


class CSVStorage(BaseStorage):

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

            if not filename.endswith(".csv"):
                filename = f"{filename}.csv"

            filepath = self.output_dir / filename

            rows = self._flatten_hourly_reports(weather_data)

            if not rows:
                raise StorageException("No hourly forecast data to save")

            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)

            logger.info(f"Weather data saved to: {filepath} ({len(rows)} rows)")
            return filepath

        except Exception as e:
            logger.error(f"Failed to save weather data to CSV: {e}")
            raise StorageException(f"CSV save failed: {str(e)}") from e

    def _flatten_hourly_reports(self, weather_data: WeatherData) -> List[Dict]:
        rows = []

        for report in weather_data.hourly_forecast:
            row = {
                # Location info
                "location_id": weather_data.location_id,
                "location_name": weather_data.location_name,
                "last_updated": weather_data.last_updated.isoformat(),
                # Time info
                "date": report.local_date.isoformat(),
                "time": report.timeslot,
                # Temperature
                "temp_c": report.temperature_c,
                "temp_f": report.temperature_f,
                "feels_like_c": report.feels_like_temperature_c,
                "feels_like_f": report.feels_like_temperature_f,
                # Weather
                "description": report.enhanced_weather_description,
                "weather_type": report.weather_type_text,
                # Precipitation
                "precip_probability": report.precipitation_probability_percent,
                # Wind
                "wind_speed_kph": report.wind_speed_kph,
                "wind_speed_mph": report.wind_speed_mph,
                "gust_speed_kph": report.gust_speed_kph,
                "gust_speed_mph": report.gust_speed_mph,
                "wind_direction": report.wind_direction,
                "wind_description": report.wind_description,
                # Atmospheric
                "humidity": report.humidity,
                "pressure": report.pressure,
                "visibility": report.visibility,
            }
            rows.append(row)

        return rows

    async def load(self, filepath: Path) -> WeatherData:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            if not rows:
                raise StorageException("CSV file is empty")

            first_row = rows[0]

            hourly_reports = []
            for row in rows:
                report = HourlyReport(
                    localDate=row["date"],
                    timeslot=row["time"],
                    timeslotLength=1,
                    temperatureC=int(row["temp_c"]),
                    temperatureF=int(row["temp_f"]),
                    feelsLikeTemperatureC=int(row["feels_like_c"]),
                    feelsLikeTemperatureF=int(row["feels_like_f"]),
                    enhancedWeatherDescription=row["description"],
                    weatherType=0,
                    weatherTypeText=row["weather_type"],
                    extendedWeatherType=0,
                    precipitationProbabilityInPercent=int(row["precip_probability"]),
                    precipitationProbabilityText="",
                    windSpeedKph=int(row["wind_speed_kph"]),
                    windSpeedMph=int(row["wind_speed_mph"]),
                    gustSpeedKph=int(row["gust_speed_kph"]),
                    gustSpeedMph=int(row["gust_speed_mph"]),
                    windDirection=row["wind_direction"],
                    windDirectionAbbreviation=row["wind_direction"],
                    windDirectionFull="",
                    windDescription=row["wind_description"],
                    humidity=int(row["humidity"]),
                    pressure=int(row["pressure"]),
                    visibility=row["visibility"],
                )
                hourly_reports.append(report)

            weather_data = WeatherData(
                location_id=first_row["location_id"],
                location_name=first_row["location_name"],
                last_updated=datetime.fromisoformat(first_row["last_updated"]),
                current_conditions=hourly_reports[0] if hourly_reports else None,
                hourly_forecast=hourly_reports,
            )

            logger.info(f"Weather data loaded from: {filepath}")
            return weather_data

        except Exception as e:
            logger.error(f"Failed to load weather data from CSV: {e}")
            raise StorageException(f"CSV load failed: {str(e)}") from e
