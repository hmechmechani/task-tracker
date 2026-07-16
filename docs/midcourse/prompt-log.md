# Prompt Log - Mid-Course Project

## Feature 1: Due dates + overdue filter

**Prompt 1 - Backend implementation.** Scoped prompt specifying: add optional `due_date` to TaskCreate/TaskUpdate/TaskResponse, add `is_task_overdue(due_date, status)` in business_rules.py, expose `is_overdue` on TaskResponse, add an `overdue` query param to GET /tasks mirroring `status`/`priority`. Constraints blocked touching tags, the frontend, or existing validation logic.
Result: accepted with a required follow-up. The initial diff computed `is_overdue` correctly at write time (create/update) but never recomputed it at read time, so a task's overdue status would go stale if time passed without an edit. Found by reading `storage.py` directly, not from a failing test.

**Prompt 2 - Weak vs. improved diagnostic prompt.**
Weak version (not used): "fix the overdue bug."
Improved version (used): a structured prompt describing the exact staleness bug, asking for root cause, why it fails, a source-only fix, confirmation the fix doesn't change write behavior, and a verification command.
Result: accepted. Correctly diagnosed the cause (`get_all_tasks`/`get_task_by_id` returning cached values) and proposed a `_hydrate_task()` helper that recomputes `is_overdue` fresh on every read. Verified via pytest before and after.

**Prompt 3 - Test generation.** One-test-at-a-time prompt for `test_is_task_overdue_recomputes_based_on_current_date`, which required adding a testability `today` parameter to `is_task_overdue` (defaulting to `date.today()`) so the test could control the date without monkeypatching. Result: accepted. Test asserts the same due date is not-overdue before it and overdue after it, directly proving the staleness fix.

**Prompt 4 - Frontend, three separate scoped prompts** (modal due-date field, card due-date/overdue-badge display, overdue filter checkbox wired through `fetchTasks`). All three accepted as-is on first correct diff. Verified live in the browser at each step.

## Feature 2: Tags / labels

**Prompt 1 - Backend implementation.** Scoped prompt: add `tags: list[str]` to the three models, validate via a shared `_validate_tags()` helper (trim, reject blank, max 5 tags, max 30 chars each), add a `tag` query param to GET /tasks. Result: accepted cleanly — correctly reused the existing title-validator pattern and didn't touch due-date or status logic.

**Prompt 2 - Rejected diff.** A later multi-file Copilot turn (interrupted partway by a "Quota Exceeded" notice) bundled backend changes together with an unrequested change to `frontend/index.html`, despite an explicit "do not modify the frontend" constraint. Rejected — reverted the frontend file via Undo before accepting the backend files.

**Prompt 3 - Test generation, two prompts.** `test_patch_update_tags_returns_200` and `test_patch_unrelated_field_preserves_tags`, one at a time. Both accepted as-is, correctly grounded in the actual PATCH semantics.

**Prompt 4 - Frontend, three separate scoped prompts** (modal tags field, tag-chip card display, tag filter combined with the overdue filter via `URLSearchParams`). All accepted as-is.

## Cross-cutting note

An Undo action on the rejected frontend diff (Prompt 2 above) reverted `frontend/index.html` further than intended — not just the unwanted tags change, but the entire Feature 1 frontend work (due-date field, overdue badge, filter checkbox) that had already been completed and verified. Caught by comparing the live app against the last-known-good file content, not from any AI narration. Restored from the last verified full-file copy.
