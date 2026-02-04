# Weather Scraper

A weather data scraper for BBC Weather with dual engine support: BeautifulSoup and Scrapy.

## Features

- Two scraping engines: BS4 (lightweight) and Scrapy (scalable)
- 14-day forecast with hourly data (~330 records)
- Temperature, wind, humidity, pressure, precipitation
- Export to JSON and CSV
- 10 pre-configured UK cities
- Custom location ID support
- Performance benchmarking

## Installation

```bash
# Clone the repository
git clone https://github.com/BronkstoneBro/weather-scraper
cd weather-scraper

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium

# Copy config
cp .env.example .env
```

## Usage

```bash
# BeautifulSoup engine (default, faster for single requests)
python -m src.main --location London

# Scrapy engine (better for scaling)
python -m src.main --location London --engine scrapy

# Export to CSV
python -m src.main --location Manchester --format csv --engine bs4

# With page screenshot (BS4 only)
python -m src.main --location Edinburgh --screenshot

# Custom location ID
python -m src.main --location-id 2643743 --location-name "London"

# Performance benchmark
python benchmark.py

# Help
python -m src.main --help
```

### Available Cities

London, Manchester, Birmingham, Edinburgh, Glasgow, Cardiff, Liverpool, Bristol, Leeds, Sheffield

### Engine Comparison

| Engine | Speed (single location) | Use Case |
|--------|-------------------------|----------|
| **bs4** | ~7.2s                   | Single location, quick scrapes |
| **scrapy** | ~6.0s                   | Multiple locations, production |

## Configuration

Main parameters in `.env`:

```bash
HEADLESS=true              # Headless browser mode
BROWSER_TIMEOUT=45000      # Page load timeout (ms)
REQUESTS_PER_MINUTE=10     # Rate limit
STORAGE_TYPE=json          # json or csv
OUTPUT_DIR=data            # Output directory
LOG_LEVEL=INFO             # Logging level
```

## Project Structure

```
src/
├── main.py              # CLI entry point
├── models/              # Pydantic data models
├── parsers/             # HTML/JSON parsers (shared)
├── scrapers/
│   ├── factory.py       # Engine factory pattern
│   ├── bs4/             # BeautifulSoup scraper
│   └── scrapy_impl/     # Scrapy spider + pipeline
├── services/            # Browser service (Playwright)
├── storage/             # JSON/CSV export (shared)
└── utils/               # Config, logging, retry, rate limiter
```

## Tech Stack

- **Playwright** — browser automation
- **BeautifulSoup4** — HTML parsing (BS4 engine)
- **Scrapy** — web scraping framework (Scrapy engine)
- **Pydantic** — data validation
- **Loguru** — logging
- **Click** — CLI interface
- **Tenacity** — retry logic

## Architecture

Both engines share core components:
- **Parser**: `BBCWeatherParser` extracts JSON from HTML
- **Models**: Pydantic validation for weather data
- **Storage**: JSON/CSV exporters

Engine-specific:
- **BS4**: Direct Playwright integration via `BrowserService`
- **Scrapy**: Spider + Pipeline architecture with scrapy-playwright

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
