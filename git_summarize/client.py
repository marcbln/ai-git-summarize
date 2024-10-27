import os
import sys
import json
from openai import OpenAI

def setup_openai(model: str):
    """Setup and return an OpenAI client based on the model type."""
    print(f"\nSetting up client for model: {model}")
    if model.startswith("openrouter/"):
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            print("Error: OPENROUTER_API_KEY environment variable is not set")
            sys.exit(1)
        print("Using OpenRouter API endpoint with base url https://openrouter.ai/api/v1")
        return OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
    else:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("Error: OPENAI_API_KEY environment variable is not set")
            sys.exit(1)
        print("Using OpenAI API endpoint")
        return OpenAI(api_key=api_key)
