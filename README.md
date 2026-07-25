# Task Tracker

FastAPI backend + static-HTML frontend for the AI-Assisted Coding course Task Tracker project. Full CRUD, due dates with an overdue filter, tags/labels, and a Kanban-style drag-and-drop board.

## Setup

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run

### Backend
```bash
uvicorn app.main:app --reload
```
API runs at `http://127.0.0.1:8000` (docs at `/docs`).

### Frontend
The backend's CORS policy (see `app/main.py`) only allows requests from `http://127.0.0.1:5500` and `http://localhost:5500`, so `frontend/index.html` must be served from one of those origins — opening the file directly in a browser (`file://`) will not work.

1. From the `frontend/` directory, serve it on port 5500:
   ```bash
   cd frontend
   python -m http.server 5500
   ```
   (or any equivalent local server on that port/origin, e.g. the VS Code "Live Server" extension, which defaults to port 5500)
2. Open `http://127.0.0.1:5500` (or `http://localhost:5500`) in a browser, with the backend already running.

## Run with Docker

Build the image:
```bash
docker build -t task-tracker:dev .
```

Run the container:
```bash
docker run --rm -d -p 8000:8000 --name tt-dev task-tracker:dev
```

Verify it's up:
```bash
curl http://localhost:8000/health
```

The image is a multi-stage build on `python:3.11-slim` (see `Dockerfile`), runs as a non-root `app` user, and starts the API with `uvicorn app.main:app --host 0.0.0.0 --port 8000`.

## Verify

```bash
curl http://localhost:8000/health
```

Example response (timestamp varies per request):
```json
{"status": "ok", "timestamp": "2026-07-12T12:00:00.000000+00:00"}
```

Swagger docs: open http://localhost:8000/docs in a browser.

## Tests

```bash
pytest -v
```
Expect 35 passed.

## CI

`.github/workflows/ci.yml` runs on every push (any branch) and on pull requests targeting `main`. It checks out the repo, sets up a pinned Python 3.11, installs dependencies from `requirements.txt`, and runs `pytest -v`.

## Mid-course project docs
See `docs/midcourse/` for user stories, the mini-ADR, the AI prompt log, verification evidence, and the reflection for this checkpoint.

## Technical decisions
See `docs/decisions/in-memory-task-storage.md` for the decision note on using an in-memory dict as the task storage layer.

## Final Project

Branch reviewed: final-project

### What this submission demonstrates
- Existing Task Tracker app still runs inside the intended course scope.
- CI runs the pytest suite on push and/or pull request.
- Docker image builds and runs with /health returning 200.
- AI review, security, and ownership evidence is in docs/.

### How to run locally
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
API runs at `http://127.0.0.1:8000` (docs at `/docs`).

### How to run tests
```bash
pytest -v
```

### How to run with Docker
```bash
docker build -t task-tracker:dev .
docker run --rm -d -p 8000:8000 --name tt-dev task-tracker:dev
curl http://localhost:8000/health
```

### Evidence files
- docs/release-evidence.md
- docs/final-ai-review.md
- docs/ai-playbook.md

### AI assistance summary
AI helped draft or review: CI, Docker, docs, security, debugging.
I verified the work by: tests, diff review, Docker /health checks, and manual scans.
One AI suggestion I rejected or corrected: The original AI-assisted `TaskUpdate.title` validator in `app/models.py` silently returned `None` unchanged when a client sent `{"title": null}` in a PATCH request, even though `TaskResponse.title` requires a non-null string. A Module 4 documentation audit caught this contract violation; I corrected the validator to explicitly raise `ValueError("title cannot be null")`, added a regression test (`test_patch_title_null_returns_422`), and verified the fix with `pytest -v`.