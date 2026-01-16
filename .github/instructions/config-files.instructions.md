---
applyTo: "**/{Cargo.toml,pyproject.toml,package.json,.editorconfig,.gitignore,.env.example,.env.docker.example,clippy.toml}"
---

# Configuration Files Instructions

## Key Configuration Files

- `.env.example` — Local development environment variables (copy to `.env`).
- `.env.docker.example` — Docker Compose environment variables (copy to `.env.docker`).
- `backend/Cargo.toml` — Check for binary name, edition, lints.
- `ai-service/pyproject.toml` — Check for Python version and PDM setup.
- `frontend/package.json` — Check for scripts and tech stack versions.
- `clippy.toml` — Rust linter config for test exceptions.
- `.editorconfig` — Editor formatting settings.

## Adding Dependencies

**Rust (backend):**
1. Edit `backend/Cargo.toml` in `[dependencies]` section
2. Prefer `default-features = false` to minimize binary size
3. Add specific features needed: `features = ["json", "rustls-tls"]`
4. Test: `cargo build`

**Python (ai-service):**
1. Add runtime deps: `cd ai-service && pdm add <package>`
2. Add dev deps: `pdm add -d <package>` (linters, test tools)
3. PDM updates `pyproject.toml` and `pdm.lock` automatically
4. Test: `make test`

**Frontend:**
1. Add runtime deps: `cd frontend && npm install <package>`
2. Add dev deps: `npm install -D <package>` (build tools, types)
3. npm updates `package.json` and `package-lock.json` automatically
4. Test: `npm run build`

## Environment Variables

This project uses two separate environment files:

- **`.env.example`** — Template for **local development** (copy to `.env`).
  - Used when running services directly on the host machine.
  - Default configuration for running outside Docker.

- **`.env.docker.example`** — Template for **Docker Compose** (copy to `.env.docker`).
  - Used by `docker-compose.yml` for containerized environments.
  - Contains Docker internal networking for inter-container communication.

**When adding new environment variables:**

1. Identify the scope: local-only, Docker-only, or both.
2. Add to appropriate file(s) with clear description:
   - Local development → `.env.example`
   - Docker Compose → `.env.docker.example`
   - Used in both → add to both files with appropriate values
3. Update service loaders (check main entry points for each service).
4. Update CI workflows if build/test-related.

**Variable patterns:**

- Frontend requires `VITE_*` prefix for Vite access in browser.
- Docker services use internal DNS names (e.g., `mongo`, `ai-service`, `backend`).
- Local development uses `localhost` with specific ports.

After changes, run service tests and verify both `.env.example` and `.env.docker.example` are updated if env vars changed.
