# History Summarization Implementation Plan

## CLI Changes
1. Add new command:
```python
@app.command()
def summarize_history(
    range: str = typer.Argument("HEAD~7..HEAD", help="Git commit range"),
    model: str = typer.Option(default_model, help="Model to use"),
    output: str = typer.Option("text", help="Output format (text, json, markdown)")
):
    """Summarize a range of git commits"""
```

2. Add argument parsing for:
   - Commit range specification
   - Output format options
   - Summary detail level

## AI Summarizer Changes
1. Add new method:
```python
def summarize_history(commit_range: str, model: str) -> str:
    commits = get_commit_messages(commit_range)
    return self._summarize_commit_history(commits, model)
```

2. Implement helper methods:
   - `get_commit_messages()` - extracts messages from git log
   - `_summarize_commit_history()` - handles the AI summarization

## Prompt Engineering
1. Create new prompt template:
```python
@staticmethod 
def build_history_prompt(commits: List[str]) -> MessageType:
    return [
        {
            "role": "system",
            "content": "Summarize these git commits into a cohesive report..."
        },
        {
            "role": "user",
            "content": "\n".join(commits) 
        }
    ]
```

2. Add variations for:
   - Technical vs non-technical summaries
   - Different time periods (daily, weekly, monthly)
   - Team vs individual focus

## Testing Plan
1. Unit tests for:
   - Commit range parsing
   - Message extraction
   - Summary generation

2. Integration tests for:
   - End-to-end history summarization
   - Different output formats
   - Edge cases (empty ranges, merge commits)

## Rollout Strategy
1. Phase 1: Basic text output
2. Phase 2: Format options (markdown, json)
3. Phase 3: Team reporting features