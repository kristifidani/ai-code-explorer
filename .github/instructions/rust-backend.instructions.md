---
applyTo: "backend/**/*.rs"
---

# Rust Backend Instructions

## Critical Conventions

**Error Handling:**
- Never `unwrap()` or `expect()` in production code (enforced by clippy lints). Allowed in tests.
- All handlers return `Result<impl Responder>` using `ApiError` enum from `src/error.rs`
- Use `?` operator for error propagation

**Testing:**
- Use `rstest` for parameterized tests
- Use `mockito` for HTTP mocking in integration tests
- Tests in `tests/` directory can use unwrap/expect (allowed via `clippy.toml`)

## Key Files

- `bin/main.rs` — Server entry point
- `src/error.rs` — Error types
- `src/app_config.rs` — Route configuration
- `src/handlers/` — Request handlers
- `src/clients/` — External clients with trait abstractions
- `src/types/` - Type definitions
- `Cargo.toml` — Configuration and dependencies

**For implementation details:** Read existing code to understand file relationships and development patterns. Keep it consistent.
