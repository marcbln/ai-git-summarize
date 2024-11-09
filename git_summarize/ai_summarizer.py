import json
from typing import Optional
from openai import OpenAI
from .prompts import PromptBuilder

def summarize_with_openai(
    client: OpenAI,
    diff_text: str,
    model: str = "gpt-3.5-turbo",
    short: bool = False
) -> Optional[str]:
    """Generate a commit message summary using OpenAI.
    
    Args:
        client: OpenAI client instance
        diff_text: Git diff text to summarize
        model: Name of the model to use (can include 'openrouter/' prefix)
        short: If True, generate a shorter summary
        
    Returns:
        str: Generated commit message summary if successful
        None: If API call fails or response is invalid
        
    The function includes extensive error checking and will return None if:
    - The API response is empty
    - The response is missing expected attributes
    - The response choices list is empty
    - Any API exception occurs
    
    Detailed error messages are printed to stdout for debugging.
    """
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
        
        # Log the full response for debugging
        print(f"\nFull API response: {response}")
        
        # Add defensive checks
        if not response:
            print("Error: Received empty response from API")
            return None
            
        if not hasattr(response, 'choices'):
            print("Error: Response missing 'choices' attribute")
            return None
            
        if not response.choices:
            print("Error: Response contains empty choices list")
            return None
            
        if not hasattr(response.choices[0], 'message'):
            print("Error: First choice missing 'message' attribute")
            return None
            
        if not hasattr(response.choices[0].message, 'content'):
            print("Error: Message missing 'content' attribute")
            return None
            
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"\nError when calling API: {type(e).__name__} - {str(e)}")
        if hasattr(e, 'response'):
            print(f"Response details: {e.response}")
        if hasattr(e, '__dict__'):
            print(f"Full error details: {e.__dict__}")
        return None
