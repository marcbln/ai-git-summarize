import typer
from rich.console import Console
from rich.panel import Panel

from ai_git.ai_client import setup_openai
from ai_git.ai_summarizer import AISummarizer
from ai_git.git_operations import get_commit_diff
from ai_git.config_utils import resolve_model_alias, UnknownModelAliasError, get_available_aliases

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
        raise typer.Exit(code=1)

    # Setup AI Client
    try:
        # Pass the resolved model to setup_openai
        client = setup_openai(resolved_model)
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
            model=resolved_model,
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