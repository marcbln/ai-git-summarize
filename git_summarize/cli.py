# git_summarize/cli.py
import os
import sys

import typer

from rich.console import Console
from rich.table import Table
from git_summarize.openrouter_models import get_openrouter_models, format_pricing


from .ai_client import setup_openai
from .ai_summarizer import summarize_with_openai
from .git_operations import check_unstaged_changes, stage_all_changes, get_git_diff, commit_changes

app = typer.Typer()

def print_models(refresh: bool = False) -> None:
    """Print the list of supported models and exit."""
    console = Console()
    table = Table(title="Available Models with Pricing")
    table.add_column("Model ID")
    table.add_column("Name")
    table.add_column("Pricing")

    openrouter_models = get_openrouter_models(refresh)
    if not openrouter_models:
        console.print("[yellow]No OpenRouter models available[/yellow]")
        return

    for model in openrouter_models:
        if isinstance(model, str):
            # Skip if model is just a string
            continue
        try:
            model_id = f"openrouter/{model['id']}"
            name = model.get('name', 'Unknown')
            pricing = format_pricing(model['pricing'])
            table.add_row(model_id, name, pricing)
        except (KeyError, TypeError):
            continue
    
    console = Console()
    console.print(table)
    sys.exit(0)

@app.command()
def main(
    model: str = typer.Option("openrouter/qwen/qwen-2.5-72b-instruct", help="Model to use (default: gpt-3.5-turbo, for OpenRouter prefix with 'openrouter/')"),
    short: bool = typer.Option(False, "--short", "-s", help="Generate single-line commit message only"),
    stage_all: bool = typer.Option(False, "--stage-all", "-a", help="Automatically stage all unstaged changes"),
    list_models: bool = typer.Option(False, "--list-models", help="List all supported models and exit"),
    refresh_openrouter_models: bool = typer.Option(False, "--refresh-openrouter-models", help="Refresh the cached OpenRouter models list and exit")
) -> None:
    """Main CLI command to summarize git changes and create commits."""

    if list_models:
        print_models(refresh_openrouter_models)
        sys.exit(0)

    if refresh_openrouter_models:
        print("Refreshing OpenRouter models...")
        from .openrouter_models import cache_models
        openrouter_models = get_openrouter_models(True)
        sys.exit(0)

    print(f"\nStarting git-summarize with model: {model}")
    client = setup_openai(model)
    
    # Check for unstaged changes
    has_unstaged, unstaged_diff = check_unstaged_changes()
    if has_unstaged:
        print("\nFound unstaged changes!")
        if stage_all:
            stage_all_changes()
        else:
            response = input("Would you like to stage these changes? [y/N]: ").lower()
            if response == 'y':
                stage_all_changes()
    
    diff_text = get_git_diff()
    
    if diff_text:
        commit_message = summarize_with_openai(client, diff_text, model=model, short=short)
        if commit_message:
            print("\nSuggested commit message:")
            print("-" * 40)
            print(commit_message)
            print("-" * 40)
            
            response = input("\nUse this message for commit? [y/N]: ").lower()
            if response == 'y':
                commit_changes(commit_message)
        else:
            print("Failed to generate commit message using API.")
    else:
        print("No changes to summarize.")

if __name__ == "__main__":
    app()
