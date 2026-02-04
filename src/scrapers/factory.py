from typing import Literal, Optional

from .base import BaseScraper
from .bs4.scraper import BBCWeatherScraper
from .scrapy_impl.scraper import ScrapyWeatherScraper


def create_scraper(
    engine: Literal["bs4", "scrapy"] = "bs4",
    storage_format: str = "json",
    output_filename: Optional[str] = None,
) -> BaseScraper:

    if engine == "bs4":
        return BBCWeatherScraper()
    elif engine == "scrapy":
        return ScrapyWeatherScraper(
            storage_format=storage_format, output_filename=output_filename
        )
    else:
        raise ValueError(
            f"Unknown scraper engine: {engine}. Supported engines: 'bs4', 'scrapy'"
        )
