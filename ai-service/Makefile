# Makefile

# Combined
.PHONY: start check lint format unit-tests integration-tests test

start:
	ENVIRONMENT=development pdm run start

# Code quality

lint:
	pdm run ruff check

format:
	pdm run ruff format

check: lint format

# Tests

unit-tests:
	pdm run pytest src/ai_service/ -v

integration-tests:
	pdm run pytest tests/ -v

test: unit-tests integration-tests