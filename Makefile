.PHONY: run install

run:
	uv run main.py

install:
	uv sync
