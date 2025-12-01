# Command Refactoring Plan

## Current Structure
- All CLI commands are currently in `git_summarize/cli.py`
- The file contains:
  - 4 main commands (git-feedback, summarize_history, git-summary, generate_report)
  - Shared helper functions
  - Typer app setup

## Proposed New Structure

```
git_summarize/
├── commands/
│   ├── __init__.py
│   ├── feedback.py        # git-feedback command
│   ├── summarize_history.py
│   ├── git_summary.py     # main git-summary command
│   └── generate_report.py
├── cli.py                # Simplified - just imports and registers commands
└── (other existing files)
```

## Refactoring Steps

1. Create commands directory:
   ```bash
   mkdir git_summarize/commands
   touch git_summarize/commands/__init__.py
   ```

2. For each command:
   - Create new file in commands/ directory
   - Move command function and related helpers
   - Add necessary imports
   - Export command in __init__.py

3. Update cli.py:
   - Remove moved commands
   - Import commands from new location
   - Keep shared utilities like display_models_table()

4. Testing:
   - Verify all commands still work
   - Check imports and dependencies
   - Ensure no functionality is broken

## Benefits
- Better code organization
- Easier maintenance
- Clearer separation of concerns
- Reduced file size and complexity
- Improved testability
