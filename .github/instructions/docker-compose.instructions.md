---
applyTo: "docker-compose.yml,**/Dockerfile"
---

# Docker & Deployment Instructions

## Service Architecture

**Infrastructure:**
- `mongo` — Backend DB storage.

**Application:**
- `ai-service` — Python RAG engine.
- `backend` — Rust backend API gateway connecting frontend and ai-service.
- `frontend` — React / TS frontend server.

## Key Files

- `docker-compose.yml` — Service definitions, check for ports, volumes, and health checks.
- `ai-service/Dockerfile` — Multi-stage Python build reference for the ai service.
- `backend/Dockerfile` — Multi-stage Rust build reference for the backend service.
- `frontend/Dockerfile` — Multi-stage React / TypeScript build reference for the frontend service.

## Environment Configuration

- Docker Compose uses `.env.docker` (copy from `.env.docker.example`). Used by `docker-compose.yml` for containerized environments.
- Contains Docker internal networking for inter-container communication with internal DNS names.
- Different from `.env` for local development which uses `localhost`.

## Image Tagging Strategy

Application images are published to GitHub Container Registry (GHCR) by CI/CD:

- **Tags**: Each successful main branch build creates two tags:
  - `sha-<commit>` — Immutable reference to specific commit (e.g., `sha-abc1234`).
  - `latest` — Always points to the most recent main branch build.

## Best Practices

- Use multi-stage builds to minimize image size.
- **Base images in Dockerfiles**: Pin versions (e.g., `python:3.10-slim`, `node:22.20.0-alpine`) to ensure reproducible builds and avoid breaking changes from upstream updates.
- **Application images in docker-compose.yml**: Use `:latest` tag which points to the most recent build from the main branch (published by CI/CD with both `sha` and `latest` tags).
- Add healthchecks for critical services with `depends_on: service_healthy` or `depends_on: service_started` accordingly.
- Mount volumes for persistent data if necessary.

Check existing Dockerfiles for consistency.
