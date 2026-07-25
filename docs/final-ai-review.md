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

**Update after instructor feedback on this submission:** the instructor flagged that the documented `422` behavior for malformed tag input did not match the actual submitted app, which could return `500`. I re-tested live against the actual running app rather than trusting the earlier write-up, confirmed the instructor was right, root-caused it, and fixed it. Full account below.

Original investigation (Module 5): while reviewing why `app/models.py`'s tag validators use Pydantic's `mode="before"` instead of the default `mode="after"`, I temporarily changed `TaskCreate.validate_tags` to `mode="after"` and sent a malformed request (`tags: "urgent"`, a string instead of a list). At that time, `mode="before"` returned a clean `422` and `mode="after"` crashed with `500`. I reverted to `mode="before"` and moved on, concluding the mode was the deciding factor.

That conclusion turned out to be incomplete. On re-testing for this resubmission, the *current* committed code — `mode="before"` on both `TaskCreate` and `TaskUpdate` — was returning `500` for the exact same malformed-tags request, confirmed with a real traceback from the running server, not narration. I tested further and found `title` had the identical problem: sending a non-string `title` also crashed with `500`, even though the automated test suite (31 tests) was still fully green.

Root cause: both validators raised `TypeError` for wrong-type input. Pydantic v2's documented contract guarantees that a `ValueError` (or `AssertionError`) raised inside a validator gets caught and converted into a clean `422` — `TypeError` was never part of that guarantee. `requirements.txt` had no version pins (a risk already flagged as `SEC-03` in `docs/security-review.md`), so the installed `pydantic-core` version drifted over time to one that no longer happens to catch `TypeError` the way an earlier version apparently did. The automated suite never caught this because none of the 29 original tests sent a wrong-*type* value for `title` or `tags` — only blank, missing, or too-long values, which all correctly use `ValueError` and were never affected.

Fix applied: changed all 4 `raise TypeError(...)` calls in `app/models.py` to `raise ValueError(...)`, corrected the now-stale `Raises:` docstrings to match, pinned `fastapi`, `uvicorn`, `pydantic`, `python-dotenv`, `pytest`, and `httpx` to their exact working versions in `requirements.txt`, and added two regression tests (`test_create_task_non_string_title_returns_422`, `test_create_task_non_list_tags_returns_422`) that specifically cover the gap that let this ship untested. Verified live: `POST /tasks` with `tags: "urgent"` and with `title: 123` both now return `422` with clear error messages, and the full suite passes at 31/31.

This is the single strongest piece of evidence in this document that AI narration (including my own earlier write-up of this exact investigation) can be wrong, and that verifying against the live, running app — not just the code or a prior test result — is the only thing that actually catches it.

### Second manual check: explicit-null corruption (found after further instructor feedback)

A second round of instructor feedback reported that explicit `null` values were still accepted for
`description`, `status`, `priority`, and `tags`, and that this could cause later requests to return
HTTP 500. Rather than assume the report was complete, I reproduced it against the running app.

What I found was worse than a simple validation gap. `PATCH /tasks/{id}` with `{"status": null}`
returned **200**, not an error — the null was written straight into storage. The crash only appeared
on the *next* request touching that task:

```
File "app/main.py", line 130, in update_task
    validate_status_transition(existing.status, payload.status)
File "app/business_rules.py", line 32, in validate_status_transition
    detail=f"Invalid status transition from {current.value} to {new.value}..."
AttributeError: 'NoneType' object has no attribute 'value'
```

Root cause, traced through the code rather than guessed: `TaskUpdate` only rejected an explicit null
for `title`; the other four fields had no such check, and `_validate_tags` explicitly returned `None`
unchanged. `app/storage.py`'s `update_task()` then merges the payload via
`task.model_copy(update=...)` — and **`model_copy` does not re-validate**. So a null bypassed Pydantic
entirely and was persisted into fields that `TaskResponse` declares as required and non-nullable.
The corrupted task then broke whichever later request tried to read or transition it.

Why the test suite missed it: all 31 tests at that point sent either valid values or wrong *types* —
none sent an explicit `null` for these four fields, so the path was never exercised.

Change made to `app/` (explained here per the project ground rules): added explicit null-rejecting
`mode="before"` validators for `description`, `status`, and `priority` on `TaskUpdate`, and changed
`_validate_tags` to raise `ValueError("tags cannot be null")` instead of returning `None`.
`assignee` and `due_date` were deliberately left nullable — they are `Optional` on `TaskResponse` too,
so clearing them is legitimate behavior, not corruption. Four regression tests were added, two of
which assert not just the 422 but that the stored task is *still readable and unchanged* afterward —
because the original bug's real damage was the corrupted state, not the response code.

Verified live after the fix: all four fields return 422 with a clear message, a follow-up status
transition succeeds instead of crashing, legitimate updates still work, and the full suite passes at
35/35.

The lesson I take from this one: the first fix I made in this area (`TypeError` → `ValueError`) was
correct but I stopped at the symptom the grader named instead of asking what *else* shared that shape.
A null is not a wrong type, so my earlier regression tests sailed past it. Checking the whole class of
input, not just the reported instance, is what would have caught both in one pass.


## One AI output I rejected or corrected

The original AI-assisted `TaskUpdate.title` validator in `app/models.py` silently returned `None` unchanged when a client sent `{"title": null}` in a PATCH request, even though `TaskResponse.title` requires a non-null string — a real contract violation. A Module 4 documentation audit caught this by testing the actual endpoint behavior against the documented contract, not by trusting the AI-generated docstring. I corrected the validator to explicitly `raise ValueError("title cannot be null")`, added a regression test (`test_patch_title_null_returns_422`), and verified the fix with `pytest -v` (29/29 passing).

## Three AI usage rules

1. Never paste: uncropped, full-desktop screenshots — repeatedly exposed my Windows username and employer's OneDrive folder path across Modules 3-5 without me being deliberate about it (documented in `docs/governance-worksheet.md`).
2. Always verify: any AI claim that a file was written, applied, or behaves a certain way — confirmed via direct file read, `git status`, or running the actual code. This course caught multiple real "applied but not actually on disk" claims, including `AGENTS.md` itself never being committed until caught via a `git status` check during Module 5's closeout.
3. Record AI contributions by: evidence-based `docs/` files with file citations and confidence levels, not narrative summaries — e.g. `docs/security-review.md`'s findings table cites exact files and marks confidence per claim.

## Ownership statement

I'm comfortable submitting this repo because every claim in it traces back to something I actually ran, read, or tested — not something an AI tool told me was true. Across this course I caught and corrected a real validation bug that let `null` titles bypass a required-field contract, caught a stale test count in the README before it could compound, caught my own AGENTS.md file never actually being committed, found a genuine crash-vs-graceful-error distinction in Pydantic validator behavior by testing it myself rather than accepting an explanation, and traced a state-corruption bug where an update that looked successful silently persisted invalid data and crashed the next request instead. Where AI proposed findings — security audits, code reviews, architecture docs — I graded each one against real file evidence rather than accepting them at face value, and I can explain why each graded decision was made. The parts of this repo I'm least confident about, like Docker internals, are explicitly named as such in my playbook rather than glossed over.