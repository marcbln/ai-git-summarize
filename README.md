# ai-git

A powerful command-line tool that leverages Large Language Models (LLMs) through OpenRouter to generate meaningful git commit messages by analyzing your staged changes.

## Features

- Generates detailed commit messages based on your code changes
- Supports multiple LLM providers through OpenRouter
- Handles both staged and unstaged changes
- Optional short-form commit messages
- Interactive commit confirmation
- Cached model information for faster operation

## Installation

1. Clone this repository:
```bash
git clone git@github.com:marcbln/ai-git-summarize.git
cd ai-git-summarize
```

2. Install using uv:
```bash
uv pip install -e .
```

3. Set up your OpenAI and/or OpenRouter API key in your shell configuration (e.g., `~/.zshrc` or `~/.bashrc`):
```bash
export OPENAI_API_KEY='your-api-key-here'
export OPENROUTER_API_KEY='your-api-key-here'
```

4. Reload your shell configuration:
```bash
source ~/.zshrc  # or source ~/.bashrc
```

## Usage

Basic usage:
```bash
# Stage your changes
git add .

# Generate a commit message
ai-git

# Use a specific model
ai-git --model openrouter/anthropic/claude-3.5-sonnet

# Generate a short commit message
ai-git --short

# Stage all changes automatically
ai-git --stage-all

# List available models
ai-git --list-models

# Show detailed model information including pricing
ai-git --print-models-table

# Refresh cached model information
ai-git --refresh-openrouter-models
```

The tool will:
1. Check for unstaged changes and offer to stage them
2. Analyze your staged changes
3. Generate a detailed commit message
4. Show you the suggested message
5. Ask for confirmation before committing

## Requirements

- Python 3.7+
- Git
- OpenAI or OpenRouter API key

## Supported Models

The tool supports a wide range of LLMs through OpenRouter, including:
- Anthropic Claude 3 Sonnet
- Qwen 2.5 72B
- LLAMA 3 70B
- DeepSeek Chat
- Nemotron 70B
- And many more...

Use `ai-git --list-models` to see all available models.

## Configuration

The tool looks for the following environment variables:
- `OPENROUTER_API_KEY`: Your OpenRouter API key (required)
- `GIT_SUMMARIZE_DEFAULT_MODEL`: Default model to use (optional) [TODO]

## Testing

The test suite uses pytest. To run all tests:

```bash
pytest -v tests/
```

Key test components:
- `test_ai_summarizer.py`: Core summarization functionality
  - Backtick stripping (`test_strip_backticks`)
  - AI response validation
  - Error handling for API calls
- `test_model_alias.py`: Model alias resolution system

To run tests with coverage report:
```bash
pytest --cov=ai_git --cov-report=term-missing
```

Example testing a specific component:
```bash
pytest -v tests/test_ai_summarizer.py::test_strip_backticks
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the ALL License - see the LICENSE file for details.

## AI-Powered Git Insights

### Installation
```bash
pip install ai-git
```

### Commands

#### `ai-git analyze-commit`
Analyze specific commit messages with AI

#### `ai-git generate-report`
Create detailed reports from git history

#### `ai-git git-summary`
Show condensed summary of repository status

#### `ai-git summarize-history`
Generate AI summaries of commit timelines

#### `ai-git openrouter`
Manage OpenRouter model configurations

#### `ai-git feedback`
Provide feedback on AI summaries
