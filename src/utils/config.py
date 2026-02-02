from pathlib import Path
from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    headless: bool = Field(default=True, description="Run browser in headless mode")
    browser_timeout: int = Field(
        default=45000, description="Browser operation timeout in ms"
    )
    page_load_wait: int = Field(
        default=3000, description="Additional wait after page load in ms"
    )

    user_agent: str = Field(
        default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        description="User agent string for requests",
    )
    viewport_width: int = Field(default=1920, description="Browser viewport width")
    viewport_height: int = Field(default=1080, description="Browser viewport height")
    locale: str = Field(default="en-GB", description="Browser locale")
    timezone: str = Field(default="Europe/London", description="Browser timezone")

    requests_per_minute: int = Field(
        default=10, description="Maximum requests per minute"
    )
    request_delay: float = Field(
        default=6.0, description="Delay between requests in seconds"
    )

    max_retry_attempts: int = Field(
        default=3, description="Maximum number of retry attempts"
    )
    retry_backoff: float = Field(
        default=2.0, description="Exponential backoff multiplier for retries"
    )
    retry_initial_wait: float = Field(
        default=1.0, description="Initial wait time for retry in seconds"
    )

    storage_type: Literal["json", "csv"] = Field(
        default="json", description="Default storage type"
    )
    output_dir: Path = Field(
        default=Path("data"), description="Output directory for scraped data"
    )

    log_level: str = Field(default="INFO", description="Logging level")
    log_file: Path = Field(
        default=Path("logs/weather_scraper.log"), description="Log file path"
    )
    log_rotation: str = Field(default="10 MB", description="Log rotation size")
    log_retention: str = Field(default="1 week", description="Log retention period")
    log_format: str = Field(
        default="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        description="Log format string",
    )

    bbc_weather_base_url: str = Field(
        default="https://www.bbc.com/weather", description="BBC Weather base URL"
    )

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    def get_weather_url(self, location_id: str) -> str:
        return f"{self.bbc_weather_base_url}/{location_id}"

    def ensure_directories(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)


settings = Settings()

settings.ensure_directories()
