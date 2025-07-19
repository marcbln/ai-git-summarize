import pytest
from ai_git.retry_utils import RetryConfig, linear_backoff


def test_linear_backoff_calculation():
    config = RetryConfig(max_retries=5, min_wait=2, max_wait=10)
    # step = (10 - 2) / (5 - 1) = 2
    assert linear_backoff(0, config) == 2  # min_wait + 0 * 2
    assert linear_backoff(1, config) == 4  # min_wait + 1 * 2
    assert linear_backoff(2, config) == 6  # min_wait + 2 * 2
    assert linear_backoff(3, config) == 8  # min_wait + 3 * 2
    assert linear_backoff(4, config) == 10 # min_wait + 4 * 2
    assert linear_backoff(5, config) == 10 # capped at max_wait

def test_linear_backoff_single_retry():
    config = RetryConfig(max_retries=1, min_wait=5, max_wait=5)
    assert linear_backoff(0, config) == 5
    assert linear_backoff(1, config) == 5

def test_linear_backoff_no_retries():
    config = RetryConfig(max_retries=0, min_wait=3, max_wait=3)
    assert linear_backoff(0, config) == 3

def test_retry_config_defaults():
    config = RetryConfig()
    assert config.max_retries == 5
    assert config.min_wait == 2
    assert config.max_wait == 10
    assert config.retryable_status_codes == [429, 503, 504]
