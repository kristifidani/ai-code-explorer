# Makefile

# Combined
.PHONY: all check lint format format-check test clean

lint:
	poetry run ruff check

format:
	poetry run ruff format

format-check:
	poetry run ruff format --check --diff

check: lint format

test:
	poetry run pytest

all: format-check test

clean:
	poetry env remove --all
