# git_summarize/cli.py
from typing import Optional, List
import typer
from openai import OpenAI
import sys

from .ai_summarizer import summarize_with_openai
from .git_operations import check_unstaged_changes, stage_all_changes, get_git_diff, commit_changes
from .ai_client import setup_openai

# List of supported models
SUPPORTED_MODELS = [
    "gpt-3.5-turbo",
    "openrouter/nvidia/llama-3.1-nemotron-70b-instruct",
    "openrouter/qwen/qwen-2.5-72b-instruct",
    "openrouter/anthropic/claude-3.5-sonnet",
    "openrouter/deepseek/deepseek-chat",
    "openrouter/meta-llama/llama-3-70b-instruct",
    "openrouter/anthracite-org/magnum-v4-72b"
]

app = typer.Typer()

def print_models() -> None:
    """Print the list of supported models and exit."""
    print("\nSupported models:")
    for model in SUPPORTED_MODELS:
        print(f"- {model}")
    sys.exit(0)

@app.command()
def main(
    model: str = typer.Option("openrouter/qwen/qwen-2.5-72b-instruct", help="Model to use (default: gpt-3.5-turbo, for OpenRouter prefix with 'openrouter/')"),
    short: bool = typer.Option(False, "--short", "-s", help="Generate single-line commit message only"),
    stage_all: bool = typer.Option(False, "--stage-all", "-a", help="Automatically stage all unstaged changes"),
    list_models: bool = typer.Option(False, "--list-models", help="List all supported models and exit")
) -> None:
    """Main CLI command to summarize git changes and create commits."""
    if list_models:
        print_models()
        
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
