.PHONY: run install test

run:
	uv run main.py

install:
	uv sync

test:
	uv run pytest tests/ -v
