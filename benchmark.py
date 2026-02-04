import asyncio
import time
from pathlib import Path

from src.constants.locations import get_location
from src.scrapers.factory import create_scraper
from src.utils.logger import logger


async def benchmark_engine(engine: str, location_name: str) -> dict:
    location = get_location(location_name)
    if not location:
        raise ValueError(f"Location not found: {location_name}")

    scraper = create_scraper(
        engine=engine, storage_format="json", output_filename=f"bench_{engine}"
    )

    start_time = time.perf_counter()

    async with scraper:
        weather_data = await scraper.scrape(location)

    end_time = time.perf_counter()

    elapsed = end_time - start_time

    return {
        "engine": engine,
        "location": location_name,
        "time_seconds": round(elapsed, 2),
        "forecasts_count": len(weather_data.hourly_forecast),
    }


async def run_benchmark():
    print("\n" + "=" * 60)
    print("BBC Weather Scraper - Performance Benchmark")
    print("=" * 60 + "\n")

    test_location = "London"

    print(f"Testing with location: {test_location}\n")

    results = []

    print("Running BeautifulSoup scraper...")
    bs4_result = await benchmark_engine("bs4", test_location)
    results.append(bs4_result)
    print(f"  [OK] Completed in {bs4_result['time_seconds']}s\n")

    print("Running Scrapy scraper...")
    scrapy_result = await benchmark_engine("scrapy", test_location)
    results.append(scrapy_result)
    print(f"  [OK] Completed in {scrapy_result['time_seconds']}s\n")

    print("=" * 60)
    print("Results:")
    print("=" * 60)
    print(f"{'Engine':<15} {'Time (s)':<12} {'Forecasts':<12}")
    print("-" * 60)

    for result in results:
        print(
            f"{result['engine']:<15} {result['time_seconds']:<12} {result['forecasts_count']:<12}"
        )

    print("-" * 60)

    bs4_time = bs4_result["time_seconds"]
    scrapy_time = scrapy_result["time_seconds"]

    if bs4_time < scrapy_time:
        faster = "BeautifulSoup"
        diff = ((scrapy_time - bs4_time) / bs4_time) * 100
    else:
        faster = "Scrapy"
        diff = ((bs4_time - scrapy_time) / scrapy_time) * 100

    print(f"\n{faster} is faster by {diff:.1f}%")
    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(run_benchmark())
