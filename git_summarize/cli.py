# git_summarize/cli.py
import os
import sys
import inquirer
import typer
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.style import Style
from git_summarize.openrouter_models import get_openrouter_models, format_pricing


import yaml
from pathlib import Path
from typing import Dict, List, Any
from .ai_client import setup_openai
from .ai_summarizer import AISummarizer
from .git_operations import (
    check_unstaged_changes, stage_all_changes, get_git_diff,
    commit_changes, push_changes, get_commit_messages,
    get_commit_diff # <-- Import the new function
)
from .commands.feedback import feedback
from .commands.git_summary import main as git_summary_main
from .commands.summarize_history import summarize_history as summarize_history_command
from .commands.generate_report import generate_report as generate_report_command
from .commands.openrouter import app as openrouter_app

# Define valid strategies
VALID_STRATEGIES = ["ai", "short", "detailed"]

app = typer.Typer()
app.add_typer(openrouter_app, name="openrouter", help="Manage OpenRouter models")

@app.command(name="git-feedback")
def feedback():
    """Generate code quality feedback for uncommitted changes"""
    from .commands.feedback import feedback as feedback_command
    feedback_command()

@app.command(name="git-summary", context_settings={"help_option_names": ["-h", "--help"]})
def git_summary(
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
):
    """Summarize git changes and create commits"""
    from .commands.git_summary import main as git_summary_command
    git_summary_command(model, strategy, stage_all, push, always_accept_commit_message)

@app.command()
def summarize_history(
    range: str = typer.Argument("HEAD~7..HEAD", help="Git commit range"),
    model: str = typer.Option(
        "openrouter/qwen/qwen-2.5-coder-32b-instruct",
        help="Model ID to use for generating commit summaries"
    ),
    output: str = typer.Option(
        "text",
        help="Output format (text, json, markdown)"
    ),
    detail: str = typer.Option(
        "technical",
        help="Detail level (technical, non-technical, overview)"
    )
) -> None:
    """Summarize a range of git commits"""
    from .commands.summarize_history import summarize_history as summarize_history_command
    summarize_history_command(range, model, output, detail)

@app.command()
def generate_report(
    group: str = typer.Option(..., "--group", "-g", help="Project group to analyze"),
    start_date: str = typer.Option(..., "--start-date", "-s", help="Start date (YYYY-MM-DD)"),
    end_date: str = typer.Option(..., "--end-date", "-e", help="End date (YYYY-MM-DD)"),
    output_format: str = typer.Option("markdown", "--output-format", "-o",
                                   help="Output format (markdown, json, text)")
) -> None:
    """Generate work report for a project group between dates"""
    from .commands.generate_report import generate_report as generate_report_command
    generate_report_command(group, start_date, end_date, output_format)


@app.command(name="git-analyze-commit")
def analyze_commit(
    commit_ref: str = typer.Argument("HEAD", help="Commit reference (hash, tag, HEAD, HEAD~N) to analyze"),
    model: str = typer.Option(
        "openrouter/qwen/qwen-2.5-coder-32b-instruct",
        "--model",
        "-m",
        help="Model ID to use for analysis. Prefix with 'openrouter/' for OpenRouter models."
    ),
):
    """Analyze a specific commit's changes for potential risks using AI."""
    console = Console()
    
    console.print(Panel(f"Analyzing commit: [bold cyan]{commit_ref}[/]", title="Commit Analysis", expand=False))

    # Setup AI Client
    try:
        # Pass the model argument to setup_openai
        client = setup_openai(model)
        if not client:
            console.print("[bold red]Error:[/bold red] Failed to set up AI client. Check API key and configuration.")
            raise typer.Exit(code=1)
        summarizer = AISummarizer(client)
    except Exception as e:
        console.print(f"[bold red]Error setting up AI client:[/bold red] {e}")
        raise typer.Exit(code=1)

    # Get the diff for the specified commit
    diff_text = get_commit_diff(commit_ref)

    if diff_text is None:
        console.print(f"[bold red]Error:[/bold red] Could not retrieve diff for commit '{commit_ref}'. Is it a valid reference?")
        raise typer.Exit(code=1)
    
    if not diff_text:
        console.print(Panel(f"No textual changes found for commit [bold cyan]{commit_ref}[/]. Nothing to analyze.", title="Analysis Result", border_style="yellow"))
        raise typer.Exit()

    # Analyze the commit impact
    try:
        analysis_result = summarizer.analyze_commit_impact(
            diff_text=diff_text,
            model=model,
            commit_ref=commit_ref # Pass the reference for context fetching
        )
    except Exception as e:
         console.print(f"[bold red]Error during AI analysis:[/bold red] {e}")
         raise typer.Exit(code=1)


    if analysis_result:
        # Determine panel style based on result
        border_style = "green" if "Clean Refactoring" in analysis_result else "red" if "Potential Risk" in analysis_result else "yellow"
        console.print(Panel(analysis_result, title="Analysis Result", border_style=border_style, expand=False))
    else:
        console.print("[bold red]Error:[/bold red] Failed to get analysis from AI.")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
