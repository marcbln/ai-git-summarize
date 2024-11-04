# git-summarize

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
cd git-summarize
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
git-summarize

# Use a specific model
git-summarize --model openrouter/anthropic/claude-3.5-sonnet

# Generate a short commit message
git-summarize --short

# Stage all changes automatically
git-summarize --stage-all

# List available models
git-summarize --list-models

# Show detailed model information including pricing
git-summarize --print-models-table

# Refresh cached model information
git-summarize --refresh-openrouter-models
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

Use `git-summarize --list-models` to see all available models.

## Configuration

The tool looks for the following environment variables:
- `OPENROUTER_API_KEY`: Your OpenRouter API key (required)
- `GIT_SUMMARIZE_DEFAULT_MODEL`: Default model to use (optional) [TODO]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
