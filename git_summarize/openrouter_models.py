import os
import sys
import json
import requests
from typing import List, Optional, Dict, Any

ModelData = Dict[str, Any]
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

CACHE_FILE = Path.home() / ".cache" / "git-summarize" / "openrouter_models.json"

def fetch_openrouter_models() -> List[ModelData]:
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
            model_list = models['data']
            console.print(f"[green]Successfully fetched {len(model_list)} models[/green]")
            return model_list
        except Exception as e:
            console.print(f"[red]Error fetching models: {e}[/red]")
            return []

def cache_models(models: List[ModelData]) -> None:
    """Cache the fetched models locally."""
    console = Console()
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, 'w') as f:
        json.dump(models, f)
    console.print(f"[blue]Cached {len(models)} models to {CACHE_FILE}[/blue]")

def load_cached_models() -> Optional[List[ModelData]]:
    """Load models from cache if available."""
    console = Console()
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE) as f:
                models = json.load(f)
                if isinstance(models, list) and all(isinstance(m, dict) for m in models):
                    console.print(f"[blue]Loaded {len(models)} models from cache[/blue]")
                    return models
                else:
                    console.print("[yellow]Invalid cache format, refreshing...[/yellow]")
                    return None
        except json.JSONDecodeError:
            console.print("[yellow]Invalid cache file, refreshing...[/yellow]")
            return None
    return None

def get_openrouter_models(refresh: bool = False) -> List[ModelData]:
    """Get OpenRouter models, either from cache or by fetching."""
    if not refresh:
        cached_models = load_cached_models()
        if cached_models:
            return cached_models
    
    models = fetch_openrouter_models()
    if models:
        cache_models(models)
    return models

def format_pricing(model_data: Dict[str, Any]) -> tuple[str, str, str]:
    """Format pricing information for display.
    
    Args:
        model_data: Complete model data dictionary from OpenRouter API
    
    Returns:
        tuple: (context_length, input_price, output_price)
    """
    pricing = model_data.get('pricing', {})
    prompt_price = float(pricing.get('prompt', '0'))
    completion_price = float(pricing.get('completion', '0'))
    
    # Get context length and format it
    context_length = model_data.get('context_length', 0)
    if context_length >= 1000000:
        context_str = f"{context_length//1000000}M"
    elif context_length >= 1000:
        context_str = f"{context_length//1000}K"
    else:
        context_str = str(context_length)

    # Convert to per million tokens and format prices
    prompt_price_m = prompt_price * 1_000_000  # Convert to per million
    completion_price_m = completion_price * 1_000_000  # Convert to per million
    
    return (
        context_str,
        f"${prompt_price_m:.2f}/M",
        f"${completion_price_m:.2f}/M"
    )
