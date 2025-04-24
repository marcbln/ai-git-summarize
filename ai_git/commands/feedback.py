import os
import sys
import inquirer
from rich.console import Console
from rich.panel import Panel
from typer import Option
from ..ai_client import setup_openai
from ..ai_summarizer import AISummarizer
from ..git_operations import check_unstaged_changes, stage_all_changes, get_git_diff
from ..config_utils import resolve_model_alias, UnknownModelAliasError, get_available_aliases

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
    
    try:
        # Resolve model alias to full identifier
        resolved_model = resolve_model_alias(model, raise_on_unknown=True)
        if resolved_model != model:
            console.print(f"\n[bold green]Model alias resolved:[/bold green] [cyan]{model}[/cyan] -> [yellow]{resolved_model}[/yellow]")
    except UnknownModelAliasError:
        # Get the available aliases
        aliases = get_available_aliases()
        
        # Print an error message
        console.print(f"\n[bold red]Error:[/bold red] Unknown model alias: [cyan]{model}[/cyan]")
        
        # Print the list of available aliases
        if aliases:
            console.print("\n[bold]Available model aliases:[/bold]")
            
            # Create a table to display the aliases
            from rich.table import Table
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
        feedback_text = ai_summarizer.generate_code_feedback(diff_text, resolved_model)
        console.print("\n[bold]Code Quality Feedback:[/bold]")
        console.print(Panel(feedback_text, border_style="blue"))
    else:
        console.print("[yellow]No changes to analyze.[/yellow]")
