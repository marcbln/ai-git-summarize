import typer
from rich.console import Console
from rich.panel import Panel

from git_summarize.ai_client import setup_openai
from git_summarize.ai_summarizer import AISummarizer
from git_summarize.git_operations import get_commit_diff

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