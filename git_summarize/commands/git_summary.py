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
from ..git_operations import (
    check_unstaged_changes,
    stage_all_changes,
    get_git_diff,
    commit_changes,
    push_changes
)
from ..openrouter_models import get_openrouter_models


def main(
    model: str = typer.Option(
        "openrouter/qwen/qwen-2.5-coder-32b-instruct",
        "--model",
        "-m",
        help="Model ID to use for generating commit messages. For OpenRouter models, prefix with 'openrouter/'. Use --list-models to see available options."
    ),
    strategy: str = typer.Option(
        "ai",
        "--strategy",
        "-s",
        help="Commit message strategy: 'ai' (auto-detect format), 'short' (force one-line), 'detailed' (force multi-line)"
    ),
    stage_all: bool = typer.Option(False, "--stage-all", "-a", help="Automatically stage all unstaged changes"),
    push: bool = typer.Option(False, "--push", "-p", help="Automatically push changes after commit without asking for confirmation"),
    always_accept_commit_message: bool = typer.Option(False, "--always-accept-commit-message", "-y",
                                                      help="Skip confirmation prompt and accept suggested commit message"),
) -> None:
    """Summarize git changes and create commits (git-summary)."""
    console = Console()

    console.print(Panel(f"Starting git-summarize with model: [cyan]{model}[/cyan]", 
                       style="bold green"))
    client = setup_openai(model)
    ai_summarizer = AISummarizer(client)

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
            model=model,
            strategy=strategy
        )
        if commit_message:
            console.print("\n[bold]Suggested commit message:[/bold]")
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
