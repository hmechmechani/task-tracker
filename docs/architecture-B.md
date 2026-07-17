# Task Tracker Architecture (Strategy B: Structured Context)

## 1. What the app does

Task Tracker is a course-project task management app with a FastAPI backend and a single-file vanilla JavaScript frontend. It lets users create, view, update, delete, filter, and move tasks across a Kanban-style board while enforcing task validation, allowed status transitions, and overdue-date rules.

## 2. Data model

The main entity is a task. Important fields include `title`, `description`, `status`, `priority`, `assignee`, `due_date`, `tags`, and derived `is_overdue`.

Supported statuses are `ToDo`, `InProgress`, and `Done`. Supported priorities are `Low`, `Medium`, and `High`. New tasks default to `ToDo` status, `Medium` priority, empty description, no assignee, no due date, and an empty tag list.

## 3. Request flow

When a user creates a task in the frontend, the modal form collects task details and sends them to the backend with a `POST /tasks` request. FastAPI receives the request in `app/main.py`, validates the payload through the Pydantic models in `app/models.py`, applies the app's task rules, stores the task in the in-memory dictionary managed by `app/storage.py`, and returns the created task with HTTP 201. The frontend then uses the API response to update the Kanban board.

## 4. Key files

- `app/main.py`: FastAPI app setup, CORS policy, health check, and task CRUD routes.
- `app/models.py`: Pydantic v2 task models, enums, field validation, and forbidden unknown fields.
- `app/business_rules.py`: Allowed status transitions and overdue-date calculation.
- `app/storage.py`: In-memory dictionary-backed task storage, filtering, hydration, and update helpers.
- `frontend/index.html`: Single-file vanilla JavaScript Kanban UI, fetch calls, drag-and-drop, and modal form.
- `tests/test_tasks.py`: Pytest coverage for CRUD, validation, transitions, filters, and overdue behavior.
- `tests/conftest.py`: FastAPI TestClient fixture and storage reset between tests.
- `Dockerfile`: Python 3.11 slim container image with non-root runtime user.
- `.github/workflows/ci.yml`: CI workflow that installs dependencies and runs `pytest -v`.

## 5. Conventions

Validation is centralized in the Pydantic models. Task titles are trimmed, required on create, limited to 200 characters, and cannot be blank. Tags must be a list of nonblank strings, are trimmed, are limited to 5 per task, and each tag is limited to 30 characters. Unknown fields are rejected.

Storage is in-process and dictionary-backed. It is not persistent, so restarting the backend clears tasks. `is_overdue` is derived rather than treated as durable stored data.

Status changes are constrained by an allowlist: `ToDo -> InProgress`, `InProgress -> Done`, and `Done -> InProgress` are allowed. Other transitions, including same-status updates and `ToDo -> Done`, are rejected.

Error handling uses FastAPI HTTP responses. Missing tasks return 404, invalid payloads or invalid transitions are rejected, task creation returns 201, and successful deletion returns 204.

The frontend interacts with the backend through direct `fetch()` calls. The backend CORS allowlist is configured for the local frontend server on port 5500.

## 6. Not visible or assumptions

Authentication, authorization, persistent database storage, multi-user behavior, production deployment behavior, and frontend build tooling are not confirmed. No linter, formatter, package manager lockfile, or frontend build step is confirmed. Opening the frontend directly through `file://` is not confirmed to work because the documented flow uses a local HTTP server on port 5500.

---

**Which context item helped most:** AGENTS.md, which supplied pre-verified business rules, API behavior, validation conventions, storage limits, and "not confirmed" boundaries.

**Remaining assumptions or unsupported details:** No files were inspected directly in this run; the draft relies only on the structured context (AGENTS.md and file summaries) provided upfront. The phrase "applies the app's task rules" is intentionally broad since the exact create-time rule path was not separately described beyond the validation/storage/business-rule summaries.
