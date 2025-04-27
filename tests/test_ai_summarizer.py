import pytest
from ai_git.ai_summarizer import AISummarizer

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
