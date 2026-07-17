# Task Tracker Architecture (Strategy A: Minimal Context)

## 1. What the app does

Task Tracker is a small FastAPI + static HTML/JavaScript app for managing tasks on a Kanban-style board. Users can create, view, update, delete, filter, and move tasks through `ToDo`, `InProgress`, and `Done`, with support for priorities, assignees, due dates, overdue detection, and tags.

## 2. Data model

The core entity is `Task`. Important fields are `id`, `title`, `description`, `status`, `priority`, `assignee`, `due_date`, `tags`, `is_overdue`, `created_at`, and `updated_at`. `status` is one of `ToDo`, `InProgress`, or `Done`; `priority` is one of `Low`, `Medium`, or `High`. Creation and update payloads are validated with Pydantic models, while API responses use `TaskResponse`.

## 3. Request flow

When a user creates a task, the frontend form builds a JSON payload and sends `POST /tasks` to the FastAPI backend at `http://localhost:8000`. FastAPI validates the request against `TaskCreate`; invalid data returns `422`. The route calls `storage.add_task`, which generates a UUID, sets UTC timestamps, computes `is_overdue`, stores the task in the module-level `_tasks` dictionary, and returns the created task with HTTP `201`.

## 4. Key files

- `README.md` - setup, run, Docker, test, and project overview.
- `app/main.py` - FastAPI app, CORS policy, health check, and task CRUD routes.
- `app/models.py` - Pydantic models, enums, and validation rules.
- `app/storage.py` - in-memory task storage and filtering/update helpers.
- `app/business_rules.py` - status transition and overdue rules.
- `frontend/index.html` - static frontend UI, fetch calls, Kanban board, modal form, filters, and drag/drop.
- `tests/test_tasks.py` - API and business-rule behavior tests.
- `tests/conftest.py` - test client setup and storage reset fixture.
- `docs/decisions/in-memory-task-storage.md` - decision note for non-persistent in-memory storage.
- `Dockerfile` - container build and API startup definition.

## 5. Conventions

Validation is handled mostly by Pydantic and FastAPI: unknown fields are forbidden, titles are trimmed and required on creation, tags are trimmed and limited, enums constrain status and priority, and bad request shapes return `422`. Storage is a single in-process Python dictionary, so tasks are lost when the server restarts. Error handling uses FastAPI `HTTPException` for `404` missing tasks and `422` invalid status transitions. The frontend is static vanilla JavaScript and talks directly to the backend with `fetch`; CORS allows only `http://127.0.0.1:5500` and `http://localhost:5500`.

## 6. Not visible or assumptions

Authentication, authorization, persistent storage, multi-user behavior, production deployment, database migrations, and frontend build tooling are not visible in the inspected files. Horizontal scaling is not supported by the confirmed in-memory storage design. No linter or formatter command was confirmed.

---

**Files inspected:** `README.md`, `app/main.py`, `app/models.py`, `app/storage.py`, `app/business_rules.py`, `frontend/index.html`, `tests/test_tasks.py`, `docs/decisions/in-memory-task-storage.md`, plus repo file listing.

**Assumptions or possible inventions:** No invented behavior beyond inspected files. The only inferred statement is that horizontal scaling is unsupported, based on the confirmed module-level in-memory dictionary.
