---
applyTo: "docker-compose.yml,**/Dockerfile"
---

# Docker & Deployment Instructions

## Service Architecture

The `docker-compose.yml` defines a multi-container setup:
- **ollama** — LLM inference (port 11434) with healthcheck
- **mongo** — MongoDB (port 27017) for backend storage
- **ai-service** — Python FastAPI (port 8000)
- **backend** — Rust Actix-web (port 8080) (TODO: no docker image yet)
- **frontend** — React dev server (port 5173) (TODO: no docker image yet)

## Best Practices

- Use multi-stage builds to minimize image size
- Pin specific base image versions (never `latest`)
- Use non-root users for security where possible
- Add healthchecks for critical services
- Respect `.dockerignore` to avoid unnecessary file copies

## Key Files

- `docker-compose.yml` — Service definitions, environment variables, volume mounts, networking
- `ai-service/Dockerfile`, `backend/Dockerfile`, `frontend/Dockerfile` — Build patterns for each service

**For implementation details:** Study existing Dockerfiles and keep it consistent.
