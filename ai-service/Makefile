# Makefile

# Combined
.PHONY: check lint format

lint:
	poetry run ruff check

format:
	poetry run ruff format

check: lint format
