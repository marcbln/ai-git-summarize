from ..app import app
import os
import sys
import inquirer
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from typing import Optional
from ..ai_client import setup_openai
from ..ai_summarizer import AISummarizer
from ..retry_utils import RetryConfig
from ..git_operations import (
    check_unstaged_changes,
    stage_all_changes,
    get_git_diff,
    commit_changes,
    push_changes
)
from ..openrouter_models import get_openrouter_models


@app.command()
def git_summary(
    model: str = typer.Option(
        "openrouter/minimax/minimax-m2:free",
        "--model",
        "-m",
        help="Model ID or alias to use for generating commit messages. For OpenRouter models, prefix with 'openrouter/'. "
             "Short aliases (e.g., 'claude35', 'geminiflash20-free') can be used and will be resolved using config/model-aliases.yaml."
    ),
    strategy: str = typer.Option(
        "ai",
        "--strategy",
        "-s",
        help="Commit message strategy: 'ai' (let ai decide the format), 'short' (one-line), 'detailed' (multi-line)"
    ),
    stage_all: bool = typer.Option(False, "--stage-all", "-a", help="Automatically stage all unstaged changes"),
    push: bool = typer.Option(False, "--push", "-p", help="Automatically push changes after commit without asking for confirmation"),
    always_accept_commit_message: bool = typer.Option(False, "--always-accept-commit-message", "-y",
                                                     help="Skip confirmation prompt and accept suggested commit message"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Test mode: only resolve model alias and print info without making git operations"),
    retries: int = typer.Option(5, "--retries", help="Number of retry attempts for API calls (default: 5)."),
    min_wait: int = typer.Option(2, "--min-wait", help="Minimum wait time in seconds between retries (default: 2)."),
    max_wait: int = typer.Option(10, "--max-wait", help="Maximum wait time in seconds between retries (default: 10)."),
) -> None:
    """Summarize git changes and create commits (git-summary)."""
    console = Console()

    console.print(Panel(f"Starting git-summarize with model: [cyan]{model}[/cyan]",
                       style="bold green"))
    
    # Import the necessary functions from config_utils
    from ..config_utils import resolve_model_alias, UnknownModelAliasError, get_available_aliases
    
    try:
        # Try to resolve the model alias, raising an exception if it's unknown
        resolved_model = resolve_model_alias(model, raise_on_unknown=True)
        
        # If dry_run is True, just test the model alias resolution
        if dry_run:
            if resolved_model != model:
                console.print(f"\n[bold green]Model alias resolved:[/bold green] [cyan]{model}[/cyan] -> [yellow]{resolved_model}[/yellow]")
            else:
                console.print(f"\n[bold]Using model:[/bold] [yellow]{model}[/yellow]")
            console.print("\n[bold blue]Dry run completed.[/bold blue] No git operations were performed.")
            return
    except UnknownModelAliasError:
        # Get the available aliases
        aliases = get_available_aliases()
        
        # Print an error message
        console.print(f"\n[bold red]Error:[/bold red] Unknown model alias: [cyan]{model}[/cyan]")
        
        # Print the list of available aliases
        if aliases:
            console.print("\n[bold]Available model aliases:[/bold]")
            
            # Create a table to display the aliases
            table = Table(title="Model Aliases", show_header=True, header_style="bold magenta")
            table.add_column("Alias", style="cyan")
            table.add_column("Full Model Identifier", style="green")
            
            # Add rows to the table
            for alias, full_id in sorted(aliases.items()):
                table.add_row(alias, full_id)
            
            console.print(table)
        else:
            console.print("\n[yellow]No model aliases found in config/model-aliases.yaml[/yellow]")
        
        # Exit with an error code
        sys.exit(1)
        
    client = setup_openai(resolved_model)
    retry_config = RetryConfig(max_retries=retries, min_wait=min_wait, max_wait=max_wait)
    ai_summarizer = AISummarizer(client, retry_config=retry_config)

    # Check for unstaged changes
    has_unstaged, unstaged_diff = check_unstaged_changes()
    if has_unstaged:
        console.print("\n[yellow]Found unstaged changes![/yellow]")
        if stage_all:
            print("Staging all changes...")
            stage_all_changes()
        else:
            questions = [
                inquirer.Confirm('stage',
                    message="Would you like to stage these changes?",
                    default=False
                ),
            ]
            answers = inquirer.prompt(questions)
            if answers and answers['stage']:
                stage_all_changes()

    diff_text = get_git_diff()
    
    if diff_text:
        commit_message = ai_summarizer.summarize_changes(
            diff_text,
            model=resolved_model,
            strategy=strategy
        )
        if commit_message:
            console.print(f"\n[bold]Suggested commit message (from {resolved_model}, strategy: {strategy}):[/bold]")
            console.print(Panel(commit_message, border_style="green"))

            if always_accept_commit_message:
                messageApproved = True
            else:
                questions = [
                    inquirer.Confirm('commit',
                        message="Use this message for commit?",
                        default=True
                    ),
                ]
                answers = inquirer.prompt(questions)
                messageApproved = answers and answers['commit']

            if messageApproved:
                if commit_changes(commit_message):
                    if push:
                        push_changes()
                    else:
                        questions = [
                            inquirer.Confirm('push',
                                message="Would you like to push these changes?",
                                default=False
                            ),
                        ]
                        push_answers = inquirer.prompt(questions)
                        if push_answers and push_answers['push']:
                            push_changes()
        else:
            console.print("[red]Failed to generate commit message using API.[/red]")
    else:
        console.print("[yellow]No changes to summarize.[/yellow]")
