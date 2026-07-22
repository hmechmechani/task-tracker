# Final AI Review and Ownership Evidence

## AGENTS.md guardrails

- Repo-specific stack and commands included: yes — verified directly against `app/models.py`, `app/business_rules.py`, and `README.md` in Module 5 Part 5.1 (transition table, tag validation limits, and run/test commands all cross-checked and confirmed accurate).
- Docs-first/read-first guardrail included: yes — explicit "Module 5 Guardrails" section states "Docs-first: inspect README, docs, tests, and existing implementation before proposing changes" and "Read-only by default."
- Unexpected app/frontend edits rule included: yes — explicit line: "Do not change files under `app/` unless the user explicitly approves that scope."

## AI code review mini-log

Reusing real findings from `docs/module4/review-log.md` (AI review of commit `e495708`, Dockerfile/`.dockerignore` changes):

| AI comment | Grade: Useful / Noise / Wrong | Reason | Verification or decision |
|---|---|---|---|
| "CI does not build or test the Docker image, only runs pytest on the host" | Useful (deferred) | Accurate — confirmed by reading `.github/workflows/ci.yml`, which only runs `pytest -v`, no `docker build` step. | Logged as a known gap; not fixed in this pass since it would expand CI scope beyond what the course required. |
| "pytest and httpx get baked into the runtime image since requirements.txt isn't split into runtime vs. dev dependencies" | Useful (deferred) | Accurate — confirmed by reading `requirements.txt`, which lists `pytest`/`httpx` alongside `fastapi`/`uvicorn` with no separation. | Logged as a known gap; a `requirements-dev.txt` split was judged out of scope for course requirements. |
| "No version pinning on any dependency is a supply-chain risk" | Noise | Technically true but generic — this course project has no deployment target where dependency drift has caused an actual problem. | Not actioned in Module 4; re-surfaced independently in the Module 5 security review (`SEC-03`), where it was graded Valid with the same reasoning applied more rigorously. |

## AI security mini-review

Reusing real findings from `docs/security-review.md` (Module 5 Part 5.2), each independently verified against actual repo files before grading:

| Finding | File evidence | Grade: Valid / False Positive / Noise | Reason | Next action |
|---|---|---|---|---|
| No authentication or authorization on task CRUD routes | `app/main.py` route handlers (verified: no auth dependencies present); `docs/decisions/in-memory-task-storage.md` | Valid | Real and evidence-backed; intentional course-scope decision, but still a genuine production blocker worth naming explicitly. | Documented as local-only; would need real auth before any deployment. |
| CORS scoped to two localhost origins but `allow_credentials=True` with no auth in place | `app/main.py` — verified directly: `allow_origins=["http://127.0.0.1:5500","http://localhost:5500"]`, `allow_credentials=True` | Valid | Real configuration mismatch — credentials enabled with nothing to protect. | Not exploitable in current local-only setup; would need tightening before deployment. |
| API docs (`/docs`) enabled by default | `app/main.py` — default `FastAPI(...)` instantiation | Noise | Expected/default behavior for a local dev-scoped project; not actionable without deployment context. | No action needed for course scope. |

## Manual security check

I ran an independent empirical test rather than accepting an AI explanation on faith. When reviewing why `app/models.py`'s tag validators use Pydantic's `mode="before"` instead of the default `mode="after"`, I temporarily changed `TaskCreate.validate_tags` to `mode="after"`, restarted the server, and sent a `POST /tasks` request with `tags: "urgent"` (a string instead of a list). Result: the same input that returns a clean `422` under `mode="before"` instead crashed the server with an unhandled `500 Internal Server Error` under `mode="after"` — visible directly in the real server traceback, not just in narration. I reverted the change and confirmed all 29 tests still passed before moving on. This was not something any AI tool told me to check; I found it by testing the code's actual behavior myself.

## One AI output I rejected or corrected

The original AI-assisted `TaskUpdate.title` validator in `app/models.py` silently returned `None` unchanged when a client sent `{"title": null}` in a PATCH request, even though `TaskResponse.title` requires a non-null string — a real contract violation. A Module 4 documentation audit caught this by testing the actual endpoint behavior against the documented contract, not by trusting the AI-generated docstring. I corrected the validator to explicitly `raise ValueError("title cannot be null")`, added a regression test (`test_patch_title_null_returns_422`), and verified the fix with `pytest -v` (29/29 passing).

## Three AI usage rules

1. Never paste: uncropped, full-desktop screenshots — repeatedly exposed my Windows username and employer's OneDrive folder path across Modules 3-5 without me being deliberate about it (documented in `docs/governance-worksheet.md`).
2. Always verify: any AI claim that a file was written, applied, or behaves a certain way — confirmed via direct file read, `git status`, or running the actual code. This course caught multiple real "applied but not actually on disk" claims, including `AGENTS.md` itself never being committed until caught via a `git status` check during Module 5's closeout.
3. Record AI contributions by: evidence-based `docs/` files with file citations and confidence levels, not narrative summaries — e.g. `docs/security-review.md`'s findings table cites exact files and marks confidence per claim.

## Ownership statement

I'm comfortable submitting this repo because every claim in it traces back to something I actually ran, read, or tested — not something an AI tool told me was true. Across this course I caught and corrected a real validation bug that let `null` titles bypass a required-field contract, caught a stale test count in the README before it could compound, caught my own AGENTS.md file never actually being committed, and found a genuine crash-vs-graceful-error distinction in Pydantic validator behavior by testing it myself rather than accepting an explanation. Where AI proposed findings — security audits, code reviews, architecture docs — I graded each one against real file evidence rather than accepting them at face value, and I can explain why each graded decision was made. The parts of this repo I'm least confident about, like Docker internals, are explicitly named as such in my playbook rather than glossed over.