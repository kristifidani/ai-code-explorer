---
applyTo: "**/{Cargo.toml,pyproject.toml,package.json,.editorconfig,.gitignore,.env.example,clippy.toml}"
---

# Configuration Files Instructions

## Adding Dependencies

**Rust (backend):**
- Edit `backend/Cargo.toml`
- Prefer `default-features = false` to minimize bloat
- Test with `cargo build` and `cargo test`

**Python (ai-service):**
- Use `pdm add <package>` in `ai-service/`
- For dev dependencies: `pdm add -d <package>`
- Test with `make test`

**Frontend:**
- Use `npm install <package>` in `frontend/`
- For dev dependencies: `npm install -D <package>`
- Test with `npm run build`

## Environment Variables

When adding new environment variables:
1. Document in `.env.example` with description (never commit `.env`)
2. Update `docker-compose.yml` if needed for containerized deployment
3. Update service config loaders (usually the main files of each service)
4. Update CI workflows if build-related (`.github/workflows/`)

## Key Configuration Files

- `.env.example` — All environment variables with descriptions
- `backend/Cargo.toml` — Rust config
- `ai-service/pyproject.toml` — Python config
- `frontend/package.json` — npm config
- `clippy.toml` — Allows unwrap/expect in tests only
- `.editorconfig` — Editor formatting (4-space Rust, 100 char limit, LF endings)

**After config changes:** Always test the build and ensure tests still pass and the bevavior is unchanged.
