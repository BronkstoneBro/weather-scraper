from datetime import datetime, date, timezone
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class HourlyReport(BaseModel):
    # Time information
    local_date: date = Field(..., alias="localDate")
    timeslot: str = Field(..., description="Time in HH:MM format")
    timeslot_length: int = Field(
        ..., alias="timeslotLength", description="Duration in hours"
    )

    # Temperature
    temperature_c: int = Field(..., alias="temperatureC")
    temperature_f: int = Field(..., alias="temperatureF")
    feels_like_temperature_c: int = Field(..., alias="feelsLikeTemperatureC")
    feels_like_temperature_f: int = Field(..., alias="feelsLikeTemperatureF")

    # Weather description
    enhanced_weather_description: str = Field(..., alias="enhancedWeatherDescription")
    weather_type: int = Field(..., alias="weatherType")
    weather_type_text: str = Field(..., alias="weatherTypeText")
    extended_weather_type: int = Field(..., alias="extendedWeatherType")

    # Precipitation
    precipitation_probability_percent: int = Field(
        ..., alias="precipitationProbabilityInPercent"
    )
    precipitation_probability_text: str = Field(
        ..., alias="precipitationProbabilityText"
    )

    # Wind
    wind_speed_kph: int = Field(..., alias="windSpeedKph")
    wind_speed_mph: int = Field(..., alias="windSpeedMph")
    gust_speed_kph: int = Field(..., alias="gustSpeedKph")
    gust_speed_mph: int = Field(..., alias="gustSpeedMph")
    wind_direction: str = Field(
        ..., alias="windDirection", description="Abbreviation like ESE"
    )
    wind_direction_abbreviation: str = Field(..., alias="windDirectionAbbreviation")
    wind_direction_full: str = Field(..., alias="windDirectionFull")
    wind_description: str = Field(..., alias="windDescription")

    # Atmospheric conditions
    humidity: int = Field(..., ge=0, le=100, description="Humidity percentage")
    pressure: int = Field(..., description="Atmospheric pressure in millibars")
    visibility: str = Field(..., description="Visibility description")

    @field_validator("local_date", mode="before")
    @classmethod
    def parse_date(cls, v):
        if isinstance(v, str):
            return datetime.strptime(v, "%Y-%m-%d").date()
        return v

    class Config:
        populate_by_name = True


class DetailedForecast(BaseModel):

    issue_date: datetime = Field(..., alias="issueDate")
    last_updated: datetime = Field(..., alias="lastUpdated")
    reports: List[HourlyReport] = Field(default_factory=list)

    @field_validator("issue_date", "last_updated", mode="before")
    @classmethod
    def parse_datetime(cls, v):
        if isinstance(v, str):
            if v.endswith("Z"):
                v = v[:-1] + "+00:00"
            return datetime.fromisoformat(v)
        return v

    class Config:
        populate_by_name = True


class SummaryReport(BaseModel):

    local_date: date = Field(..., alias="localDate")
    temperature_c: Optional[int] = Field(None, alias="temperatureC")
    temperature_f: Optional[int] = Field(None, alias="temperatureF")
    enhanced_weather_description: Optional[str] = Field(
        None, alias="enhancedWeatherDescription"
    )
    weather_type_text: Optional[str] = Field(None, alias="weatherTypeText")
    wind_speed_kph: Optional[int] = Field(None, alias="windSpeedKph")
    wind_speed_mph: Optional[int] = Field(None, alias="windSpeedMph")
    humidity: Optional[int] = Field(None)
    pressure: Optional[int] = Field(None)
    visibility: Optional[str] = Field(None)

    @field_validator("local_date", mode="before")
    @classmethod
    def parse_date(cls, v):
        if isinstance(v, str):
            return datetime.strptime(v, "%Y-%m-%d").date()
        return v

    class Config:
        populate_by_name = True


class SummaryForecast(BaseModel):

    reports: List[SummaryReport] = Field(default_factory=list)

    class Config:
        populate_by_name = True


class DailyForecast(BaseModel):

    detailed: Optional[DetailedForecast] = None
    summary: Optional[SummaryForecast] = None

    class Config:
        populate_by_name = True


class ForecastData(BaseModel):

    forecasts: List[DailyForecast] = Field(default_factory=list)

    class Config:
        populate_by_name = True


class WeatherOptions(BaseModel):

    location_id: str = Field(..., alias="location_id")
    day: str = Field(default="none")
    locale: str = Field(default="en")

    class Config:
        populate_by_name = True


class BBCWeatherResponse(BaseModel):

    options: WeatherOptions
    data: ForecastData

    class Config:
        populate_by_name = True


class WeatherData(BaseModel):

    location_id: str
    location_name: Optional[str] = None
    last_updated: datetime
    current_conditions: Optional[HourlyReport] = None
    hourly_forecast: List[HourlyReport] = Field(default_factory=list)
    daily_summaries: List[SummaryReport] = Field(default_factory=list)

    class Config:
        populate_by_name = True

    @classmethod
    def from_bbc_response(
        cls, response: BBCWeatherResponse, location_name: Optional[str] = None
    ) -> "WeatherData":
        all_hourly_reports = []
        last_updated = None

        for forecast in response.data.forecasts:
            if forecast.detailed and forecast.detailed.reports:
                all_hourly_reports.extend(forecast.detailed.reports)
                if (
                    last_updated is None
                    or forecast.detailed.last_updated > last_updated
                ):
                    last_updated = forecast.detailed.last_updated

        if last_updated is None:
            last_updated = datetime.now(timezone.utc)

        daily_summaries = []
        for forecast in response.data.forecasts:
            if forecast.summary and forecast.summary.reports:
                daily_summaries.extend(forecast.summary.reports)

        current_conditions = all_hourly_reports[0] if all_hourly_reports else None

        return cls(
            location_id=response.options.location_id,
            location_name=location_name,
            last_updated=last_updated,
            current_conditions=current_conditions,
            hourly_forecast=all_hourly_reports,
            daily_summaries=daily_summaries,
        )
