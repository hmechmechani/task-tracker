# Verification - Mid-Course Project

## Baseline
Before starting: 18 backend tests passing (end of Module 3 state), confirmed on the `mid-course-project` branch before any feature work began.

## Final backend test results
28 tests passing, 0 failed (18 original + 10 new: 5 for due dates/overdue, 5 for tags).

## Manual browser checks (full behavior contract)
1. Board loads, tasks grouped correctly by status — pass.
2. Drag-and-drop between columns persists, including due date and tags — pass.
3. Invalid drag transition (e.g. In Progress to To Do) rolls back with an error — pass.
4. Create task via modal with due date and tags — pass.
5. Edit one field, unrelated fields (due date, tags) survive — pass.
6. All 4 UI states (loading, ready, empty, error+Retry) — pass.
7. Blank title blocked client-side, no network request sent — pass.
8. Modal closes via Cancel, X, Escape, and backdrop click — pass.
9. Overdue filter, tag filter, and both combined — pass.

## Behavior contract before/after refactor
Refactor: removed a redundant `is_overdue` computation in `storage.py`'s `update_task` (dead code — immediately overwritten by the final `_hydrate_task()` call).
Before refactor: 28 passed.
After refactor: 28 passed. Manually re-verified the overdue badge still appears correctly on a task with a past due date after the refactor.

## Break Test evidence

**Test 1: `test_list_tasks_overdue_filter_returns_only_overdue_tasks`**
Break: inverted the filter condition in `get_all_tasks` from `task.is_overdue is overdue` to `task.is_overdue is not overdue`.
Result: `FAILED ... assert 200 == 422` → actually `assert 'Not overdue task' == 'Overdue task'` (title mismatch as predicted).
Restored, reran full suite: 28 passed.

**Test 2: `test_list_tasks_filter_by_tag_returns_only_matches`**
Break: inverted the filter condition from `tag in task.tags` to `tag not in task.tags`.
Result: `FAILED ... AssertionError: assert ['Review task'] == ['Urgent task', 'Also urgent']` — exactly the predicted failure.
Restored, reran full suite: 28 passed.