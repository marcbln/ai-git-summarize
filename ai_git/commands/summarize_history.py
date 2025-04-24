from typing import Optional
from rich.console import Console
from rich.panel import Panel
from ai_git.ai_client import setup_openai
from ai_git.ai_summarizer import AISummarizer
from ai_git.config_utils import resolve_model_alias, UnknownModelAliasError, get_available_aliases

def summarize_history(
    range: str = "HEAD~7..HEAD",
    model: str = "openrouter/qwen/qwen-2.5-coder-32b-instruct",
    output: str = "text",
    detail: str = "technical"
) -> Optional[str]:
    """Summarize a range of git commits"""
    console = Console()
    console.print(Panel(f"Summarizing commit history with model: [cyan]{model}[/cyan]",
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
        
        # Return None to indicate failure
        return None
    
    client = setup_openai(resolved_model)
    ai_summarizer = AISummarizer(client)
    
    summary = ai_summarizer.summarize_history(range, resolved_model, detail)
    if not summary:
        console.print("[red]Failed to generate history summary[/red]")
        return None
        
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
    
    return summary
