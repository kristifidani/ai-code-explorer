# AI Code Explorer — Copilot Instructions

## Project Overview

This is a **RAG-powered AI codebase explorer** with a 3-service architecture:

- **AI Service** (Python/FastAPI) at `ai-service/` — Core RAG engine with ChromaDB vector storage, sentence-transformers embeddings, and Ollama LLM integration
- **Backend** (Rust/Actix-web) at `backend/` — API gateway for request routing, validation, and future auth features with MongoDB
- **Frontend** (React/TypeScript/Vite) at `frontend/` — Modern web interface for GitHub project upload and Q&A chat

**Data flow:** Frontend → Backend → AI Service → ChromaDB/Ollama

**Critical patterns:**
- Backend wraps all responses in `ApiResponse<T>` with `code`, `data?`, `message` fields
- AI Service uses `set_repo_context(url)` before ChromaDB operations for multi-tenant isolation
- Rust binary name is `rest-api` (not `backend`) - see `Cargo.toml`
- Custom errors use classmethod factories (Python) and `thiserror` (Rust) - see `errors.py` and `error.rs`

For detailed architecture, read the root `README.md` and service-level READMEs (especially `ai-service/README.md` for RAG flow diagram).

## Development Workflow

### Quick Start Commands
```bash
# Full stack (requires Docker, Ollama, MongoDB)
docker compose up -d --wait

# Individual services
cd ai-service && make start      # Port 8000 (requires PDM, Python 3.10+)
cd backend && cargo run          # Port 8080 (requires Rust 1.90+)
cd frontend && npm run dev       # Port 5173 (requires Node 18+)
```

### Before Committing
```bash
cd backend && cargo clippy && cargo fmt && cargo test
cd ai-service && make check && make format && make test
cd frontend && npm run lint && npm run build
```

**Testing:**
- Rust: `rstest` for parametric tests, `mockito` for HTTP mocking - see `integration_tests_*.rs`
- Python: `pytest` with session fixtures for DB/model initialization - see `conftest.py`
- Frontend: No tests yet

**Note:** Services with Makefiles (`ai-service`) should use `make` commands. See `ai-service/Makefile` for all available targets.

## Code Quality & Standards

| Language | Lint / Format | Test | Notes |
|----------|---------------|------|-------|
| Rust | `cargo clippy`, `cargo fmt` | `cargo test` | No `unwrap()`/`expect()` in production code |
| Python | `make lint`, `make format` | `make test` | Type hints required on all functions |
| TypeScript | `npm run lint` | (no tests yet) | Strict TypeScript, no `any` types |

## Core Principles

1. **Read before writing** — Always infer context from the current file and related modules before suggesting edits
2. **Never assume architecture** — Verify imports, structs, routes, and dependencies. Study existing structure
3. **Follow established patterns** — Mirror coding styles, error handling, type definitions, API implementations
4. **Stay up to date** — Base all recommendations on the latest project state
5. **Respect service boundaries** — Avoid mixing backend, AI, and frontend logic

### Style & Conventions
- Keep code **modular**, **typed**, and **idiomatic**
- Use descriptive names, minimal comments, and short TODOs
- Handle errors gracefully following existing patterns
- Keep dependencies minimal; prefer standard library where possible

## Configuration & Environment

- Single root `.env` for local setup.  
- Environment variables are referenced across:
  - `.env`
  - CI/CD workflows
  - Dockerfiles
  - Service config files  
  - Test setups

When adding or changing env vars, update **all** references consistently.

- Read:
    - `Cargo.toml` for Rust dependencies and backend service setup. 
    - `pyproject.toml` for Python dependencies and ai service setup.
    - `package.json` for JavaScript dependencies and frontend service setup.

## Valuation Criteria

When generating or modifying code, ensure:

1. **Correctness** — Must compile, run, and be tested
2. **Security** — Never include credentials or unsafe code
3. **Consistency** — Follow project conventions and existing patterns
4. **Modernity** — Use latest stable versions and best practices
5. **Clarity** — Write clear, maintainable code
6. **Performance** — Optimize without sacrificing readability
7. **Minimalism** — Avoid unnecessary complexity
8. **Test Coverage** — Ensure tests exist and pass
9. **Documentation** — Update relevant docs and READMEs
