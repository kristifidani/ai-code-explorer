# Makefile

# Combined
.PHONY: all check lint format test clean

lint:
	poetry run ruff check

format:
	poetry run ruff format --check --diff

check: lint format

test:
	poetry run pytest

all: check test

clean: poetry env remove --all || true
