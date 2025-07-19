import time
import logging
from dataclasses import dataclass, field
from typing import List, Callable, Any, TypeVar

# Configure logging
logger = logging.getLogger(__name__)

T = TypeVar('T')

@dataclass
class RetryConfig:
    """Configuration for retry mechanism."""
    max_retries: int = 5
    min_wait: int = 2  # seconds
    max_wait: int = 10  # seconds
    retryable_status_codes: List[int] = field(default_factory=lambda: [429, 503, 504])

def linear_backoff(attempt: int, config: RetryConfig) -> float:
    """Calculate wait time using linear backoff."""
    if config.max_retries <= 1:
        return config.min_wait
    
    step = (config.max_wait - config.min_wait) / (config.max_retries - 1)
    wait_time = config.min_wait + (attempt * step)
    return min(wait_time, config.max_wait)

def with_retry(config: RetryConfig, retryable_exceptions: tuple) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """A decorator for retrying a function with linear backoff."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            for attempt in range(config.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    if attempt >= config.max_retries:
                        logger.error(f"Final attempt failed. No more retries left.")
                        break

                    wait_time = linear_backoff(attempt, config)
                    logger.warning(
                        f"Attempt {attempt + 1}/{config.max_retries + 1} failed with {e}. "
                        f"Retrying in {wait_time:.2f} seconds..."
                    )
                    time.sleep(wait_time)
                except Exception as e:
                    logger.error(f"An non-retryable error occurred: {e}")
                    raise e

            raise last_exception
        return wrapper
    return decorator
