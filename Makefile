.PHONY: run format

run:
	uv run market-analytics-platform

format:
	uv run ruff check --fix .
	uv run ruff format .
