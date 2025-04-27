# Pytest Integration and Documentation Plan

## Goal

Integrate `pytest` and `pytest-cov` into the `ai-git-summarize` project and create a `HOWTO_pytest.md` document.

## Plan Steps

1.  **Update Project Configuration (`pyproject.toml`):**
    *   Add `pytest` and `pytest-cov` to the development dependencies using the `venv-management` tool (equivalent to `uv add --dev pytest pytest-cov`).
    *   Add a `[tool.pytest.ini_options]` section to configure test discovery (test paths, file/function naming conventions).

2.  **Create Documentation (`HOWTO_pytest.md`):**
    *   Create a new file named `HOWTO_pytest.md` in the project root.
    *   Document:
        *   Setup and dependencies (`pyproject.toml`).
        *   Command to run all tests: `uv run pytest`
        *   Command to run tests with coverage: `uv run pytest --cov=ai_git --cov-report=term-missing`
        *   Explanation of the `[tool.pytest.ini_options]` configuration.

## Workflow Diagram

```mermaid
graph TD
    A[Start: Integrate Pytest] --> B(Modify pyproject.toml);
    B --> B1(Add pytest & pytest-cov as dev deps);
    B --> B2(Add [tool.pytest.ini_options] section);
    A --> C(Create HOWTO_pytest.md);
    C --> C1(Document Setup & Dependencies);
    C --> C2(Document Command: Run Tests);
    C --> C3(Document Command: Run Coverage);
    C --> C4(Document Configuration);
    B1 & B2 & C1 & C2 & C3 & C4 --> D{Review Plan};
    D --> E{User Approval?};
    E -- Yes --> F{Write HOWTO_pytest.md?};
    F -- Yes --> G(Write File Action);
    F -- No --> H(Proceed without writing file);
    G --> I(Suggest Switch to Code Mode);
    H --> I;
    E -- No --> J(Revise Plan);
    J --> D;
    I --> K[End: Ready for Implementation];