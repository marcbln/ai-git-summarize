import typer
from rich.console import Console
from rich.table import Table
from ..openrouter_models import get_openrouter_models, format_pricing

app = typer.Typer()

@app.command()
def list(refresh: bool = False):
    """List all available OpenRouter models with pricing"""
    models = get_openrouter_models(refresh=refresh)
    console = Console()
    
    table = Table(title="OpenRouter Models")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Provider", style="green")
    table.add_column("Context", justify="right")
    table.add_column("Pricing", justify="right")
    
    for model in models:
        table.add_row(
            model['id'],
            model['name'],
            f"{model['top_provider']['context_length']} ctx",
            str(model['context_length']),
            format_pricing(model['pricing'])
        )
    
    console.print(table)

@app.command()
def list_ids(refresh: bool = False):
    """List only OpenRouter model IDs"""
    models = get_openrouter_models(refresh=refresh)
    for model in models:
        print(model['id'])

@app.command()
def refresh():
    """Refresh the OpenRouter models cache"""
    get_openrouter_models(refresh=True)
    print("OpenRouter models cache refreshed")