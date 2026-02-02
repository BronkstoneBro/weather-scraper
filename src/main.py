import asyncio
import sys
from pathlib import Path
from typing import Optional
import argparse

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


def parse_args():
    parser = argparse.ArgumentParser(
        description="BBC Weather Scraper - Scrape weather data from BBC Weather",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape weather for London (save as JSON)
  python -m src.main --location London

  # Scrape and save as CSV
  python -m src.main --location Manchester --format csv

  # Scrape with custom output filename
  python -m src.main --location Edinburgh --output my_weather

  # Scrape with screenshot
  python -m src.main --location London --screenshot

  # Use custom location ID
  python -m src.main --location-id 2643743 --location-name "London"

Available locations:
  London, Manchester, Birmingham, Edinburgh, Glasgow, Cardiff,
  Liverpool, Bristol, Leeds, Sheffield
        """,
    )

    parser.add_argument(
        "--location",
        type=str,
        help="Location name (e.g., 'London', 'Manchester')",
    )

    parser.add_argument(
        "--location-id",
        type=str,
        help="BBC Weather location ID (alternative to --location)",
    )

    parser.add_argument(
        "--location-name",
        type=str,
        help="Location display name (used with --location-id)",
    )

    parser.add_argument(
        "--format",
        choices=["json", "csv"],
        default="json",
        help="Output format (default: json)",
    )

    parser.add_argument(
        "--output", type=str, help="Custom output filename (without extension)"
    )

    parser.add_argument(
        "--screenshot",
        action="store_true",
        help="Save screenshot of the weather page",
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)",
    )

    parser.add_argument(
        "--headless",
        type=lambda x: x.lower() in ["true", "1", "yes"],
        default=True,
        help="Run browser in headless mode (default: true)",
    )

    return parser.parse_args()


async def main():
    args = parse_args()

    if args.log_level:
        settings.log_level = args.log_level

    if args.headless is not None:
        settings.headless = args.headless

    try:
        location = None

        if args.location_id:
            location_name = args.location_name or args.location_id
            location = Location(location_id=args.location_id, name=location_name)
            logger.info(
                f"Using custom location ID: {args.location_id} ({location_name})"
            )

        elif args.location:
            location = get_location(args.location)
            if not location:
                logger.error(f"Location not found: {args.location}")
                logger.info(
                    "Available locations: London, Manchester, Birmingham, Edinburgh, Glasgow, Cardiff, Liverpool, Bristol, Leeds, Sheffield"
                )
                sys.exit(1)

        else:
            logger.error("Please specify either --location or --location-id")
            sys.exit(1)

        output_path = await scrape_weather(
            location=location,
            output_format=args.format,
            output_file=args.output,
            screenshot=args.screenshot,
        )

        print("\n" + "=" * 60)
        print(f"[SUCCESS] Weather data scraped for {location.name}")
        print(f"[OUTPUT] Saved to: {output_path}")
        print("=" * 60)

        return 0

    except WeatherScraperException as e:
        logger.error(f"Scraping failed: {e}")
        print(f"\n[ERROR] {e}", file=sys.stderr)
        return 1

    except KeyboardInterrupt:
        logger.warning("Scraping interrupted by user")
        print("\n[INTERRUPTED] Cancelled by user", file=sys.stderr)
        return 130

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        print(f"\n[ERROR] Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
