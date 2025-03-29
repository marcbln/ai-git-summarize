# Commit Message Format Improvements

## Problem Statement
The current implementation uses hardcoded logic (500 character threshold) to decide between short and detailed commit message formats. This leads to suboptimal decisions for cases like simple renames that exceed the length threshold.

## Solution Approach
Implement a unified prompt that:
1. Contains instructions for both short and detailed formats
2. Lets the AI autonomously decide which format to use
3. Maintains Conventional Commits standards

## Implementation Plan

### 1. Prompt Changes (prompts.py)
- Create new unified prompt combining both formats:
```python
@staticmethod
def build_unified_prompt(diff_text: str) -> "PromptBuilder.MessageType":
    return [
        {
            "role": "system",
            "content": """You are an expert at analyzing git diffs and generating optimal commit messages. Follow these rules:

1. First analyze the changes and determine if they warrant:
   - SHORT format (single line) for simple changes like:
     * Renames/refactors
     * Small fixes
     * Trivial updates
   - DETAILED format (multi-line) for:
     * Complex changes
     * Multiple files modified
     * Significant functionality changes

2. Use Conventional Commit types:
   feat: New features
   fix: Bug fixes  
   chore: Maintenance
   docs: Documentation
   test: Tests
   refactor: Code improvements
   perf: Performance
   ci: CI/CD

3. Format:
   - SHORT: "type: description" (one line)
   - DETAILED: "type: description" followed by bullet points

Output only the commit message."""
        },
        {
            "role": "user",
            "content": f"Analyze these changes and generate the optimal commit message:\n\n{diff_text}"
        }
    ]
```

### 2. AI Summarizer Changes (ai_summarizer.py)
- Remove hardcoded threshold logic
- Use unified prompt for "ai" strategy:
```python
def summarize_changes(self, diff_text: str, model: str, strategy: str) -> Optional[str]:
    if strategy == "ai":
        messages = PromptBuilder.build_unified_prompt(diff_text)
    elif strategy == "short":
        messages = PromptBuilder.build_short_diff_prompt(diff_text) 
    elif strategy == "detailed":
        messages = PromptBuilder.build_diff_prompt(diff_text)
    
    kwargs = self._prepare_api_kwargs(messages, model)
    return self._make_api_call(kwargs)
```

### 3. CLI Updates (cli.py)
- Update help text for strategy parameter:
```python
strategy: str = typer.Option(
    "ai", 
    help="Commit message strategy: 'ai' (auto-detect format), 'short' (force one-line), 'detailed' (force multi-line)"
)
```

## Expected Benefits
- More accurate format decisions
- Cleaner commit history
- Reduced manual intervention
- Maintained Conventional Commits compliance