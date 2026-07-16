# Docker Security Log — Task Tracker

| Check | Evidence |
|---|---|
| Non-root user | `docker exec tt-dev whoami` → `app` |
| Slim runtime base | Runtime stage uses `python:3.11-slim` (explicit version, not `latest`) |
| No baked secrets | `.dockerignore` excludes `.env`, `.git`, `venv/`, `.venv/`, caches, and build artifacts |

## Additional verification
- Build: `docker build -t task-tracker:dev .` — succeeded, 14/14 steps.
- Run: `docker run --rm -d -p 8000:8000 --name tt-dev task-tracker:dev` — started successfully.
- Health check: `curl -i http://localhost:8000/health` → `HTTP/1.1 200 OK`, `{"status":"ok","timestamp":"..."}`.
- Image size: 258MB disk usage / 61.2MB unique content layer.