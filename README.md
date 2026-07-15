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
