# AI Code Explorer — Copilot Instructions

## Project Overview

This is a **RAG-powered AI codebase explorer** with a 3-service architecture:

- **AI Service** (Python/FastAPI) at `ai-service/` — Core RAG engine with ChromaDB, embeddings, and LLM
- **Backend** (Rust/Actix-web) at `backend/` — API gateway with MongoDB storage
- **Frontend** (React/TypeScript/Vite) at `frontend/` — Web interface for GitHub upload and Q&A

**Data flow:** Frontend → Backend → AI Service → ChromaDB/Ollama

Read `README.md` files in root and service directories for architecture details.

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

- Single root `.env` for local setup
- Environment variables referenced across: `.env`, CI/CD workflows, Dockerfiles, service configs, test setups

When adding or changing env vars, update **all** references consistently.

Check config files for current setup:
- `Cargo.toml` for Rust dependencies and backend configuration
- `pyproject.toml` for Python dependencies and AI service configuration
- `package.json` for JavaScript dependencies and frontend configuration

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
