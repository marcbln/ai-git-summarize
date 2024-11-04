import os
import sys
import json
import requests
from typing import List, Optional
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

CACHE_FILE = Path.home() / ".cache" / "git-summarize" / "openrouter_models.json"

def fetch_openrouter_models() -> List[str]:
    """Fetch available models from OpenRouter API."""
    console = Console()
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        console.print("[red]Error: OPENROUTER_API_KEY environment variable is not set[/red]")
        sys.exit(1)

    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task(description="Fetching models from OpenRouter...", total=None)
        try:
            response = requests.get("https://openrouter.ai/api/v1/models", headers=headers)
            response.raise_for_status()
            models = response.json()
            model_list = [f"openrouter/{model['id']}" for model in models['data']]
            console.print(f"[green]Successfully fetched {len(model_list)} models[/green]")
            return model_list
        except Exception as e:
            console.print(f"[red]Error fetching models: {e}[/red]")
            return []

def cache_models(models: List[str]) -> None:
    """Cache the fetched models locally."""
    console = Console()
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, 'w') as f:
        json.dump(models, f)
    console.print(f"[blue]Cached {len(models)} models to {CACHE_FILE}[/blue]")

def load_cached_models() -> Optional[List[str]]:
    """Load models from cache if available."""
    console = Console()
    if CACHE_FILE.exists():
        with open(CACHE_FILE) as f:
            models = json.load(f)
            console.print(f"[blue]Loaded {len(models)} models from cache[/blue]")
            return models
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
