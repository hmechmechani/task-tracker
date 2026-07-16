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
Expect 28 passed.

## CI

`.github/workflows/ci.yml` runs on every push (any branch) and on pull requests targeting `main`. It checks out the repo, sets up a pinned Python 3.11, installs dependencies from `requirements.txt`, and runs `pytest -v`.

## Mid-course project docs
See `docs/midcourse/` for user stories, the mini-ADR, the AI prompt log, verification evidence, and the reflection for this checkpoint.
