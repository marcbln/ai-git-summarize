import os
import sys
import yaml
import typer
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from ..ai_client import setup_openai
from ..ai_summarizer import AISummarizer
from ..config_utils import resolve_model_alias, UnknownModelAliasError, get_available_aliases

def generate_report(
    group: str,
    start_date: str,
    end_date: str,
    output_format: str = "markdown",
    model: str = typer.Option(
        "openrouter/qwen/qwen-2.5-coder-32b-instruct",
        "--model",
        "-m",
        help="Model ID or alias to use for generating the report"
    )
) -> None:
    """Generate work report for a project group between dates"""
    console = Console()
    
    try:
        config = load_project_groups_config(validate_paths=False)
        
        if group not in config["projects-groups"]:
            console.print(f"[red]Error: Unknown group '{group}'[/red]")
            console.print(f"Available groups: {', '.join(config['projects-groups'].keys())}")
            return
            
        # Now validate paths just for the requested group
        projects = []
        for path in config["projects-groups"][group]:
            if not Path(path).exists():
                console.print(f"[red]Error: Project path does not exist: {path}[/red]")
                return
            projects.append(path)
        
        # Validate dates
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
        
        # Resolve model alias
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
            return
        
        # Aggregate project data
        report_data = aggregate_project_data(projects, start_date, end_date, resolved_model)
        
        # Generate output in requested format
        generate_output(report_data, output_format, console)
        
    except Exception as e:
        console.print(f"[red]Error generating report: {e}[/red]")

def load_project_groups_config(validate_paths: bool = True) -> Dict[str, List[str]]:
    """Load projects-groups configuration file."""
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
        
    if validate_paths:
        # Validate project paths exist
        for group, paths in config["projects-groups"].items():
            for path in paths:
                if not Path(path).exists():
                    raise ValueError(f"Project path does not exist: {path}")
                
    return config

def aggregate_project_data(projects: List[str], start_date: str, end_date: str, model: str) -> Dict[str, Any]:
    """Aggregate git history data from multiple projects."""
    # Resolve model alias
    resolved_model = resolve_model_alias(model)
    if resolved_model != model:
        print(f"Model alias resolved: {model} -> {resolved_model}")
        
    client = setup_openai(resolved_model)
    ai_summarizer = AISummarizer(client)
    
    report_data = ai_summarizer.generate_project_report(
        projects, start_date, end_date, resolved_model
    )
    
    if report_data["total_commits"] > 0:
        all_commits = []
        for project in report_data["projects"]:
            all_commits.extend(project.get("commits", []))
            
        report_data["ai_analysis"] = {
            "summary": ai_summarizer._summarize_commit_history(all_commits, resolved_model, "technical"),
            "key_activities": categorize_activities(all_commits)
        }
    
    return report_data

def categorize_activities(commits: List[str]) -> Dict[str, int]:
    """Categorize commits into activity types."""
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
    """Generate formatted output for the report."""
    if output_format == "json":
        import json
        json_data = report_data.copy()
        console.print_json(json.dumps(json_data, indent=2, default=str))
        
    elif output_format == "text":
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
