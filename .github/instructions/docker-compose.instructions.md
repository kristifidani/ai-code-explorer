---
applyTo: "docker-compose.yml,**/Dockerfile"
---

# Docker & Deployment Instructions

## Service Architecture

**Infrastructure:**
- `ollama` — LLM inference with healthcheck
- `mongo` — Backend storage

**Application:**
- `ai-service` — Python RAG engine
- `backend` — Rust backend API gateway
- `frontend` — React frontend server

Check `docker-compose.yml` for current ports, service dependencies and more details.

## Best Practices

- Use multi-stage builds to minimize image size.
- Pin base image versions to the current version we are using locally, avoid `:latest`.
- Add healthchecks for critical services with `depends_on: service_healthy` or `depends_on: service_started` accordingly.
- Mount volumes for persistent data if necessary.

Check existing Dockerfiles for multi-stage build pattern.

## Key Files

- `docker-compose.yml` — Service definitions, check for ports, volumes, and health checks.
- `ai-service/Dockerfile` — Multi-stage Python build reference for the ai service.
- `backend/Dockerfile` — Multi-stage Rust build reference for the backend service.
- `frontend/Dockerfile` — Multi-stage React / TypeScript build reference for the frontend service.
