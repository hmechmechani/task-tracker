# Release Evidence

## Baseline

- Branch: `final-project`
- Date: 2026-07-17
- Local app run command: `uvicorn app.main:app --reload`
- /health result: `{"status":"ok","timestamp":"2026-07-17T14:13:42.675881+00:00"}` (HTTP 200)
- Frontend check: Served via `python -m http.server 5500` from the `frontend/` directory, opened at `http://127.0.0.1:5500`. Kanban board renders and the create/edit modal opens correctly.
- Test command: `pytest -v`
- Test result: 29 passed, 4 warnings, in 1.18s. No failures. Warnings are pre-existing deprecation notices (`httpx`/`starlette.testclient`, `HTTP_422_UNPROCESSABLE_ENTITY`), not errors, and not introduced by final project work.

## CI evidence

- Workflow file: `.github/workflows/ci.yml`
- Latest run link or note: [to be added after final-project branch CI run — paste GitHub Actions run URL]
- Test command used by CI: `pytest -v`
- Shortcut check: no `continue-on-error`, no `|| true`, pytest is not skipped, Python version is pinned to 3.11, dependencies are installed from `requirements.txt` before tests run.

## Docker evidence

- Build command: `docker build -t task-tracker:dev .`
- Run command: `docker run --rm -d -p 8000:8000 --name tt-dev task-tracker:dev`
- /health check: `curl http://localhost:8000/health` → `{"status":"ok",...}` (HTTP 200)
- Non-root check: Dockerfile creates and runs as a non-root `app` user (`USER app` before `CMD`).
- No-baked-secrets check: `.dockerignore` excludes `.env`, `.git`, `venv/`, `__pycache__/`, and other local-only files from the build context; no secrets are copied into the image.

## Documentation claim-vs-reality log

| Claim checked | Evidence used | Result | Change made, if any |
|---|---|---|---|
| README said "Expect 28 passed" for the test suite | Ran `pytest -v` directly | Actual count was 29, not 28 — claim was stale even before any new work | Fixed README to say "Expect 29 passed" (Module 5, commit `2feff60`) |
| `TaskUpdate.title` accepts `null` without error (implied by no explicit rejection in early docs) | Sent `PATCH /tasks/{id}` with `{"title": null}` directly | Claim was false — endpoint correctly rejects with 422; this was fixed in Module 4 after being caught by a documentation audit | Added `test_patch_title_null_returns_422` regression test (Module 4) |
| AGENTS.md claim that `tags` validation allows max 5 tags, 30 characters each, trimmed, blank rejected | Read `app/models.py` `_validate_tags` function directly | Confirmed accurate — matches code exactly | None needed |
