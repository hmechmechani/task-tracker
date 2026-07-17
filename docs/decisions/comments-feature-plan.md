# Comments on Tasks — Feature Plan (Module 5, Part 5.4)

**Status: Plan only. Not implemented.** This document compares a generic, ungrounded AI plan against a repo-grounded Codex App plan for the same feature, then critiques the repo-grounded plan section by section.

A comment has: `id` (string UUID), `task_id` (string reference), `author` (required string, 1-100 chars), `body` (required string, 1-2000 chars), `created_at` (server-generated UTC datetime).

## Method

Two plans were produced independently: a generic plan (5.4A) written with no repo access, and a repo-grounded plan (5.4B) written by Codex App after reading the actual repository files. The repo-grounded plan was then critiqued section by section (5.4C) and compared against the generic baseline.

## Repo-Grounded Plan

### 1. Data Model

Comments follow the existing Pydantic v2 model pattern in `app/models.py`. Add separate models alongside `TaskCreate`, `TaskUpdate`, and `TaskResponse`:

- `CommentCreate`: `author` (required, trimmed, 1-100 chars), `body` (required, trimmed, 1-2000 chars), `extra="forbid"` to match existing task request models.
- `CommentResponse`: `id`, `task_id`, `author`, `body`, `created_at`, `extra="forbid"` to match `TaskResponse`.

Do not add comments directly to `TaskResponse` for the first version unless the team explicitly wants task reads to include comment data — existing task routes return flat objects, and nesting comments would change the response shape and frontend rendering assumptions.

Storage lives in `app/storage.py` near the existing in-memory `_tasks` dictionary: a second in-memory dictionary for comments, keyed by comment id, with helper functions for creating, listing by task id, retrieving, and deleting comments. Because storage is non-durable and reset through `storage._reset()`, comments must also be cleared by `_reset()`. `created_at` uses `datetime.now(timezone.utc)`, matching task timestamp generation in `storage.add_task`.

### 2. API Routes

Routes added in `app/main.py`, tagged `tags=["comments"]`:

- `GET /tasks/{task_id}/comments` — list comments for a task. `200` with list of `CommentResponse` (sorted `created_at` ascending), `404` if task doesn't exist, empty list if task exists with no comments.
- `POST /tasks/{task_id}/comments` — create a comment. `201` with `CommentResponse`, `404` if task doesn't exist, `422` for missing/blank/oversized `author` or `body`, non-string values, or unknown fields.
- `GET /tasks/{task_id}/comments/{comment_id}` — get one comment. `200`, `404` if task or comment doesn't exist under that task.
- `DELETE /tasks/{task_id}/comments/{comment_id}` — delete a comment. `204` no body (matching `DELETE /tasks/{task_id}`), `404` if task or comment doesn't exist under that task.

No authentication or current-user identity exists in the repo, so `author` remains user-provided text unless that changes.

### 3. Tests

Following the existing style in `tests/test_tasks.py`, reusing `client` and `created_task` fixtures from `tests/conftest.py`.

Happy path: `test_create_comment_valid_returns_201_with_full_body`, `test_list_comments_for_task_returns_200_and_comments`, `test_list_comments_for_task_with_no_comments_returns_empty_list`, `test_get_comment_by_id_returns_comment`, `test_delete_comment_existing_returns_204_no_body`, `test_comments_are_cleared_by_storage_reset_between_tests`.

Validation: `test_create_comment_missing_author_returns_422`, `test_create_comment_blank_author_returns_422`, `test_create_comment_author_over_100_returns_422`, `test_create_comment_missing_body_returns_422`, `test_create_comment_blank_body_returns_422`, `test_create_comment_body_over_2000_returns_422`, `test_create_comment_unknown_field_returns_422`, `test_create_comment_non_string_author_returns_422`, `test_create_comment_non_string_body_returns_422`, `test_create_comment_trims_author_and_body`.

Edge cases: `test_list_comments_missing_task_returns_404`, `test_create_comment_missing_task_returns_404`, `test_get_comment_missing_task_returns_404`, `test_get_comment_missing_comment_returns_404`, `test_get_comment_from_different_task_returns_404`, `test_delete_comment_missing_task_returns_404`, `test_delete_comment_missing_comment_returns_404`, `test_delete_task_removes_or_orphans_comments_according_to_decision`, `test_comment_created_at_is_utc_timestamp`, `test_list_comments_order_is_stable_by_created_at`.

### 4. Frontend Changes

`frontend/index.html` is the single file with inline CSS/JS that would need all UI, state, fetch, rendering, and error handling changes.

User-visible behavior: task cards could show a comment count; the existing Edit modal could grow a comments section; users see author/body/timestamp per comment and can add new comments; validation errors follow the existing `field-error`/`form-error` pattern; new comments appear without a full page reload.

Comments should probably load lazily when a task is opened for editing, rather than fetched for every card on every board render, unless comment counts on cards are required (which would need an API or additional-request decision).

### 5. Migration Notes

No database migration needed — `app/storage.py` uses in-process dictionaries, and data clears on restart.

- Add an in-memory comment store.
- Update `storage._reset()` so tests clear comments as well as tasks.
- Decide whether deleting a task also deletes its comments — cascade delete is probably least surprising for an in-memory system, but should be explicit.
- If comments are embedded in `TaskResponse`, existing tests comparing full task JSON may need updates.
- **Correction from critique below:** README's test count (`Expect 28 passed`) was already stale *before* this feature — actual count was 29. Already fixed in a separate commit. Documentation accuracy should be checked before starting a feature, not just after finishing one.

### 6. Open Questions

1. Should comments be available only through nested routes, or should `TaskResponse` include comment counts or embedded comment lists?
2. When a task is deleted, should its comments be deleted too, or retained as orphaned records? No archive/history model currently exists.
3. Should comments be editable? The requested feature only defines creation fields and `created_at`, not `updated_at`.
4. Should comment listing be sorted oldest-first or newest-first?
5. Should there be a maximum number of comments per task, given in-memory storage can grow unbounded during a process lifetime?
6. Should `author` remain free text, or is this a placeholder for future authentication?

### Files Read

`AGENTS.md`, `README.md`, `app/models.py`, `app/main.py`, `app/storage.py`, `app/business_rules.py`, `tests/test_tasks.py`, `tests/conftest.py`, `tests/verify_a.py`, `frontend/index.html`.

### Assumptions to Verify

Comments implemented in the same FastAPI app and in-memory storage layer, not a separate service or database. No authentication required for v1; `author` is client-supplied text. Nested routes under `/tasks/{task_id}/comments` are acceptable. No edit/update behavior unless separately requested. Frontend remains a single-file vanilla HTML/CSS/JS app.

## Critique: Repo-Grounded Plan vs. Generic Plan

| Section | Label | Evidence | Minimal correction |
|---|---|---|---|
| Data Model | Right | Matches real Pydantic v2 conventions (`extra="forbid"`, trim/length validation mirroring `title`/`tags`) and real storage location (`_tasks` dict pattern). | None needed. |
| API Routes | Right | Nested route structure, 404-on-missing-task, 201/204 status codes all match verified conventions in `app/main.py`. | None needed. |
| Tests | Right | Test names and structure match real `tests/test_tasks.py` conventions and reuse actual fixtures. | None needed. |
| Frontend Changes | Right | Correctly identifies `frontend/index.html` as the single file to touch; references real `field-error`/`form-error` classes and global `tasks` array. | None needed. |
| Migration Notes | Missing | Claimed the README test count "would become stale after comment tests are added" — but it was already stale before any comment work started (README said 28, actual was 29). | Check documentation accuracy before starting a feature, not just note that it will drift later. Corrected above. |
| Open Questions | Right | Concrete, real decisions (cascade-delete vs. orphan, nested vs. embedded response, sort order, editability) rather than generic filler. | None needed. |

**Generic vs. repo-grounded comparison:**

- Biggest difference: the generic plan invents an unknown testing framework and hedges throughout ("depending on the existing test approach"); the repo-grounded plan gives exact, ready-to-write test names matching the real file.
- Plan I would hand to a teammate: the repo-grounded plan — directly actionable against the actual codebase with zero translation work.
- Task shape where generic chat is enough: greenfield projects with no existing repo or conventions to ground against, or early brainstorming before any code exists.