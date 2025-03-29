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
from .git_operations import check_unstaged_changes, stage_all_changes, get_git_diff, commit_changes, push_changes, get_commit_messages

# Define valid strategies
VALID_STRATEGIES = ["ai", "short", "detailed"]

def aggregate_project_data(projects: List[str], start_date: str, end_date: str, model: str) -> Dict[str, Any]:
    """Aggregate git history data from multiple projects.
    
    Args:
        projects: List of project paths
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        model: Model to use for AI analysis
        
    Returns:
        Dictionary containing aggregated report data
    """
    client = setup_openai(model)
    ai_summarizer = AISummarizer(client)
    
    # Generate report data
    report_data = ai_summarizer.generate_project_report(
        projects, start_date, end_date, model
    )
    
    # Add AI analysis if there are commits
    if report_data["total_commits"] > 0:
        # Collect all commits across projects
        all_commits = []
        for project in report_data["projects"]:
            all_commits.extend(project.get("commits", []))
            
        # Analyze commit patterns
        report_data["ai_analysis"] = {
            "summary": ai_summarizer._summarize_commit_history(all_commits, model, "technical"),
            "key_activities": categorize_activities(all_commits)
        }
    
    return report_data

def categorize_activities(commits: List[str]) -> Dict[str, int]:
    """Categorize commits into activity types.
    
    Args:
        commits: List of commit messages
        
    Returns:
        Dictionary mapping activity types to commit counts
    """
    categories = {
        "feature": 0,
        "bugfix": 0,
        "refactor": 0,
        "docs": 0,
        "other": 0
    }
    
    for commit in commits:
        lower_commit = commit.lower()
        if any(term in lower_commit for term in ["feat", "feature", "add", "implement"]):
            categories["feature"] += 1
        elif any(term in lower_commit for term in ["fix", "bug", "issue", "error", "crash"]):
            categories["bugfix"] += 1
        elif any(term in lower_commit for term in ["refactor", "clean", "improve", "optimize"]):
            categories["refactor"] += 1
        elif any(term in lower_commit for term in ["doc", "comment", "readme"]):
            categories["docs"] += 1
        else:
            categories["other"] += 1
            
    return categories

def generate_output(report_data: Dict[str, Any], output_format: str, console: Console) -> None:
    """Generate formatted output for the report.
    
    Args:
        report_data: Dictionary containing report data
        output_format: Output format (markdown, json, text)
        console: Rich console instance for output
    """
    if output_format == "json":
        # Convert sets to lists for JSON serialization
        import json
        json_data = report_data.copy()
        console.print_json(json.dumps(json_data, indent=2, default=str))
        
    elif output_format == "text":
        # Simple text output
        console.print(f"\n[bold]Work Report[/bold] ({report_data['period']['start']} to {report_data['period']['end']})")
        console.print(f"Total commits: {report_data['total_commits']}")
        console.print(f"Contributors: {', '.join(report_data['unique_authors'])}")
        console.print(f"Files changed: {report_data['files_changed']}")
        
        if "ai_analysis" in report_data:
            console.print("\n[bold]Summary:[/bold]")
            console.print(report_data["ai_analysis"]["summary"])
            
            console.print("\n[bold]Key Activities:[/bold]")
            for category, count in report_data["ai_analysis"]["key_activities"].items():
                console.print(f"- {category.capitalize()}: {count} commits")
                
    else:  # markdown
        # Create markdown report
        md_lines = [
            f"# Work Report for Projects ({report_data['period']['start']} to {report_data['period']['end']})",
            "",
            "## Project Summary",
            f"- Total commits: {report_data['total_commits']}",
            f"- Contributors: {', '.join(report_data['unique_authors'])}",
            f"- Files changed: {report_data['files_changed']}",
            ""
        ]
        
        if "ai_analysis" in report_data:
            md_lines.extend([
                "## Key Activities",
                ""
            ])
            
            for category, count in report_data["ai_analysis"]["key_activities"].items():
                md_lines.append(f"- {category.capitalize()} ({count} commits)")
                
            md_lines.extend([
                "",
                "## Summary",
                "",
                report_data["ai_analysis"]["summary"]
            ])
            
        md_content = "\n".join(md_lines)
        console.print(Panel(md_content, title="[bold]Work Report[/bold]", border_style="blue", expand=False))

def load_project_groups_config() -> Dict[str, List[str]]:
    """Load and validate projects-groups configuration file.
    
    Returns:
        Dictionary mapping group names to lists of project paths
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config is invalid
    """
    config_path = Path("projects-groups.yaml")
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at {config_path}")
        
    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in config file: {e}")
        
    if not config or "projects-groups" not in config:
        raise ValueError("Config file missing 'projects-groups' key")
        
    # Validate project paths exist
    for group, paths in config["projects-groups"].items():
        for path in paths:
            if not Path(path).exists():
                raise ValueError(f"Project path does not exist: {path}")
                
    return config

app = typer.Typer()

@app.command(name="git-feedback")
def feedback(
    model: str = typer.Option(
        "openrouter/qwen/qwen-2.5-coder-32b-instruct",
        "--model",
        "-m",
        help="Model ID to use for generating code feedback"
    ),
    stage_all: bool = typer.Option(False, "--stage-all", "-a", help="Automatically stage all unstaged changes")
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

@app.command()
def summarize_history(
    range: str = typer.Argument("HEAD~7..HEAD", help="Git commit range"),
    model: str = typer.Option("openrouter/qwen/qwen-2.5-coder-32b-instruct", help="Model to use"),
    output: str = typer.Option("text", help="Output format (text, json, markdown)"),
    detail: str = typer.Option("technical", help="Detail level (technical, non-technical, overview)")
) -> None:
    """Summarize a range of git commits"""
    console = Console()
    console.print(Panel(f"Summarizing commit history with model: [cyan]{model}[/cyan]",
                     style="bold green"))
    
    client = setup_openai(model)
    ai_summarizer = AISummarizer(client)
    
    summary = ai_summarizer.summarize_history(range, model, detail)
    if not summary:
        console.print("[red]Failed to generate history summary[/red]")
        return
        
    if output == "json":
        try:
            import json
            print(json.dumps({"summary": summary}, indent=2))
        except Exception as e:
            console.print(f"[red]Error formatting JSON: {e}[/red]")
    elif output == "markdown":
        console.print(Panel(summary, title="[bold]Commit History Summary[/bold]",
                          border_style="blue", expand=False))
    else:  # text
        console.print("\n[bold]Commit History Summary:[/bold]")
        console.print(summary)


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

@app.command(name="git-summary")
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
    print_models_table: bool = typer.Option(False, "--print-models-table", help="Print detailed table of all supported models and exit"),
    list_models: bool = typer.Option(False, "--list-models", help="List model IDs only and exit"),
    refresh_openrouter_models: bool = typer.Option(False, "--refresh-openrouter-models", help="Refresh the cached OpenRouter models list and exit"),
    push: bool = typer.Option(False, "--push", "-p", help="Automatically push changes after commit without asking for confirmation"),
    always_accept_commit_message: bool = typer.Option(False, "--always-accept-commit-message", "-y",
                                                      help="Skip confirmation prompt and accept suggested commit message"),
    
) -> None:
    """Summarize git changes and create commits (git-summary)."""

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

    console = Console()
    console.print(Panel(f"Starting git-summarize with model: [cyan]{model}[/cyan]", 
                       style="bold green"))
    client = setup_openai(model)
    ai_summarizer = AISummarizer(client)

    # Validate strategy
    if strategy not in VALID_STRATEGIES:
        console.print(f"[bold red]Error:[/bold red] Unknown strategy '{strategy}'.")
        console.print(f"Valid choices are: {', '.join(VALID_STRATEGIES)}")
        sys.exit(1)
    
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
    console = Console()
    console.print(Panel(f"Summarizing commit history with model: [cyan]{model}[/cyan]",
                       style="bold green"))
    
    client = setup_openai(model)
    ai_summarizer = AISummarizer(client)
    
    summary = ai_summarizer.summarize_history(range, model, detail)
    if summary:
        if output == "json":
            console.print_json(summary)
        else:
            console.print(Panel(summary, title="[bold]Commit History Summary[/bold]"))
    else:
        console.print("[red]Failed to generate commit history summary[/red]")

@app.command()
def generate_report(
    group: str = typer.Option(..., "--group", "-g", help="Project group to analyze"),
    start_date: str = typer.Option(..., "--start-date", "-s", help="Start date (YYYY-MM-DD)"),
    end_date: str = typer.Option(..., "--end-date", "-e", help="End date (YYYY-MM-DD)"),
    output_format: str = typer.Option("markdown", "--output-format", "-o",
                                   help="Output format (markdown, json, text)")
) -> None:
    """Generate work report for a project group between dates"""
    console = Console()
    
    try:
        # Load and validate config
        config = load_project_groups_config()
        if group not in config["projects-groups"]:
            console.print(f"[red]Error: Unknown group '{group}'[/red]")
            console.print(f"Available groups: {', '.join(config['projects-groups'].keys())}")
            return
            
        projects = config["projects-groups"][group]
        
        # Validate dates
        from datetime import datetime
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            if start > end:
                console.print("[red]Error: Start date must be before end date[/red]")
                return
        except ValueError as e:
            console.print(f"[red]Error: Invalid date format - {e}[/red]")
            console.print("Please use YYYY-MM-DD format for dates")
            return
            
        # Generate report
        console.print(Panel(f"Generating report for group [cyan]{group}[/cyan] "
                          f"from [cyan]{start_date}[/cyan] to [cyan]{end_date}[/cyan]",
                          style="bold green"))
        
        # Get model to use for AI analysis
        model = "openrouter/qwen/qwen-2.5-coder-32b-instruct"
        
        # Aggregate project data
        report_data = aggregate_project_data(projects, start_date, end_date, model)
        
        # Generate output in requested format
        generate_output(report_data, output_format, console)
        
    except Exception as e:
        console.print(f"[red]Error generating report: {e}[/red]")

if __name__ == "__main__":
    app()
