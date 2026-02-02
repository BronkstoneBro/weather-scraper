import asyncio
import sys
from pathlib import Path
from typing import Optional

import click

from src.models.location import get_location, Location
from src.models.exceptions import WeatherScraperException
from src.scrapers.bs4.scraper import BBCWeatherScraper
from src.storage.json_storage import JSONStorage
from src.storage.csv_storage import CSVStorage
from src.utils.logger import logger
from src.utils.config import settings


async def scrape_weather(
    location: Location,
    output_format: str = "json",
    output_file: Optional[str] = None,
    screenshot: bool = False,
) -> Path:
    logger.info(f"Starting weather scrape for {location.name}")

    async with BBCWeatherScraper() as scraper:
        weather_data = await scraper.scrape(location)

        if screenshot and scraper._page:
            screenshot_path = (
                settings.output_dir
                / f"screenshot_{location.name.lower().replace(' ', '_')}.png"
            )
            await scraper.take_screenshot(str(screenshot_path))
            logger.info(f"Screenshot saved to: {screenshot_path}")

    if output_format == "json":
        storage = JSONStorage()
    elif output_format == "csv":
        storage = CSVStorage()
    else:
        raise ValueError(f"Invalid output format: {output_format}")

    saved_path = await storage.save(weather_data, output_file)

    logger.info(f"Weather data saved to: {saved_path}")
    logger.info(f"Scraped {len(weather_data.hourly_forecast)} hourly forecasts")

    return saved_path


LOCATIONS = "London, Manchester, Birmingham, Edinburgh, Glasgow, Cardiff, Liverpool, Bristol, Leeds, Sheffield"


@click.command()
@click.option("-l", "--location", help="Location name (e.g., London, Manchester)")
@click.option("--location-id", help="BBC Weather location ID")
@click.option("--location-name", help="Display name (used with --location-id)")
@click.option("-f", "--format", "output_format", default="json", type=click.Choice(["json", "csv"]), help="Output format")
@click.option("-o", "--output", help="Custom output filename (without extension)")
@click.option("-s", "--screenshot", is_flag=True, help="Save page screenshot")
@click.option("--log-level", default="INFO", type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]), help="Logging level")
@click.option("--headless/--no-headless", default=True, help="Run browser in headless mode")
def main(location, location_id, location_name, output_format, output, screenshot, log_level, headless):

    settings.log_level = log_level
    settings.headless = headless

    try:
        loc = None

        if location_id:
            name = location_name or location_id
            loc = Location(location_id=location_id, name=name)
            logger.info(f"Using custom location ID: {location_id} ({name})")

        elif location:
            loc = get_location(location)
            if not loc:
                logger.error(f"Location not found: {location}")
                click.echo(f"Available: {LOCATIONS}", err=True)
                sys.exit(1)

        else:
            click.echo("Error: specify --location or --location-id", err=True)
            sys.exit(1)

        output_path = asyncio.run(
            scrape_weather(
                location=loc,
                output_format=output_format,
                output_file=output,
                screenshot=screenshot,
            )
        )

        click.echo("")
        click.echo(f"[SUCCESS] Weather data scraped for {loc.name}")
        click.echo(f"[OUTPUT] Saved to: {output_path}")


    except WeatherScraperException as e:
        logger.error(f"Scraping failed: {e}")
        click.echo(f"\n[ERROR] {e}", err=True)
        sys.exit(1)

    except KeyboardInterrupt:
        logger.warning("Scraping interrupted by user")
        click.echo("\n[INTERRUPTED] Cancelled by user", err=True)
        sys.exit(130)


if __name__ == "__main__":
    main()
