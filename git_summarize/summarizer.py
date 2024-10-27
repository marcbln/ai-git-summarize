import json
from openai import OpenAI
from .prompt_builder import PromptBuilder

def summarize_with_openai(client: OpenAI, diff_text: str, model: str = "gpt-3.5-turbo", short: bool = False) -> str | None:
    """Generate a commit message summary using OpenAI."""
    print(f"\nGenerating summary using model: {model}")
    try:
        messages = (PromptBuilder.build_short_diff_prompt(diff_text) if short 
                   else PromptBuilder.build_diff_prompt(diff_text))
        print(f"Generated prompt with {len(messages)} messages")
        
        # Add OpenRouter specific headers if using OpenRouter
        if model.startswith("openrouter/"):
            # Remove the "openrouter/" prefix for the actual API call
            actual_model = model.replace("openrouter/", "", 1)
            print(f"Using OpenRouter with model: {actual_model}")
            kwargs = {
                "extra_headers": {
                    "X-Title": "ai-git-summarize",
                },
                "model": actual_model,
                "messages": messages,
            }
            print("Using OpenRouter configuration:")
            print(json.dumps(kwargs, indent=2))
        else:
            kwargs = {
                "model": model,
                "messages": messages,
                "max_tokens": 100
            }
            print("Using OpenAI configuration:")
            print(json.dumps(kwargs, indent=2))
            
        print("\nSending API request...")
        response = client.chat.completions.create(**kwargs)
        print("Successfully received API response")
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"\nError when calling API: {type(e).__name__} - {str(e)}")
        if hasattr(e, 'response'):
            print(f"Response details: {e.response}")
        return None
