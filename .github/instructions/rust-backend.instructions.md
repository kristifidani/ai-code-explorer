---
applyTo: "backend/**/*.rs"
---

# Rust Backend Instructions

## Critical Conventions

**Error Handling:**
- No `unwrap()`/`expect()` in production code (clippy enforced)
- Handlers return `Result<impl Responder>` with custom error types
- Errors convert to `ApiResponse<T>` wrapper with HTTP status

**Response Pattern:**
- All responses use `ApiResponse<T>` wrapper
- Check `types/response.rs` for implementation details

**Dependency Injection:**
- External clients use trait abstractions for testability
- See `clients/` for implementation details

**Testing:**
- `rstest` for parameterized tests, `mockito` for HTTP mocks
- Tests can use unwrap/expect (check `clippy.toml`)

## Key Files

- `bin/main.rs` — Server entry point
- `src/app_config.rs` — Route definitions
- `src/error.rs` — Error types with HTTP status mapping
- `src/handlers/` — Request handlers
- `src/types/external.rs` — Frontend API contracts
- `src/types/internal.rs` — AI Service API contracts
- `Cargo.toml` — Check for binary name, edition, Rust version

For more details and complete overview read the `backend/README.md` and scan the tree structure.
