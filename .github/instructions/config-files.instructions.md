---
applyTo: "**/{Cargo.toml,pyproject.toml,package.json,.editorconfig,.gitignore,.env.example,clippy.toml}"
---

# Configuration Files Instructions

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

When adding new environment variables:

1. Document in `.env.example` with description
2. Update `docker-compose.yml` if needed for containers
3. Update service loaders (check main entry points for each service)
4. Update CI workflows if build/test-related

**Variable patterns:**
- Frontend requires `VITE_*` prefix for Vite access
- Check `.env.example` for current naming conventions

## Key Configuration Files

- `.env.example` — Environment variable reference (copy to `.env` locally)
- `backend/Cargo.toml` — Check for binary name, edition, lints
- `ai-service/pyproject.toml` — Check for Python version and PDM setup
- `frontend/package.json` — Check for scripts and tech stack versions
- `clippy.toml` — Rust linter config for test exceptions
- `.editorconfig` — Editor formatting settings

After changes, run service tests and verify `.env.example` is updated.

**After config changes:** 
- Run service-specific tests: `cargo test`, `make test`, `npm run build`
- Verify no behavior changes unless intended
- Check that `.env.example` is updated if env vars changed
