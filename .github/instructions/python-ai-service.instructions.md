---
applyTo: "ai-service/**/*.py"
---

# Python AI Service Instructions

## Critical Conventions

**Type Safety:**
- Type hints required on all functions. Working on strict mode
- Pydantic models for FastAPI request/response

**ChromaDB Context:**
- ALWAYS call `set_repo_context(url)` before DB operations
- Enables multi-tenant collection isolation
- See `db_setup/setup.py` for implementation details

**Error Handling:**
- Custom exceptions inherit from `AIServiceError`
- Use classmethod factories
- See `errors.py` for implementation details

**Testing:**
- Session fixtures initialize ChromaDB + embedding model
- Check `conftest.py` for setup patterns

## Architecture Context

**RAG Flow:** Ingest (clone → chunk → embed → store) → Query (embed → search → LLM)

Read `ai-service/README.md` for detailed architecture and flow diagrams. Read the module READMEs for implementation details.

**Commands:** Use `make` for all tasks (check `Makefile` for available targets)

## Key Files

- `main.py` — FastAPI app with lifespan for service initialization
- `handlers/` — Request handlers for ingest and Q&A flows
- `db_setup/setup.py` — ChromaDB context management
- `errors.py` — Exception hierarchy with classmethod factories
- `embeddings/` — Model initialization and encoding
- `chunking/` — Code chunking strategies
- `pyproject.toml` — Check for Python version and dependencies

For more details and complete overview scan the tree structure.
