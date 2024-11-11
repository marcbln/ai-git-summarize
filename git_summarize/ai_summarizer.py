import json
from typing import Optional, Dict, Any
from openai import OpenAI
from .prompts import PromptBuilder


class AISummarizer:
    """Class to handle AI-powered code summarization and feedback."""
    
    def __init__(self, client: OpenAI):
        """Initialize with an OpenAI client instance."""
        self.client = client

    def _prepare_api_kwargs(self, messages: list, model: str, max_tokens: int = 100) -> Dict[str, Any]:
        """Prepare kwargs for API call based on model type."""
        if model.startswith("openrouter/"):
            actual_model = model.replace("openrouter/", "", 1)
            print(f"Using OpenRouter with model: {actual_model}")
            kwargs = {
                "extra_headers": {
                    "X-Title": "ai-git-summarize",
                },
                "model": actual_model,
                "messages": messages,
            }
        else:
            kwargs = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens
            }
        print(f"API configuration:\n{json.dumps(kwargs, indent=2)}")
        return kwargs

    def _make_api_call(self, kwargs: Dict[str, Any]) -> Optional[str]:
        """Make API call with error handling and response validation."""
        try:
            print("\nSending API request...")
            response = self.client.chat.completions.create(**kwargs)
            print("Successfully received API response")
            print(f"\nFull API response: {response}")

            # Validate response
            if (not response or not hasattr(response, 'choices') or
                not response.choices or not hasattr(response.choices[0], 'message') or
                not hasattr(response.choices[0].message, 'content')):
                print("Error: Invalid API response structure")
                return None

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"\nError when calling API: {type(e).__name__} - {str(e)}")
            if hasattr(e, 'response'):
                print(f"Response details: {e.response}")
            if hasattr(e, '__dict__'):
                print(f"Full error details: {e.__dict__}")
            return None

    def generate_code_feedback(self, diff_text: str, model: str) -> Optional[str]:
        """Generate code quality feedback using AI.
        
        Args:
            diff_text: Git diff text to analyze
            model: Name of the model to use (can include 'openrouter/' prefix)
            
        Returns:
            str: Generated feedback if successful
            None: If API call fails
        """
        print(f"\nGenerating feedback using model: {model}")
        messages = PromptBuilder.build_feedback_prompt(diff_text)
        kwargs = self._prepare_api_kwargs(messages, model, max_tokens=300)
        return self._make_api_call(kwargs)

    def summarize_changes(self, diff_text: str, model: str = "gpt-3.5-turbo",
                         short: bool = False) -> Optional[str]:
        """Generate a commit message summary using AI.
        
        Args:
            diff_text: Git diff text to summarize
            model: Name of the model to use (can include 'openrouter/' prefix)
            short: If True, generate a shorter summary
            
        Returns:
            str: Generated commit message summary if successful
            None: If API call fails or response is invalid
        """
        print(f"\nGenerating summary using model: {model}")
        messages = (PromptBuilder.build_short_diff_prompt(diff_text) if short
                   else PromptBuilder.build_diff_prompt(diff_text))
        print(f"Generated prompt with {len(messages)} messages")
        
        kwargs = self._prepare_api_kwargs(messages, model)
        return self._make_api_call(kwargs)
