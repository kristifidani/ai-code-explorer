# AI Code Explorer - AI Coding Agent Instructions

## Project Architecture & Structure

This is a **RAG-powered AI codebase explorer** with a 3-service architecture:

- **AI Service** (Python/FastAPI): Core RAG engine with ChromaDB vector storage, sentence-transformers embeddings, and Ollama LLM integration. Please look at `/ai-code-explorer/ai-service` for more details about its structure and key files.
- **Backend** (Rust/Actix-web): API gateway for request routing, validation, and future auth features. Please look at `/ai-code-explorer/backend` for more details about its structure and key files.
- **Frontend** (React/TypeScript/Vite): Modern web interface for GitHub project upload and Q&A chat. Please look at `/ai-code-explorer/frontend` for more details about its structure and key files.

Data flows: Frontend → Rust Backend → Python AI Service → ChromaDB/Ollama.

## Critical Development Principles

### Consistency is Paramount
This is an active learning project emphasizing **professional patterns and industry standards**. When making changes:

1. **Follow Established File Structure**: Each service has its own organization pattern - study existing structure before adding files.
2. **Error Handling Consistency**: Check how errors are defined and propagated in each service; follow the same pattern.
3. **Type Definitions**: Place types in designated locations. See existing files for guidance.
4. **API Patterns**: Match existing API design patterns.
5. **Configuration Management**: Follow established environment/config patterns per service.
6. **Documentation**: Update all relevant `README.md` files and docs after any architectural or workflow changes.

### Code Quality & Standards
- Naming conventions, error handling, and code placement must follow existing patterns for each service.
- Always produce code that is linted and formatted according to the service standard: Python -> Ruff/Black, Rust -> `cargo clippy`/`rustfmt`, TypeScript -> `npm run lint`/Prettier if present.
- Respect language/runtime versions used in the repo (e.g., Rust 1.90). Mention version constraints in PR descriptions when changes require tool updates.
- Provide inline doc comments for complex flows. Keep comments concise and add TODOs only when necessary.
- Security: never include credentials in code or docs. Use `.env` and/or CI secrets. Point to where secrets are expected to be configured. Mention security concerns throughout the code when relevant.

### Modern Technology Standards
- Prioritize latest stable versions and industry best practices.
- Use contemporary patterns modern patterns.
- Avoid deprecated approaches - research current standards before suggesting solutions.
- Gather debugging information systematically rather than making assumptions. Do not go in repeated loops.
- Always prefer professional, up-to-date solutions and avoid legacy patterns.

### Environment Configuration
- There is a single root `.env` for local development. Check its values for environment-sensitive settings (hosts, ports, model names). 
- Check where those values are used in each service to ensure consistency.
- Environmental variables are also used in CI / CD workflows and in Dockerfiles for containers and deployment.
- When adding / removing / updating env vars, make sure it is consistent with all places in the codebase (code, tests, CI / CD, Dockerfiles, Docs).

## Key Files and Codebase Awareness
- Do NOT rely on hardcoded file paths or locations; the file structure may change during development.
- Agents must always be up to date with the codebase by reading and analyzing the latest project state before making suggestions or edits.
- For any question or task related to a specific service (ai-service, backend, frontend), always scan and read the corresponding directory and its files to understand the current structure, key files, and conventions.
- When providing answers, code changes, or architectural advice, base all recommendations on the current codebase, not on outdated or static assumptions.
