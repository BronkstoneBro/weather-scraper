"""
Retry decorators and utilities using tenacity
"""

from functools import wraps
from typing import Callable, Type, Tuple
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    after_log,
)
from playwright._impl._errors import TimeoutError as PlaywrightTimeoutError

from .config import settings
from .logger import logger


def retry_on_exception(
    exception_types: Tuple[Type[Exception], ...] = (Exception,),
    max_attempts: int = None,
    initial_wait: float = None,
    backoff: float = None,
) -> Callable:
    max_attempts = max_attempts or settings.max_retry_attempts
    initial_wait = initial_wait or settings.retry_initial_wait
    backoff = backoff or settings.retry_backoff

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=initial_wait, max=60, exp_base=backoff),
            retry=retry_if_exception_type(exception_types),
            before_sleep=before_sleep_log(logger, log_level="WARNING"),
            after=after_log(logger, log_level="DEBUG"),
            reraise=True,
        )
        async def async_wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        @wraps(func)
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=initial_wait, max=60, exp_base=backoff),
            retry=retry_if_exception_type(exception_types),
            before_sleep=before_sleep_log(logger, log_level="WARNING"),
            after=after_log(logger, log_level="DEBUG"),
            reraise=True,
        )
        def sync_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def retry_on_browser_error(max_attempts: int = 3) -> Callable:
    return retry_on_exception(
        exception_types=(
            PlaywrightTimeoutError,
            TimeoutError,
            ConnectionError,
        ),
        max_attempts=max_attempts,
    )


def retry_on_parse_error(max_attempts: int = 2) -> Callable:
    from src.models.exceptions import ParserException, DataExtractionException

    return retry_on_exception(
        exception_types=(ParserException, DataExtractionException),
        max_attempts=max_attempts,
    )
