from src.utils.config import settings as app_settings

BOT_NAME = "weather_scraper"

SPIDER_MODULES = ["src.scrapers.scrapy_impl.spiders"]
NEWSPIDER_MODULE = "src.scrapers.scrapy_impl.spiders"

ROBOTSTXT_OBEY = False

CONCURRENT_REQUESTS = 1

DOWNLOAD_DELAY = app_settings.request_delay

DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

PLAYWRIGHT_BROWSER_TYPE = "chromium"

PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": app_settings.headless,
    "args": ["--disable-blink-features=AutomationControlled"],
}

PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = app_settings.browser_timeout

PLAYWRIGHT_CONTEXTS = {
    "default": {
        "viewport": {
            "width": app_settings.viewport_width,
            "height": app_settings.viewport_height,
        },
        "user_agent": app_settings.user_agent,
        "locale": app_settings.locale,
        "timezone_id": app_settings.timezone,
    }
}

RETRY_TIMES = app_settings.max_retry_attempts
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

DOWNLOADER_MIDDLEWARES = {
    "scrapy.downloadermiddlewares.retry.RetryMiddleware": None,
    "scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware": 810,
}

ITEM_PIPELINES = {
    "src.scrapers.scrapy_impl.pipelines.storage_pipeline.StoragePipeline": 300,
}

LOG_LEVEL = app_settings.log_level

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
FEED_EXPORT_ENCODING = "utf-8"
