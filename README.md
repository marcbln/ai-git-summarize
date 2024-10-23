# git-summarize

A command-line tool that uses OpenAI's API to generate meaningful git commit messages by analyzing your staged changes.

## Installation

1. Clone this repository:
```bash
git clone [your-repo-url]
cd git-summarize
```

2. Install using uv:
```bash
uv pip install -e .
```

3. Set up your OpenAI API key in your shell configuration (e.g., `~/.zshrc` or `~/.bashrc`):
```bash
export OPENAI_API_KEY='your-api-key-here'
```

4. Make sure your Python bin directory is in your PATH by adding these lines to your shell config:
```bash
export PATH="$HOME/.local/bin:$PATH"
export PATH="$HOME/.local/share/uv/bin:$PATH"
```

5. Reload your shell configuration:
```bash
source ~/.zshrc  # or source ~/.bashrc
```

## Usage

1. Stage your changes as usual:
```bash
git add .  # or git add specific-files
```

2. Generate a commit message:
```bash
git-summarize
```

3. Optionally specify a different OpenAI model:
```bash
git-summarize --model gpt-4
```

The tool will:
- Show you the suggested commit message
- Ask if you want to use it
- If you confirm, automatically commit the changes with the generated message

## Requirements

- Python 3.7+
- Git
- OpenAI API key
- `uv` package manager

## Project Structure

```
.
├── README.md
├── pyproject.toml
└── git_summarize/
    └── cli.py
```

## Development

To contribute or modify:

1. Clone the repository
2. Make your changes
3. Reinstall with `uv pip install -e .`

## License

[Your chosen license]
