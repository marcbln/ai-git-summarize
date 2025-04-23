import os
import sys
import inquirer
from rich.console import Console
from rich.panel import Panel
from typer import Option
from ..ai_client import setup_openai
from ..ai_summarizer import AISummarizer
from ..git_operations import check_unstaged_changes, stage_all_changes, get_git_diff

def feedback(
    model: str = Option(
        "openrouter/qwen/qwen-2.5-coder-32b-instruct",
        "--model",
        "-m",
        help="Model ID to use for generating code feedback"
    ),
    stage_all: bool = Option(False, "--stage-all", "-a", help="Automatically stage all unstaged changes")
) -> None:
    """Generate code quality feedback for uncommitted changes"""
    console = Console()
    console.print(Panel(f"Generating code feedback with model: [cyan]{model}[/cyan]",
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
        feedback_text = ai_summarizer.generate_code_feedback(diff_text, model)
        console.print("\n[bold]Code Quality Feedback:[/bold]")
        console.print(Panel(feedback_text, border_style="blue"))
    else:
        console.print("[yellow]No changes to analyze.[/yellow]")
