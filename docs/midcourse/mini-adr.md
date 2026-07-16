# Mini-ADR - Mid-Course Project

## Feature: Due dates + overdue filter

Decision: Add an optional `due_date` field (ISO 8601 date-only, YYYY-MM-DD) to TaskCreate, TaskUpdate, and TaskResponse. Compute `is_overdue` as a derived value in `business_rules.py`, alongside the existing `validate_status_transition` logic, rather than in storage.py. Expose `is_overdue` in TaskResponse and add an optional `overdue` query parameter to GET /tasks to mirror the existing `status` and `priority` filters.

Alternatives considered and rejected:
- Computing overdue entirely in the frontend from the raw `due_date` (rejected because it would split the rule across clients and weaken the existing central business-rule pattern).

## Feature: Tags / labels

Decision: Add a `tags` field (list of strings) to TaskCreate, TaskUpdate, and TaskResponse. Validate it in `models.py` using the same field-validator pattern already used for title: trim each tag, reject empty or whitespace-only values, and enforce a maximum of 5 tags per task with a 30-character limit each. Add an optional `tag` query parameter to GET /tasks, following the same pattern as `status` and `priority`.

Alternatives considered and rejected:
- Using a comma-separated string instead of a list (rejected because per-tag validation and filtering are harder to enforce reliably and more error-prone).

