# Makefile

# Combined
.PHONY: all start check lint format format-check unit-tests integration-tests test-all clean

start:
	poetry run start

lint:
	poetry run ruff check

format:
	poetry run ruff format

format-check:
	poetry run ruff format --check --diff

check: lint format-check

# Unit tests
unit-tests:
	poetry run pytest src/ai_service/ -v

# Integration tests (main tests directory)
integration-tests:
	poetry run pytest tests/ -v

# Run all tests
test-all: unit-tests integration-tests

all: format-check test-all

clean:
	poetry env remove --all
