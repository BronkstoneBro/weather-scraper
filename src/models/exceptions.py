class WeatherScraperException(Exception):
    """Base exception for weather scraper"""

    pass


class ScraperException(WeatherScraperException):
    """Exception raised during scraping process"""

    pass


class ParserException(WeatherScraperException):
    """Exception raised during parsing process"""

    pass


class BrowserException(WeatherScraperException):
    """Exception raised during browser operations"""

    pass


class StorageException(WeatherScraperException):
    """Exception raised during storage operations"""

    pass


class LocationNotFoundException(WeatherScraperException):
    """Exception raised when location is not found"""

    pass


class DataExtractionException(ParserException):
    """Exception raised when data extraction fails"""

    pass


class ValidationException(WeatherScraperException):
    """Exception raised when data validation fails"""

    pass
