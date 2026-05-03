# AGENTS.md

## Coding Style

- **Type hints**: Always annotate all function signatures, including return types.
- **Pure functions**: Prefer non-mutating functions. Push side effects (I/O, filesystem, network) to the edges of the program — CLI layer and explicit write functions. Core logic should be pure transformations.
- **Immutability**: Use `frozen=True` dataclasses, tuples, and `Sequence` over `list` in public APIs. Avoid in-place mutation of collections.
- **Explicit error handling**: Use `ValueError` for invalid data. No bare `except`. Log or re-raise clearly.
- **Naming**: snake_case for functions/variables, PascalCase for classes.
- **Imports**: stdlib first, then third-party, then local. No `import *`.

## Project Conventions

- **Layout**: `src/` layout (`src/topo_tool/`).
- **CLI**: `cli.py` handles argument parsing only. All logic lives in library modules.
- **Entry point**: declared in `pyproject.toml` as `topo-tool = "topo_tool.cli:main"`.
- **Commits**: Never commit or push unless explicitly asked to do so.
