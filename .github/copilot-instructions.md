# AI Code Explorer — Global Copilot Instructions

These instructions define how GitHub Copilot and Copilot Chat should behave in this repository.

## Project Overview

This is a **RAG-powered AI codebase explorer** with a 3-service architecture:

- **AI Service** (Python/FastAPI): Core RAG engine with ChromaDB vector storage, sentence-transformers embeddings, and Ollama LLM integration. Look at `/ai-code-explorer/ai-service` for more details.
- **Backend** (Rust/Actix-web): API gateway for request routing, validation, and future auth features. Look at `/ai-code-explorer/backend` for more details.
- **Frontend** (React/TypeScript/Vite): Modern web interface for GitHub project upload and Q&A chat. Look at `/ai-code-explorer/frontend` for more details.

Data flows: **Frontend** → **Backend** → **AI Service** → **ChromaDB/Ollama**.

Read the root `Readme.md` file and `Readme.md` files in each service folder for more context.

## Codebase Awareness

1. **Read before writing:** Always infer context from the current file and related modules before suggesting edits. 
2. **Never assume architecture:** Verify imports, structs, routes, and dependencies. Study existing structure.
3. **Follow established patterns:** Mirror coding styles, error handling, type definitions, API implementations and all other project conventions.
4. **Stay up to date:** Agents must always be up to date with the codebase. Base all recommendations on the latest project state.
5. **Respect service boundaries:** Avoid mixing backend, AI, and frontend logic. 

## Code Quality & Standards

| Language | Lint / Format | Test | Notes |
|-----------|----------------|------|-------|
| Rust | `cargo clippy`, `rustfmt` | `cargo test` | `cargo audit` | Use idiomatic async and error handling |
| Python | `ruff`, `black` | `pytest` | Maintain type hints and FastAPI typing |
| TypeScript | `npm run lint`, `prettier` | `vitest` | Use ES Modules, React Hooks, and strict typing |

### Style & Conventions
- Keep code **modular**, **typed**, and **idiomatic**. Follow best practices and adjust to existing patterns.
- Use descriptive names, minimal comments, and short TODOs.  
- Handle errors gracefully. Follow existing patterns for error handling.  
- Keep dependencies minimal; prefer standard library where possible.

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

When generating or modifying code, always ensure the following criteria are met:

1. **Correctness:** Must compile, run, and be tested.  
2. **Security:** Never include credentials or unsafe code.  
3. **Consistency:** Follow project conventions, existing patterns and architecture.  
4. **Modernity:** Use latest stable versions and industry best practices. Suggest updates when applicable.  
5. **Clarity:** Write clear, maintainable, and well-documented code.
6. **Performance:** Optimize for efficiency without sacrificing readability or maintainability.
7. **Minimalism:** Avoid unnecessary complexity or dependencies. Keep solutions as simple as possible.
8. **Test Coverage:** Ensure new code is covered by appropriate tests and existing tests are not broken.
9. **Documentation:** Update relevant documentation, comments, and READMEs to reflect changes.
