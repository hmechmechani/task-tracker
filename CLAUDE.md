# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

FastAPI backend + static-HTML frontend for a Task Tracker, built incrementally as an AI-Assisted Coding course project (currently mid-course). In-memory storage only — no database.

## Tech stack

Python 3.11 (target) / 3.13 installed locally in `venv`, FastAPI, Pydantic v2, Uvicorn, pytest, httpx, vanilla JavaScript frontend (no framework, no build step).

## Commands

```bash
# Setup
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run backend (serves at http://127.0.0.1:8000, docs at /docs)
uvicorn app.main:app --reload --port 8000

# Run all tests (expect 28 passed)
pytest -v

# Run a single test file / test
pytest tests/test_tasks.py
pytest tests/test_tasks.py::test_patch_invalid_transition_todo_to_done_returns_422

# Frontend: no build step — open frontend/index.html directly in a browser
# with the backend already running.
```

There is no linter or formatter configured in this repo.

## Architecture

**Backend** (`app/`) is a 3-layer FastAPI app with a clean separation that new endpoints/fields should follow:
- `models.py` — Pydantic schemas (`TaskCreate`, `TaskUpdate`, `TaskResponse`, `TaskStatus`, `TaskPriority`) and field-level validation (title trimming/length, tag cleaning via `_validate_tags`). All models use `extra="forbid"` — unknown fields are rejected with 422.
- `business_rules.py` — domain rules that don't belong to a single field: `validate_status_transition` (raises `HTTPException` directly) and `is_task_overdue`. New cross-field or derived-value logic belongs here, not in `storage.py` or `main.py` — see the mini-ADR rationale in `docs/midcourse/mini-adr.md`.
- `storage.py` — in-memory persistence (`_tasks: dict[str, TaskResponse]`), pure CRUD, no HTTP concerns. `_hydrate_task` recomputes derived fields (currently `is_overdue`) on every read so they're never stale in storage. `_reset()` is test-only, used by the `_reset_storage` autouse fixture in `tests/conftest.py`.
- `main.py` — routes only. Status-transition validation happens in the route handler (fetches existing task, calls `validate_status_transition`) before delegating to `storage.update_task`.

Status transitions are a explicit whitelist in `business_rules.VALID_TRANSITIONS`: ToDo→InProgress, InProgress→Done, Done→InProgress. Any other transition (including no-op same-status) is rejected with 422. Extending the workflow means adding tuples there, not branching logic elsewhere.

`is_overdue` is always derived (from `due_date` + `status`), never stored as truth — it's recomputed against "today" on every read/hydrate, so a task can flip overdue state without being written to.

**Frontend** (`frontend/index.html`) is a single static file, no build step, no framework. It calls the backend directly via `fetch` against `BASE_URL = "http://localhost:8000"` hardcoded in the file. CORS in `main.py` is locked to `http://127.0.0.1:5500` / `http://localhost:5500` (VS Code Live Server default) — if the frontend is served from a different origin/port, update `allow_origins` in `main.py`.

**Tests** (`tests/`) use `fastapi.testclient.TestClient` against the real `app` object with in-memory storage reset before/after every test (autouse fixture in `conftest.py`). `created_task` fixture posts a minimal task and returns its JSON body for tests that need an existing task. `tests/verify_a.py` is a standalone manual verification script (run directly with `python`, not via pytest) predating the pytest suite — prefer adding new coverage to `tests/test_tasks.py`.

## UI states

`frontend/index.html` tracks a single `state` variable (`loading | ready | empty | error`, set in `fetchTasks()` and rendered by `setState()`):
- **Loading** — shown on initial page load and every `fetchTasks()` call (including filter changes and retries): a "Loading tasks..." status message above the board.
- **Ready** — `fetchTasks()` succeeded and returned at least one task: tasks render into their status columns; no banner is shown by default (only transient success/error messages from drag-and-drop moves).
- **Empty** — `fetchTasks()` succeeded but returned zero tasks (none exist, or none match the active tag/overdue filter): no global banner by default, but each column shows a "No tasks" placeholder.
- **Error** — `fetchTasks()` failed (network error or non-OK response): shows the error message plus a "Retry" button that re-calls `fetchTasks()`; the board still renders underneath (empty).

## Mid-course project docs

`docs/midcourse/` contains user stories, a mini-ADR explaining the due-date/overdue and tags/labels feature decisions, an AI prompt log, verification evidence, and a reflection — check the mini-ADR before changing how derived fields or filters are structured, since it documents rejected alternatives.

## Do-not rules

Do not do the following without asking first:
- Add authentication
- Add a database
- Add deployment steps or infrastructure
- Make major UI changes
