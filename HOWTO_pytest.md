# How to use Pytest in ai-git-summarize

## Setup and Dependencies

Pytest and pytest-cov are included as development dependencies in `pyproject.toml`. To install them, ensure you have `uv` installed and run:

```bash
uv sync
```

## Running Tests

To run all tests in the project, use the following command:

```bash
uv run pytest
```

## Running Tests with Coverage

To run tests and generate a coverage report, use the following command:

```bash
uv run pytest --cov=ai_git --cov-report=term-missing
```

This command will show a summary of code coverage in the terminal, highlighting missing lines.

## Pytest Configuration

The pytest configuration is located in the `[tool.pytest.ini_options]` section of `pyproject.toml`.

```toml
[tool.pytest.ini_options]
pythonpath = "."
testpaths = "tests"
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
```

*   `pythonpath = "."`: Adds the current directory to the Python path, allowing pytest to discover modules within the project.
*   `testpaths = "tests"`: Specifies that tests are located in the `tests` directory.
*   `python_files = "test_*.py"`: Tells pytest to discover test files named `test_*.py`.
*   `python_classes = "Test*"`: Tells pytest to discover test classes named `Test*`.
*   `python_functions = "test_*"`: Tells pytest to discover test functions named `test_*`.