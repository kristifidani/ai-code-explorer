---
applyTo: "docker-compose.yml,**/Dockerfile"
---

# Docker & Deployment Instructions

## Service Architecture

**Infrastructure:**
- `ollama` — LLM inference with healthcheck
- `mongo` — Backend storage

**Application:**
- `ai-service` — Python RAG engine (waits for Ollama health)
- `backend` — Rust API gateway (check if Docker image exists)
- `frontend` — React dev server (check if Docker image exists)

Check `docker-compose.yml` for current ports and service dependencies.

## Best Practices

- Use multi-stage builds to minimize image size
- Pin base image versions, avoid `:latest`
- Add healthchecks for critical services with `depends_on: service_healthy`
- Mount volumes for persistent data

Check `ai-service/Dockerfile` for multi-stage build pattern.

## Key Files

- `docker-compose.yml` — Service definitions, check for ports, volumes, and health checks
- `ai-service/Dockerfile` — Multi-stage Python build reference
- `backend/Dockerfile` — Check if implemented
- `frontend/Dockerfile` — Check if implemented
