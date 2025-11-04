---
applyTo: "ai-service/**/*.py"
---

# Python AI Service Instructions

## Critical Conventions

**Type Safety:**
- Type hints required on all function parameters and returns
- Use Pydantic `BaseModel` for all FastAPI request/response models

**Testing:**
- Integration tests require ChromaDB and Ollama running locally
- Use pytest fixtures from `conftest.py`
- Tests in `tests/` directory

**Commands:**
- See `ai-service/Makefile` for all available targets.

## Architecture Context

Read `ai-service/README.md` first — it explains the RAG flow:
**Ingestion** → **Chunking** → **Embedding** → **Storage** (ChromaDB) → **Query** → **LLM Answer**

There are also Readmes in key subdirectories explaining their roles. Read those to understand how different modules interact.

## Key Files

- `src/ai_service/main.py` — Server entry point
- `src/ai_service/handlers/` — Request handlers
- `src/ai_service/embeddings/` — Embeddings strategy
- `src/ai_service/chunking/` — Chunking strategy
- `src/ai_service/db_setup/` — ChromaDB operations
- `src/ai_service/ollama_client.py` — LLM client wrapper

**For implementation details:** Read existing code to understand file relationships and development patterns. Keep it consistent.
