# git_summarize/cli.py
import typer
from .client import setup_openai
from .git import get_git_diff, commit_changes, check_unstaged_changes, stage_all_changes
from .summarizer import summarize_with_openai

app = typer.Typer()

@app.command()
def main(
    model: str = typer.Option("openrouter/qwen/qwen-2.5-72b-instruct", help="Model to use (default: gpt-3.5-turbo, for OpenRouter prefix with 'openrouter/')"),
    short: bool = typer.Option(False, "--short", "-s", help="Generate single-line commit message only"),
    stage_all: bool = typer.Option(False, "--stage-all", "-a", help="Automatically stage all unstaged changes")
):
    """Main CLI command to summarize git changes and create commits."""
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
