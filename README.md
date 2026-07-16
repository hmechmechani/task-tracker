# Task Tracker API (Module 1 skeleton)

Minimal FastAPI foundation for the AI-Assisted Coding course Task Tracker project.

## Scope (Module 1)
This is a skeleton only: one `/health` endpoint. No CRUD, no auth, no database.
Full CRUD, data models, and business logic are added in Module 2.

## Setup

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

## Verify

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "ok", "timestamp": "2026-07-12T12:00:00.000000+00:00"}
```

Swagger docs: open http://localhost:8000/docs in a browser.

## Running the project

### Backend
1. From the project root: `pip install -r requirements.txt`
2. Start the API: `uvicorn app.main:app --reload`
3. API runs at `http://127.0.0.1:8000` (docs at `/docs`).

### Frontend
1. Open `frontend/index.html` directly in a browser (double-click, or right-click → Open With), with the backend already running.
2. No build step or server needed — it's a single static file that calls the backend API directly.

### Tests
1. From the project root: `pytest`
2. Expect 28 passed.

## Mid-course project docs
See `docs/midcourse/` for user stories, the mini-ADR, the AI prompt log, verification evidence, and the reflection for this checkpoint.
