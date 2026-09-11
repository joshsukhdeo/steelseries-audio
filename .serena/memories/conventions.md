# Conventions

- CLI output utilizes specific ANSI color codes for terminal formatting (C_CYAN, C_GREEN, etc.).
- Python uses type hints for function signatures.
- Keep to standard library in Python to avoid adding `pip` dependencies (optional `argcomplete` is handled via `try/except`).
- Scripts are designed to be run directly and rely on `subprocess` / `run_cmd` for system integration.