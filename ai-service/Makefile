# Makefile

# Combined
.PHONY: all start check lint format format-check unit-tests integration-tests test-all clean install

install:
	pdm sync --dev

start:
	pdm run start

lint:
	pdm run ruff check

format:
	pdm run ruff format

format-check:
	pdm run ruff format --check --diff

check: lint format-check

# Unit tests
unit-tests:
	pdm run pytest src/ai_service/ -v

# Integration tests (main tests directory)
integration-tests:
	pdm run pytest tests/ -v

# Run all tests
test-all: unit-tests integration-tests

all: format-check test-all

clean:
	pdm env remove --all
