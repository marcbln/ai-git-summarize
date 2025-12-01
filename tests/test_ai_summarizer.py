import pytest
from unittest.mock import MagicMock, patch
from openai import RateLimitError, APIError, APIStatusError
from ai_git.ai_summarizer import AISummarizer
from ai_git.retry_utils import RetryConfig

@pytest.mark.parametrize("input_text,expected", [
    # Triple backticks
    ("```python\nprint('hello')\n```", "print('hello')"),
    ("```\nsimple text\n```", "simple text"),
    
    # Single backticks
    ("`single line`", "single line"),
    
    # Mixed/weird cases
    ("`` `middle` ``", "`middle`"),
    ("```\n```\ncontent\n```\n```", "content"),
    
    # Standalone backtick lines
    ("Line1\n```\nLine2\n````\nLine3", "Line1\nLine2\nLine3"),
    
    # No backticks
    ("Clean text", "Clean text"),
    
    # Edge cases
    ("", None),
    (None, None),
])
def test_strip_backticks(input_text, expected):
    summarizer = AISummarizer(None)  # Pass None as client since we're not using it
    assert summarizer._strip_backticks(input_text) == expected


@pytest.fixture
def mock_openai_client():
    return MagicMock()


def test_successful_retry(mock_openai_client):
    """Test that the API call succeeds after a few retries."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Successful response"

    # Simulate two failures then a success
    mock_openai_client.chat.completions.create.side_effect = [
        RateLimitError("Too many requests", response=MagicMock(), body=None),
        APIStatusError("Service Unavailable", response=MagicMock(status_code=503), body=None),
        mock_response
    ]

    retry_config = RetryConfig(max_retries=3, min_wait=0.01, max_wait=0.01)
    summarizer = AISummarizer(mock_openai_client, retry_config=retry_config)

    with patch('time.sleep', return_value=None) as mock_sleep:
        result = summarizer._make_api_call(kwargs={"model": "test-model", "messages": []})

        assert result == "Successful response"
        assert mock_openai_client.chat.completions.create.call_count == 3
        assert mock_sleep.call_count == 2


def test_failed_retry_after_exhausting_attempts(mock_openai_client):
    """Test that the API call fails after all retries are exhausted."""
    mock_openai_client.chat.completions.create.side_effect = RateLimitError(
        "Too many requests", response=MagicMock(), body=None
    )

    retry_config = RetryConfig(max_retries=2, min_wait=0.01, max_wait=0.01)
    summarizer = AISummarizer(mock_openai_client, retry_config=retry_config)

    with patch('time.sleep', return_value=None) as mock_sleep:
        result = summarizer._make_api_call(kwargs={"model": "test-model", "messages": []})

        assert result is None
        # 1 initial call + 2 retries = 3 total calls
        assert mock_openai_client.chat.completions.create.call_count == 3
        assert mock_sleep.call_count == 2


def test_non_retryable_error_fails_immediately(mock_openai_client):
    """Test that a non-retryable error is not retried."""
    # 400 Bad Request is not in the default retryable status codes
    mock_openai_client.chat.completions.create.side_effect = APIStatusError(
        "Bad Request", response=MagicMock(status_code=400), body=None
    )

    retry_config = RetryConfig(max_retries=3, min_wait=0.01, max_wait=0.01)
    summarizer = AISummarizer(mock_openai_client, retry_config=retry_config)

    with patch('time.sleep', return_value=None) as mock_sleep:
        # The decorator catches the exception and logs it, then returns None.
        # It does not re-raise the exception.
        result = summarizer._make_api_call(kwargs={"model": "test-model", "messages": []})

        assert result is None
        assert mock_openai_client.chat.completions.create.call_count == 1
        assert mock_sleep.call_count == 0


def test_summarize_changes_forces_newline(mock_openai_client):
    """Test that missing blank line between subject and body is inserted programmatically."""
    # Mock the OpenAI client to return a malformed commit message (missing blank line)
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "feat: add new feature\n- implemented feature X\n- added tests"

    mock_openai_client.chat.completions.create.return_value = mock_response

    retry_config = RetryConfig(max_retries=3, min_wait=0.01, max_wait=0.01)
    summarizer = AISummarizer(mock_openai_client, retry_config=retry_config)

    # Call summarize_changes with a dummy diff and strategy
    result = summarizer.summarize_changes("dummy diff text", "test-model", "detailed")

    # Assert that the returned string has the blank line inserted
    expected = "feat: add new feature\n\n- implemented feature X\n- added tests"
    assert result == expected
