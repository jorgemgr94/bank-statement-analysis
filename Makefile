.PHONY: run install test typecheck

run:
	uv run main.py

install:
	uv sync

test:
	uv run pytest tests/ -v

typecheck:
	uv run --with mypy mypy bank_analysis/ main.py
