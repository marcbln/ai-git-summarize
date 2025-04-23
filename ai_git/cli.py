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
from ai_git.openrouter_models import get_openrouter_models, format_pricing


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
from .commands.git_summary import git_summary
from .commands.summarize_history import summarize_history
from .commands.generate_report import generate_report
from .commands.analyze_commit import analyze_commit
from .commands.openrouter import app as openrouter_app

# Define valid strategies
VALID_STRATEGIES = ["ai", "short", "detailed"]

from .app import app
app.add_typer(openrouter_app, name="openrouter", help="Manage OpenRouter models")

app.command(name="git-feedback")(feedback)
app.command()(summarize_history)
app.command()(generate_report)
app.command(name="git-analyze-commit")(analyze_commit)






if __name__ == "__main__":
    app()
