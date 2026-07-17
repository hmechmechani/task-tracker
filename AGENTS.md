# AGENTS.md

Repository guidance for Codex App agents working on the Module 5 Task Tracker repo.

## Project Summary

This repository is a course project for a Task Tracker application. It contains a FastAPI backend plus a single-file static HTML/JavaScript frontend.

The backend exposes task CRUD routes, health checking, filtering by status/priority/overdue/tag, status-transition validation, due-date overdue calculation, and in-memory task storage. The frontend is a vanilla JavaScript Kanban-style board that calls the API directly.

Storage is an in-process dictionary in `app/storage.py`. Data is not persisted to disk or a database, and restarting the server clears tasks.

## Tech Stack

- Python 3.11 target, confirmed by `Dockerfile` and `.github/workflows/ci.yml`.
- FastAPI API app in `app/main.py`.
- Pydantic v2 models and validation in `app/models.py`.
- Uvicorn ASGI server.
- pytest and FastAPI TestClient/httpx for tests.
- Vanilla HTML/CSS/JavaScript frontend in `frontend/index.html`.
- Docker image based on `python:3.11-slim`.

No linter, formatter, package manager lockfile, or frontend build step is confirmed in the repo.

## Supported Commands

Setup:

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Run the backend:

```bash
uvicorn app.main:app --reload
```

The API runs at `http://127.0.0.1:8000`; Swagger docs are at `/docs`.

Run the frontend:

```bash
cd frontend
python -m http.server 5500
```

Then open `http://127.0.0.1:5500` or `http://localhost:5500` with the backend already running. Opening `frontend/index.html` directly via `file://` is not confirmed to work because the frontend uses `fetch()` and the backend CORS allowlist is limited to port 5500 origins.

Run tests:

```bash
pytest -v
```

Run a single test file:

```bash
pytest tests/test_tasks.py
```

Run the standalone verification script, if needed:

```bash
python tests/verify_a.py
```

Docker build/run:

```bash
docker build -t task-tracker:dev .
docker run --rm -d -p 8000:8000 --name tt-dev task-tracker:dev
curl http://localhost:8000/health
```

CI is confirmed in `.github/workflows/ci.yml`: it installs `requirements.txt` on Python 3.11 and runs `pytest -v`.

Lint and format commands: not confirmed.

## Business Rules Visible in Code

Task statuses are defined in `app/models.py`:

- `ToDo`
- `InProgress`
- `Done`

Task priorities are defined in `app/models.py`:

- `Low`
- `Medium`
- `High`

Task creation defaults:

- `status` defaults to `ToDo`.
- `priority` defaults to `Medium`.
- `description` defaults to an empty string.
- `assignee` defaults to `None`.
- `due_date` defaults to `None`.
- `tags` defaults to an empty list.

Validation rules visible in `app/models.py`:

- Unknown fields are forbidden on `TaskCreate`, `TaskUpdate`, and `TaskResponse`.
- `TaskCreate.title` is required, trimmed, must be a string, cannot be blank, and must be 200 characters or fewer.
- `TaskUpdate.title` may be omitted, but if provided cannot be `null`, blank, non-string, or longer than 200 characters.
- `tags` must be a list of strings.
- Tags are trimmed.
- Tags cannot contain blank values.
- A task can have at most 5 tags.
- Each tag must be 30 characters or fewer.
- Invalid enum values for status or priority are rejected by FastAPI/Pydantic.
- `due_date` is an optional date-only field; invalid dates are rejected by FastAPI/Pydantic.

Status transition rules visible in `app/business_rules.py`:

- `ToDo -> InProgress` is allowed.
- `InProgress -> Done` is allowed.
- `Done -> InProgress` is allowed.
- All other transitions are rejected with HTTP 422, including same-status updates and `ToDo -> Done`.

Overdue rules visible in `app/business_rules.py` and `app/storage.py`:

- A task is overdue when it has a `due_date` before today's date and its status is not `Done`.
- A task with no `due_date` is not overdue.
- A task due today or in the future is not overdue.
- A `Done` task is not overdue.
- `is_overdue` is derived and recomputed on reads/hydration; it is not treated as durable stored truth.

API behavior visible in `app/main.py` and tests:

- `GET /health` returns `{"status": "ok", "timestamp": ...}`.
- `GET /tasks` supports optional `status`, `priority`, `overdue`, and `tag` filters.
- `GET /tasks/{task_id}` returns 404 when the task does not exist.
- `POST /tasks` creates a task and returns 201.
- `PATCH /tasks/{task_id}` partially updates a task and returns 404 when the task does not exist.
- `DELETE /tasks/{task_id}` returns 204 for an existing task and 404 for a missing task.

Authentication, authorization, persistent storage, multi-user behavior, and production deployment behavior are not confirmed.

## Module 5 Guardrails

- Docs-first: inspect README, docs, tests, and existing implementation before proposing changes.
- Read-only by default: prefer analysis, explanation, and citations unless the user explicitly asks for edits.
- One task per thread: keep each Codex thread focused on a single requested task.
- Do not change files under `app/` unless the user explicitly approves that scope.
- For Module 5 work, prefer documenting findings and constraints before modifying behavior.
- If a command, rule, or feature is not visible in the repository, mark it as "not confirmed" instead of inferring it.

## Security and Governance Reminders

- Do not paste, expose, or invent secrets, tokens, credentials, private URLs, or environment values.
- Do not run destructive commands such as recursive delete, force reset, or cleanup scripts unless the user explicitly asks and the target is verified.
- Do not invent findings. Ground claims in files that were actually inspected.
- Cite repository files when making claims about behavior, commands, or architecture.
- Preserve user work. Do not revert unrelated changes.
- Keep edits scoped to the user's request.
- Treat the in-memory storage as non-production and non-durable.
- If tests are not run, say so clearly.
