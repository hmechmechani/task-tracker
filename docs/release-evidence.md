# Release Evidence

## Baseline

- Branch: `final-project`
- Date: 2026-07-25 (re-verified after the second round of instructor feedback)
- Local app run command: `uvicorn app.main:app --reload`
- /health result: `{"status":"ok","timestamp":"2026-07-17T14:13:42.675881+00:00"}` (HTTP 200)
- Frontend check: Served via `python -m http.server 5500` from the `frontend/` directory, opened at `http://127.0.0.1:5500`. Kanban board renders and the create/edit modal opens correctly.
- Test command: `pytest -v`
- Test result: 35 passed, 4 warnings, in 0.57s. No failures. Warnings are pre-existing deprecation notices (`httpx`/`starlette.testclient`, `HTTP_422_UNPROCESSABLE_ENTITY`), not errors, and not introduced by final project work.
- Test count history: the suite was 29 tests at the original baseline. Two regression tests were added for wrong-type `title`/`tags` input, and four more for explicit-`null` input on `description`/`status`/`priority`/`tags`, bringing the current total to 35. Both additions are documented under "Documentation claim-vs-reality log" below.

## CI evidence

- Workflow file: `.github/workflows/ci.yml`
- Green run for the final code-affecting commit `f2a7bc8`: https://github.com/hmechmechani/task-tracker/actions/runs/30178052135 (green, on `final-project`, running the full 35-test suite)
- Full CI history for this branch (every commit's run, including any commit made after the one above): https://github.com/hmechmechani/task-tracker/actions?query=branch%3Afinal-project
- Note on the final commit: `f2a7bc8` is the last commit that changes application code or tests. Any commit after it on this branch is a documentation-only update to this file, so it cannot itself cite its own future run ID. Its green run is visible at the branch history link above, and it does not alter the code the run above validated.
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
| README said "Expect 29 passed" after regression tests were added | Ran `pytest -v` directly | Stale again — actual count was 35 after two rounds of regression tests were added | Fixed README to say "Expect 35 passed" (commit `f2a7bc8`) |
| `TaskUpdate.title` accepts `null` without error (implied by no explicit rejection in early docs) | Sent `PATCH /tasks/{id}` with `{"title": null}` directly | Claim was false — endpoint correctly rejects with 422; this was fixed in Module 4 after being caught by a documentation audit | Added `test_patch_title_null_returns_422` regression test (Module 4) |
| Malformed `tags` input returns a clean 422 | Sent `POST /tasks` with `{"tags": "urgent"}` against the running app | Claim was false — returned an unhandled 500. Root cause: validators raised `TypeError`, which Pydantic v2 does not guarantee to catch (only `ValueError`/`AssertionError`), combined with unpinned dependency drift | Changed all `raise TypeError` to `raise ValueError` in `app/models.py`, pinned `requirements.txt`, added 2 regression tests (commit `68f9faa`) |
| Explicit `null` for `description`/`status`/`priority`/`tags` on PATCH is rejected | Sent `PATCH /tasks/{id}` with `{"status": null}`, then a follow-up `PATCH {"status": "InProgress"}` against the running app | Claim was false — the first PATCH returned 200 and wrote `None` into storage (`model_copy` does not re-validate), and the follow-up request then crashed with `AttributeError: 'NoneType' object has no attribute 'value'` → HTTP 500 | Added explicit null-rejecting validators for `description`, `status`, and `priority`, and made `_validate_tags` reject `None`; added 4 regression tests including two that assert the task is not corrupted after a rejected update (commit `f2a7bc8`) |
| AGENTS.md claim that `tags` validation allows max 5 tags, 30 characters each, trimmed, blank rejected | Read `app/models.py` `_validate_tags` function directly | Confirmed accurate — matches code exactly | None needed |