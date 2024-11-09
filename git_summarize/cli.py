# git_summarize/cli.py
import os
import sys

import typer

from rich.console import Console
from rich.table import Table
from git_summarize.openrouter_models import get_openrouter_models, format_pricing


from .ai_client import setup_openai
from .ai_summarizer import summarize_with_openai
from .git_operations import check_unstaged_changes, stage_all_changes, get_git_diff, commit_changes, push_changes

app = typer.Typer()

def display_models_table(refresh: bool = False) -> None:
    """Print a detailed table of supported models with their pricing information.
    
    Args:
        refresh (bool): If True, force refresh of cached model data before displaying.
                       Default is False.
    """
    console = Console()
    table = Table(title="Available Models with Pricing")
    table.add_column("Model ID", no_wrap=True)
    table.add_column("Context", no_wrap=True)
    table.add_column("Input", no_wrap=True)
    table.add_column("Output", no_wrap=True)

    openrouter_models = get_openrouter_models(refresh)
    if not openrouter_models:
        console.print("[yellow]No OpenRouter models available[/yellow]")
        return

    # Convert models to list of tuples for sorting
    model_rows = []
    for model in openrouter_models:
        if isinstance(model, str):
            # Skip if model is just a string
            continue
        try:
            model_id = f"openrouter/{model['id']}"
            context, input_price, output_price = format_pricing(model)
            model_rows.append((model_id, context, input_price, output_price))
        except (KeyError, TypeError):
            continue
    
    # Sort rows by model ID and add to table
    for model_id, context, input_price, output_price in sorted(model_rows, key=lambda x: x[0].lower()):
        table.add_row(model_id, context, input_price, output_price)
    
    console = Console()
    console.print(table)
    sys.exit(0)

@app.command()
def main(
    model: str = typer.Option(
        "openrouter/qwen/qwen-2.5-72b-instruct", 
        help="Model ID to use for generating commit messages. For OpenRouter models, prefix with 'openrouter/'. Use --list-models to see available options."
    ),
    short: bool = typer.Option(False, "--short", "-s", help="Generate single-line commit message only"),
    stage_all: bool = typer.Option(False, "--stage-all", "-a", help="Automatically stage all unstaged changes"),
    print_models_table: bool = typer.Option(False, "--print-models-table", help="Print detailed table of all supported models and exit"),
    list_models: bool = typer.Option(False, "--list-models", help="List model IDs only and exit"),
    refresh_openrouter_models: bool = typer.Option(False, "--refresh-openrouter-models", help="Refresh the cached OpenRouter models list and exit"),
    push: bool = typer.Option(False, "--push", "-p", help="Automatically push changes after commit without asking for confirmation")
) -> None:
    """Main CLI command to summarize git changes and create commits."""

    if print_models_table:
        display_models_table(refresh_openrouter_models)
        sys.exit(0)

    if list_models:
        openrouter_models = get_openrouter_models(refresh_openrouter_models)
        if not openrouter_models:
            print("No OpenRouter models available")
            sys.exit(0)
        model_ids = []
        for model in openrouter_models:
            if isinstance(model, str):
                continue
            try:
                model_ids.append(f"openrouter/{model['id']}")
            except (KeyError, TypeError):
                continue
        for model_id in sorted(model_ids, key=str.lower):
            print(model_id)
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
                if commit_changes(commit_message):
                    if push:
                        push_changes()
                    else:
                        push_response = input("\nWould you like to push these changes? [y/N]: ").lower()
                        if push_response == 'y':
                            push_changes()
        else:
            print("Failed to generate commit message using API.")
    else:
        print("No changes to summarize.")

if __name__ == "__main__":
    app()
