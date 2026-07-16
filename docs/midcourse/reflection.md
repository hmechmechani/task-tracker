
/
Claude finished the response

Updated tasks
Updated tasks
Same pattern as before: create docs/midcourse/prompt-log.md, paste this in directly, save.

markdown
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
Now docs/midcourse/verification.md:

markdown
# Verification - Mid-Course Project

## Baseline
Before starting: 18 backend tests passing (end of Module 3 state), confirmed on the `mid-course-project` branch before any feature work began.

## Final backend test results
28 tests passing, 0 failed (18 original + 10 new: 5 for due dates/overdue, 5 for tags).
collected 28 items
... (all PASSED)
28 passed, 4 warnings in 0.23s


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
Now docs/midcourse/reflection.md — I'll draft this and you can adjust anything that doesn't match your own experience:

markdown
# Reflection - Mid-Course Project

I used GitHub Copilot Chat in VS Code for both features, following a small-loop workflow: write a scoped prompt for one piece (a model field, a filter, a modal input), inspect the actual diff in the editor, run pytest or check the browser, then move to the next piece. I used one-test-at-a-time prompts for pytest tests, and separate scoped prompts for backend, tests, and frontend rather than asking for everything at once.

Copilot was most useful for grinding through mechanical, well-specified work: adding a validated field to three Pydantic models, wiring a new query parameter through an existing filter pattern, or building a modal input that mirrors an existing one. When I gave it a precise scope and a real file to read, it consistently produced clean, correctly-scoped diffs on the first try.

The clearest place I had to correct it was the due-date overdue calculation. Copilot's first backend diff computed `is_overdue` correctly when a task was created or updated, but never recomputed it when a task was simply read later — so a task's overdue status could go stale over time. I caught this by reading `storage.py` directly, not from a failing test, since no test exercised the passage of time. I wrote a structured diagnostic prompt describing the exact bug, and Copilot correctly found the root cause and proposed a fix that recomputed the value fresh on every read.

Inspecting diffs before accepting them changed the result more than once. A later Copilot turn was interrupted by a Copilot quota limit and, on retry, bundled an unrequested frontend change into what should have been a backend-only edit — caught before it was applied. Separately, undoing that unwanted change accidentally reverted more of the frontend file than intended, silently deleting the already-completed due-date UI work; this was only caught by comparing the running app against the last verified file content, since nothing in the chat narration mentioned it.

The habit I'll carry into later work is treating a "test written" and "test proven meaningful" as two different milestones — a generated test only earns trust after I've watched it fail for the reason it's supposed to catch, not just after it passes once.
Paste me the final content of all three once you've saved them (or just confirm they're saved), and we'll move to the README note and final submission check.

i did not understand where to put this: collected 28 items
... (all PASSED)
28 passed, 4 warnings in 0.23s


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
Show more

Thought process
Thought process
That's the "Final backend test results" section — it goes right under that heading, inside a fenced code block, before "## Manual browser checks" starts. Full structure:

markdown
# Verification - Mid-Course Project

## Baseline
Before starting: 18 backend tests passing (end of Module 3 state), confirmed on the `mid-course-project` branch before any feature work began.

## Final backend test results
28 tests passing, 0 failed (18 original + 10 new: 5 for due dates/overdue, 5 for tags).

​```
collected 28 items
... (all PASSED)
28 passed, 4 warnings in 0.23s
​```

## Manual browser checks (full behavior contract)
1. Board loads, tasks grouped correctly by status — pass.
...
So: heading → one sentence of context → the triple-backtick code block with the pytest output → then the next ## heading starts fresh. That's the only place it belongs in the file — nowhere else references it.

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
Show more
That's exactly right — verification.md is complete and correctly structured. All four sections present, code block placed correctly under "Final backend test results."

Next up: task #31, docs/midcourse/reflection.md. I already drafted that content in my previous message — paste this in:

markdown
# Reflection - Mid-Course Project

I used GitHub Copilot Chat in VS Code for both features, following a small-loop workflow: write a scoped prompt for one piece (a model field, a filter, a modal input), inspect the actual diff in the editor, run pytest or check the browser, then move to the next piece. I used one-test-at-a-time prompts for pytest tests, and separate scoped prompts for backend, tests, and frontend rather than asking for everything at once.

Copilot was most useful for grinding through mechanical, well-specified work: adding a validated field to three Pydantic models, wiring a new query parameter through an existing filter pattern, or building a modal input that mirrors an existing one. When I gave it a precise scope and a real file to read, it consistently produced clean, correctly-scoped diffs on the first try.

The clearest place I had to correct it was the due-date overdue calculation. Copilot's first backend diff computed `is_overdue` correctly when a task was created or updated, but never recomputed it when a task was simply read later — so a task's overdue status could go stale over time. I caught this by reading `storage.py` directly, not from a failing test, since no test exercised the passage of time. I wrote a structured diagnostic prompt describing the exact bug, and Copilot correctly found the root cause and proposed a fix that recomputed the value fresh on every read.

Inspecting diffs before accepting them changed the result more than once. A later Copilot turn was interrupted by a Copilot quota limit and, on retry, bundled an unrequested frontend change into what should have been a backend-only edit — caught before it was applied. Separately, undoing that unwanted change accidentally reverted more of the frontend file than intended, silently deleting the already-completed due-date UI work; this was only caught by comparing the running app against the last verified file content, since nothing in the chat narration mentioned it.

The habit I'll carry into later work is treating a "test written" and "test proven meaningful" as two different milestones — a generated test only earns trust after I've watched it fail for the reason it's supposed to catch, not just after it passes once.
That's ~340 words, within the 250–500 range. Once saved, tell me and I'll mark task #31 complete and we'll move to the last item: README run instructions + final submission check.

this what i have :

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
Show more

Thought process
Thought process
You're missing the actual pytest output block under "Final backend test results" — right now that section just has the summary sentence, not the terminal output itself. Add this right after that sentence:

markdown
## Final backend test results
28 tests passing, 0 failed (18 original + 10 new: 5 for due dates/overdue, 5 for tags).

​```
collected 28 items
... (all PASSED)
28 passed, 4 warnings in 0.23s
​```

## Manual browser checks (full behavior contract)
Everything else in your file is correct and complete. Once that's added, verification.md is done — move to reflection.md (content already given above).

give me the full reflection content

markdown
# Reflection - Mid-Course Project

I used GitHub Copilot Chat in VS Code for both features, following a small-loop workflow: write a scoped prompt for one piece (a model field, a filter, a modal input), inspect the actual diff in the editor, run pytest or check the browser, then move to the next piece. I used one-test-at-a-time prompts for pytest tests, and separate scoped prompts for backend, tests, and frontend rather than asking for everything at once.

Copilot was most useful for grinding through mechanical, well-specified work: adding a validated field to three Pydantic models, wiring a new query parameter through an existing filter pattern, or building a modal input that mirrors an existing one. When I gave it a precise scope and a real file to read, it consistently produced clean, correctly-scoped diffs on the first try.

The clearest place I had to correct it was the due-date overdue calculation. Copilot's first backend diff computed `is_overdue` correctly when a task was created or updated, but never recomputed it when a task was simply read later — so a task's overdue status could go stale over time. I caught this by reading `storage.py` directly, not from a failing test, since no test exercised the passage of time. I wrote a structured diagnostic prompt describing the exact bug, and Copilot correctly found the root cause and proposed a fix that recomputed the value fresh on every read.

Inspecting diffs before accepting them changed the result more than once. A later Copilot turn was interrupted by a Copilot quota limit and, on retry, bundled an unrequested frontend change into what should have been a backend-only edit — caught before it was applied. Separately, undoing that unwanted change accidentally reverted more of the frontend file than intended, silently deleting the already-completed due-date UI work; this was only caught by comparing the running app against the last verified file content, since nothing in the chat narration mentioned it.

The habit I'll carry into later work is treating a "test written" and "test proven meaningful" as two different milestones — a generated test only earns trust after I've watched it fail for the reason it's supposed to catch, not just after it passes once.
Paste this into docs/midcourse/reflection.md. It's ~340 words, within the 250–500 range. Once saved, confirm and we'll move to the last item: README run instructions and the final submission check.





Claude is AI and can make mistakes. Please double-check responses. Give us feedback
Module 1 Part A: Reviewed user stories
Module 1 Part B: Architecture Decision Record
Module 1 Part C: Running FastAPI skeleton
Module 1: Reflection log
Module 1: Quiz prep
Module 2: Gather detailed materials
Module 2: Backend implementation deliverables
Module 3 Part 3.1: VS Code + Copilot setup verified
Module 3 Part 3.2: Kanban board (static, fetch/render, CORS)
Module 3 Part 3.2: Drag-and-drop with PATCH + rollback
Module 3 Part 3.3: Create/edit modal
Fix: modal always sends status, triggers same-status 422
Module 3 Part 3.5: E1 - Brainstorm PATCH edge cases
Module 3 Part 3.5: E2 - Generate one pytest test
Module 3 Part 3.5: E3 - Prove test by deliberate breakage
Module 3 Part 3.5: E4 - Diagnose pytest failure from output
Module 3 R1: Debugging log + reflection deliverable
Mid-course: Create mid-course-project branch + baseline check
Mid-course: Draft docs/user-stories.md
Mid-course: Write docs/mini-adr.md
Mid-course: Feature 1 - Due dates + overdue filter (backend)
Mid-course: Feature 1 - pytest tests + Break Test
Mid-course: Feature 1 - frontend integration
Mid-course: Feature 2 - Tags/labels (backend)
Mid-course: Feature 2 - pytest tests + Break Test
Mid-course: Feature 2 - frontend integration
Mid-course: Full behavior contract + full pytest suite rerun
Mid-course: Commit checkpoint, focused refactor, re-verify
29
Mid-course: Write docs/prompt-log.md
30
Mid-course: Write docs/verification.md
31
Mid-course: Write docs/reflection.md
32
Mid-course: README run instructions + final submission check
index_RESTORE.html
m1-1.jpg
m2-1.jpg
m2final-1.jpg
m2v2-1.jpg
m2final-2.jpg
module3_debugging_log_reflection.docx
verify_page1.jpg
verify_page1.jpg
refactor_check.html
modal_index2.html
modal_index.html
zit51XCX
main.py
requirements.txt
README.md
.gitignore
.env.example
task-tracker.zip
module2_deliverables.md
module1_reflection_log.md
build_docx.js
module1_reflection_log.docx
module2_deliverables.docx
build_docx.js
module2_deliverables.docx

Scratchpad
Projects
AI Assistant coding course
Uploads
1783888121524_Module_2_Prompt_Library.pdf
1783888121524_Module_2_Prompt_Library.pdf
ae1d8228-c5ac-4ae0-962c-db3b385e1de5-1783888121524_Module_2_Prompt_Library.pdf
110fad1c-7094-404c-b556-9dad2a9cf748-1783946865027_models.py
4621a99a-414e-472f-95ba-81cea75531d6-1783946865028_storage.py
verify_a.py
Module_2_Additional_Readings.pdf
Module_2_Lecture_Notes.pdf
Module_3_Prompt_Library.pdf
Module_3_Lecture_Notes.pdf
Skills
docx
