# OpenRouter Command Refactoring Plan

## Current Implementation

The OpenRouter model management functionality is currently implemented as flags in `git_summary.py`:

```python
print_models_table: bool = typer.Option(False, "--print-models-table", help="Print detailed table of all supported models and exit")
list_models: bool = typer.Option(False, "--list-models", help="List model IDs only and exit")
refresh_openrouter_models: bool = typer.Option(False, "--refresh-openrouter-models", help="Refresh the cached OpenRouter models list and exit")
```

## Problems with Current Approach

1. Mixes model management with git summary functionality
2. Flags are not discoverable
3. No logical grouping of related features

## Proposed Solution

Create a new `openrouter` command group with subcommands:

1. `list`: Shows detailed model table (replaces --print-models-table)
2. `list-ids`: Lists model IDs only (replaces --list-models)
3. `refresh`: Refreshes cached models (replaces --refresh-openrouter-models)

## Implementation Steps

### 1. Create New Command Module

Create `git_summarize/commands/openrouter.py` with:

```python
import typer
from rich.console import Console
from ..openrouter_models import get_openrouter_models, format_pricing

app = typer.Typer()

@app.command()
def list(refresh: bool = False):
    """List all available OpenRouter models with pricing"""
    # Implementation from git_summary.py display_models_table()

@app.command()
def list_ids(refresh: bool = False):
    """List only OpenRouter model IDs"""
    # Implementation from git_summary.py list models logic

@app.command()
def refresh():
    """Refresh the OpenRouter models cache"""
    # Implementation from git_summary.py refresh logic
```

### 2. Update cli.py

Add new command group:

```python
from .commands.openrouter import app as openrouter_app

app.add_typer(openrouter_app, name="openrouter", help="Manage OpenRouter models")
```

### 3. Clean Up git_summary.py

Remove:
- print_models_table parameter
- list_models parameter 
- refresh_openrouter_models parameter
- display_models_table function
- Related conditionals in main()

## Impact Analysis

### Benefits
- Better command organization
- More discoverable functionality
- Clearer separation of concerns

### Migration Notes
- Existing scripts using flags will need to be updated
- Documentation will need updating