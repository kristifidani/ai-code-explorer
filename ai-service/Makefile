# Makefile

# Combined
.PHONY: all start check lint format format-check test clean

start:
	poetry run start

lint:
	poetry run ruff check

format:
	poetry run ruff format

format-check:
	poetry run ruff format --check --diff

check: lint format-check

test:
	poetry run pytest

all: format-check test

clean:
	poetry env remove --all
