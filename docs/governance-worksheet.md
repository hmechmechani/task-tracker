# Governance Worksheet — Task Tracker (Module 5, Part 5.3)

## What I Shared

| Item shared | Risk | Reason | Safer future version |
|---|---|---|---|
| `app/models.py`, `app/main.py`, `app/business_rules.py`, `app/storage.py` (full file contents) | Low | Course toy project code, no sensitive data or proprietary logic. | No change needed. |
| `requirements.txt`, `Dockerfile`, `.github/workflows/ci.yml` | Low | Public-pattern config files, no secrets or credentials in them. | No change needed. |
| pytest/CI error logs and terminal output | Low | Contains only test names, file paths, and generic error text — no data, no credentials. | No change needed. |
| Screenshots of VS Code, GitHub Actions, Docker Desktop, terminal | Medium | Screenshots can incidentally capture more than intended — full file paths including my Windows username and employer's OneDrive folder name (`OneDrive - MenaRest FZCO`), open tabs, or background app state. | Crop screenshots to just the relevant panel before sharing; avoid full-desktop captures. |
| `README.md`, `CLAUDE.md`, `AGENTS.md`, and `docs/` files (ADR, reflections, review logs) | Low | Course documentation, no sensitive data. | No change needed. |
| GitHub repo name/branch name (`hmechmechani/task-tracker`, `mid-course-project`) | Low | Course-scoped repo identifier, no secrets. | No change needed. |
| `git status` / `git log` output | Low | Commit metadata only, no sensitive content. | No change needed. |

## Notes

The one recurring, low-but-real exposure across this course has been terminal/file-path screenshots showing my actual Windows username and my employer's OneDrive folder name. Not a secret, but not something I was being deliberate about scoping out — worth being more careful about going forward, especially outside a course context.

No credentials, tokens, production config, or real user/customer data were shared with any AI tool during this course. This is consistent with the project's course-scope decision (documented in `docs/decisions/in-memory-task-storage.md`) to have no authentication, no real users, and no production deployment.

## Code Ownership Trace (Part 5.3B)

Traced the `mode="before"` Pydantic field validator pattern in `app/models.py` (`_validate_tags` helper plus the `@field_validator("tags", mode="before")` decorators on `TaskCreate` and `TaskUpdate`). Initially could not explain why `mode="before"` was chosen over Pydantic's default `mode="after"`.

Ran an empirical test instead of accepting an explanation on faith: temporarily changed `TaskCreate.validate_tags` to `mode="after"`, restarted the server, and sent a `POST /tasks` request with `tags: "urgent"` (a string instead of a list).

Result:
- With `mode="before"` (original code): request returns a clean `422 Unprocessable Entity` with the custom error message `"tags must be a list of strings"`.
- With `mode="after"` (test change): the identical `TypeError` is raised inside the validator, but it is not caught — it propagates unhandled and crashes the request with a generic `500 Internal Server Error`. The real error only appears in the server's own logs, not in the response sent to the client.

Reverted the change back to `mode="before"` and confirmed all 29 tests still pass. This is now something I can explain and reproduce myself, not just something an AI tool told me.
