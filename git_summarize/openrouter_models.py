import os
import sys
import json
import requests
from typing import List, Optional
from pathlib import Path

CACHE_FILE = Path.home() / ".cache" / "git-summarize" / "openrouter_models.json"

def fetch_openrouter_models() -> List[str]:
    """Fetch available models from OpenRouter API."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OPENROUTER_API_KEY environment variable is not set")
        sys.exit(1)

    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    try:
        response = requests.get("https://openrouter.ai/api/v1/models", headers=headers)
        response.raise_for_status()
        models = response.json()
        return [f"openrouter/{model['id']}" for model in models['data']]
    except Exception as e:
        print(f"Error fetching models: {e}")
        return []

def cache_models(models: List[str]) -> None:
    """Cache the fetched models locally."""
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, 'w') as f:
        json.dump(models, f)

def load_cached_models() -> Optional[List[str]]:
    """Load models from cache if available."""
    if CACHE_FILE.exists():
        with open(CACHE_FILE) as f:
            return json.load(f)
    return None

def get_openrouter_models(refresh: bool = False) -> List[str]:
    """Get OpenRouter models, either from cache or by fetching."""
    if not refresh:
        cached_models = load_cached_models()
        if cached_models:
            return cached_models
    
    models = fetch_openrouter_models()
    if models:
        cache_models(models)
    return models
