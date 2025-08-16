# Makefile

# Combined
.PHONY: all start check lint format format-check test test-unit test-integration test-all clean

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
test-all: test-unit test-integration

# Default test command (integration tests for backwards compatibility)
test: test-integration

all: format-check test-all

clean:
	poetry env remove --all
