# 🚀 Backend Service (Rust)

The **Backend Service** acts as an intermediary layer between the AI Service and the web-service frontend.

## Intended Functionalities

- **Request Routing:** Redirects and manages API calls between the web frontend and the AI Service.
- **Validation:** Ensures that incoming requests are well-formed and meet expected criteria.
- **Authentication & Authorization:** Verifies user identity and permissions before processing requests.
- **Extensibility:** Serves as a foundation for adding more advanced features such as rate limiting, monitoring, and analytics.

> **Note:** While some of these features (authentication, etc.) are not yet implemented, they represent the intended direction and architectural purpose of the backend service.

This backend is designed to be modular and extensible making it easy to evolve as the needs of projects grow.

## Examples

- Using Cargo (local development):

```bash
cargo run
```

You need to make sure the `ai-service` is also up and running.

- Using Docker Compose:

```bash
docker compose build backend
docker compose up -d --wait backend
```

### HTTP

You can check the [HTTP Requests](requests.http) for http examples.

### CURL

- Ingest a GitHub repository

```bash
curl -X POST http://localhost:8080/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "github_url": "https://github.com/octocat/Hello-World.git"
  }'
```

- Ask a question about a repository

```bash
curl -X POST http://localhost:8080/v1/answer \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How does authentication work in this codebase?",
    "canonical_github_url": "https://github.com/octocat/hello-world.git"
  }'
```

- Ask a general question (no repository context)

```bash
curl -X POST http://localhost:8080/v1/answer \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Hello, how are you?"
  }'
```
