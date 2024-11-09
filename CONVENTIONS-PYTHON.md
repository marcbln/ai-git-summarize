# CONVENTIONS.md

## Python Coding Conventions

- **Python version**: 3.10+
- **Type hints**: Mandatory for functions.
- **Style**: Follow [PEP8](https://peps.python.org/pep-0008/) and [PEP257](https://peps.python.org/pep-0257/).
- **Naming**:
  - `snake_case` for functions/variables
  - `PascalCase` for classes
- **F-strings**: Preferred for string formatting

## Frameworks

- **Typer**: for CLI apps, with type hints for arguments/options.
- **FastAPI**: for web apps, with async endpoints where possible.
- **SQLAlchemy**: for database models with declarative syntax.
- **Pydantic**: for data validation and serialization.
- **rich**: for colorful terminal output.
