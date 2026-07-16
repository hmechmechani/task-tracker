# Claim-vs-Reality Log — Module 4 Documentation Audit

## Finding 1 (bug, fixed): title: null silently accepted
**Claim:** `TaskResponse.title` is documented and typed as a required `str`; no docstring or README claim suggested a task could ever have a null title.
**Reality:** `PATCH /tasks/{id}` with `{"title": null}` returned `200` with `"title": null` in the response body. `TaskUpdate.title` was `Optional[str]`, and the validator passed `None` straight through, silently violating `TaskResponse`'s required-string contract. No test covered this.
**Resolution:** Fixed `TaskUpdate.validate_title` to reject an explicit `null` with a validation error (422), matching the existing rule that title can never be blank. Added a regression test, `test_patch_title_null_returns_422`.
**Evidence:** `pytest -v` — 29 passed (28 → 29 with the new test).

## Finding 2 (doc inconsistency, fixed): update_task docstring incomplete
**Claim:** `update_task`'s docstring `Raises:` section listed only the two explicit 404s and the transition 422, unlike `create_task` and `list_tasks`, which both note that FastAPI/Pydantic reject malformed request bodies with 422 before the function body runs.
**Reality:** The same framework-level 422 behavior applies to `update_task`'s `TaskUpdate` payload, just undocumented.
**Resolution:** Added the same `[VERIFY]` note to `update_task`, matching the other two route docstrings.
**Evidence:** Diff applied to `app/main.py`, scoped to that one docstring.

## Finding 3 (confirmed accurate): Docker instructions
**Claim:** README's "Run with Docker" section — build/run/curl commands, non-root `app` user.
**Reality:** Verified empirically, not just read from the Dockerfile — built the image, ran the container, curled `/health` (200 OK), and confirmed `docker exec tt-dev whoami` returns `app`.
**Resolution:** No change needed.

## Finding 4 (confirmed accurate): status codes
**Claim:** `POST /tasks` returns 201, `DELETE /tasks/{id}` returns 204.
**Reality:** Confirmed explicit in `app/main.py` (`status.HTTP_201_CREATED`, `status.HTTP_204_NO_CONTENT`) and covered by passing tests.
**Resolution:** No change needed.

## Finding 5 (confirmed accurate): CI claims
**Claim:** README's CI section — triggers on push (any branch) and PR to main, pinned Python 3.11, installs from requirements.txt, runs pytest -v.
**Reality:** Confirmed against the literal `.github/workflows/ci.yml` content.
**Resolution:** No change needed.
