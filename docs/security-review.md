# Security Review — Task Tracker (Module 5, Part 5.2)

## Method

A read-only AI security audit was run in Codex App (prompt 5.2A) against the actual repository files (not generic FastAPI advice). Each finding was then graded Valid / False Positive / Noise (prompt 5.2B), with the "no authentication" finding specifically evaluated as a possible course-scope decision rather than an outright defect. No independent manual scan of `app/` was performed for this pass — see note below.

## AI Audit Findings

| ID | Severity | File / location | Finding | Evidence | Suggested next step | Confidence |
|---|---|---|---|---|---|---|
| SEC-01 | Medium | `app/main.py` (route handlers); `docs/decisions/in-memory-task-storage.md`; `AGENTS.md` | Task CRUD routes have no visible authentication or authorization. | Verified: no auth dependencies on any route; decision doc states no authentication; AGENTS.md marks auth as not confirmed. | Keep explicitly local/course-only, or add auth + per-user/tenant authorization before any real deployment. | High |
| SEC-02 | Medium | `app/models.py` (`description`, `assignee` fields); `app/storage.py` (`_tasks` dict) | `description` and `assignee` are optional strings with no length limits, stored in-process. | Verified against `app/models.py`: `title` and `tags` have validators/limits; `description`/`assignee` do not. | Add max lengths for free-text fields; consider a request body size limit. | High |
| SEC-03 | Medium | `requirements.txt`; `.github/workflows/ci.yml`; `Dockerfile` | Python dependencies are unpinned (no version numbers). | Verified: `requirements.txt` lists package names only; CI and Docker install directly from it. | Pin versions or add a lock/constraints file. | High |
| SEC-04 | Low | `app/main.py` (CORS middleware); `frontend/index.html`; `README.md` | CORS is scoped to two localhost origins but sets `allow_credentials=True` with no auth in place. | Verified directly against `app/main.py`: `allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"]`, `allow_credentials=True`. | Keep local-only, or move origins to env config and set `allow_credentials=False` until credentials are actually used. | High |
| SEC-05 | Low | `.github/workflows/ci.yml`; `Dockerfile`; `docs/module4/docker-security-log.md` | CI only installs deps and runs tests; no dependency audit or image scan. | Workflow ends at `pytest -v`; no scanner configured. | Add `pip-audit`/Dependabot and container scanning if repo use extends beyond coursework. | Medium |
| SEC-06 | Informational | `app/main.py`; `README.md` | API docs (`/docs`) are enabled by default. | Default `FastAPI(...)` instantiation; README advertises Swagger docs. | Gate or disable docs outside development if ever deployed. | Medium |

## Grading

| Finding | Grade | Reasoning |
|---|---|---|
| SEC-01 | Valid | Real and evidence-backed. Intentional course-scope decision (documented in the mid-course ADR), but still a genuine production blocker worth naming explicitly rather than silently accepting. |
| SEC-02 | Valid | Real gap — `title`/`tags` are bounded, `description`/`assignee` are not. Minor severity given in-memory, single-process, local-only scope. |
| SEC-03 | Valid | Real and actionable for reproducibility, independent of deployment target. |
| SEC-04 | Valid | Real configuration mismatch (credentials enabled with no auth to protect), even though not exploitable in the current local-only setup. |
| SEC-05 | Noise | True but generic hardening advice with no specific vulnerability or deployment requirement driving it. |
| SEC-06 | Noise | True but expected/default behavior for a local dev-scoped project; not an actionable item without deployment context. |

## Manual Scan

No independent manual scan of `app/` was performed for this deliverable. This means there is no "You-only" column — all findings above are AI-sourced. This is a known gap in this submission's evidence base compared to the ideal Module 5 workflow, which calls for a student-led manual scan alongside the AI audit.

## Observation

AI coverage was strongest on obvious production-readiness gaps: authentication, validation limits, dependency hygiene, and local-only configuration. It was weaker where findings became generic hardening advice without repo-specific urgency, particularly CI/container scanning and default API docs.

## Top-3 Security Backlog

| Rank | Finding | Why it matters | Suggested owner | Next action |
|---|---|---|---|---|
| 1 | SEC-01: No authentication or authorization | Fine for course scope, but unsafe for any shared or deployed environment — anyone who can reach the API can read, create, update, or delete tasks. | Course/project owner + backend | Document as local-only, or define minimal auth requirements before deployment. |
| 2 | SEC-02: Unbounded free-text fields | Large `description` or `assignee` values could cause memory/resource issues, especially since storage is in-process. | Backend | Add max lengths for `description` and `assignee`, with tests for rejection. |
| 3 | SEC-03: Unpinned dependencies | Builds may drift over time, reducing CI/Docker reproducibility and increasing supply-chain risk. | DevOps | Pin dependency versions or add a constraints/lock file. |

## Files Inspected

`app/main.py`, `app/models.py`, `app/storage.py`, `app/business_rules.py`, `tests/test_tasks.py`, `requirements.txt`, `Dockerfile`, `.github/workflows/ci.yml`, `frontend/index.html`, `README.md`, `AGENTS.md`, `docs/decisions/in-memory-task-storage.md`, `docs/module4/docker-security-log.md`.