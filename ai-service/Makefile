# Makefile

# Combined
.PHONY: check lint format test

lint:
	poetry run ruff check

format:
	poetry run ruff format

check: lint format

test:
	poetry run pytest
