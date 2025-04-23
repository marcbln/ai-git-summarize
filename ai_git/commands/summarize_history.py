from typing import Optional
from rich.console import Console
from rich.panel import Panel
from ai_git.ai_client import setup_openai
from ai_git.ai_summarizer import AISummarizer

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
    
    client = setup_openai(model)
    ai_summarizer = AISummarizer(client)
    
    summary = ai_summarizer.summarize_history(range, model, detail)
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
