# CONVENTIONS.md

## Python Coding Conventions

- **Python version**: 3.10+
- **Type hints**: Mandatory for functions.
- **Style**: Follow [PEP8](https://peps.python.org/pep-0008/) and [PEP257](https://peps.python.org/pep-0257/).
- **Naming**: 
  - `snake_case` for functions/variables, 
  - `PascalCase` for classes.
- **F-strings**: Preferred for string formatting.

## Frameworks

- **Typer**: Use for CLI apps, with type hints for arguments/options.
- **FastAPI**: Use for web apps, with async endpoints where possible.
- **SQLAlchemy**: Use for database models with declarative syntax.
