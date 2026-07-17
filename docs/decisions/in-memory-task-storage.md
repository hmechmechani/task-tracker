# Technical Decision Note: In-Memory Dict as the Task Storage Layer

Status: Reviewed and finalized.

## 1. Context

The Task Tracker backend (`app/storage.py`) stores all tasks in a single module-level Python dict, `_tasks: dict[str, TaskResponse]` (`app/storage.py:8`). There is no database, ORM, or file persistence anywhere in the codebase — `requirements.txt` lists only `fastapi`, `uvicorn[standard]`, `pydantic`, and `python-dotenv` as runtime dependencies, with no DB driver of any kind.

Every route in `app/main.py` (`list_tasks`, `get_task`, `update_task`, `delete_task`, `create_task`) calls straight into `storage.py`'s module-level functions — there is no repository interface, no dependency-injected storage abstraction, and no separate persistence-layer schema. The same Pydantic model, `TaskResponse` (`app/models.py`), is used both as the API response shape and as the in-memory "row" representation stored in `_tasks`.

This decision predates the mid-course feature work — the existing `docs/midcourse/mini-adr.md` documents the due-dates/overdue and tags/labels decisions, but does not document the original choice of in-memory storage itself. This note fills that gap.

A private helper, `_reset()` (`app/storage.py:159`), exists solely to clear `_tasks` between test runs (used by the autouse `_reset_storage` fixture in `tests/conftest.py`) — itself a symptom of storage being global mutable process state rather than an isolated, swappable dependency.

**This app has no authentication, no database, no deployment pipeline beyond CI running tests and a Dockerfile, and no production hardening of any kind.** Nothing below should be read as implying otherwise.

## 2. Decision

Task storage is a single in-process Python dict, scoped to the lifetime of the running server process. Data is not persisted to disk, a database, or any external store. Restarting the process (including `uvicorn --reload` picking up a code change) discards all tasks. This is the storage layer for the entire project as it currently stands — there is no partial or optional database mode.

## 3. Alternatives Considered

- **SQLite via SQLAlchemy or a raw driver** — would give real persistence across restarts and transactional writes, at the cost of a schema/migration story and an ORM/session-management layer the module scope doesn't currently ask for. Not adopted.
- **A JSON/pickle file on disk** — would survive process restarts without a real database, but introduces file I/O error handling, concurrent-write corruption risk, and serialization concerns for the `TaskResponse` model that the current dict avoids entirely. Not adopted.
- **An abstract storage interface (e.g., a `TaskRepository` protocol) with the dict as one implementation** — would make a future swap to a real database cheaper, but adds an abstraction layer with only one concrete implementation today, which is premature for the project's current scope. Not adopted.

[VERIFY] I did not find evidence in the repo (commit history, `docs/midcourse/mini-adr.md`, or code comments) that these alternatives were explicitly weighed at the time storage.py was first written — the "alternatives considered" above are reconstructed from what the current design implies was in scope, not from a recorded discussion.

## 4. Consequences

- The app cannot be horizontally scaled (multiple processes/replicas) without tasks silently diverging between instances, since each process has its own `_tasks` dict. [VERIFY] this has not been tested — it's a direct consequence of the design, not an observed failure.
- Test isolation depends on `storage._reset()` being called between tests (`tests/conftest.py`); forgetting this in a future test file would leak state across tests silently.
- The Docker image (`Dockerfile`) ships no volume or persistence configuration, which is consistent with this decision — there is nothing to persist.
- Any future move to a real database will require touching every function in `storage.py` and likely introducing async I/O, since the current synchronous, in-memory functions assume storage access never blocks.

## Trade-offs

Choosing an in-memory dict kept the project simple and let every module build on it without setup overhead — no schema to design, no migrations, nothing extra to install to run the app or the tests. The real cost is durability: every restart wipes all data with no warning, which would be unacceptable for a real product but is a reasonable trade for a course project whose scope was explicitly features, testing, and engineering practice, not data persistence. The read-then-write race in update_task is a real gap, but fixing it now would mean solving a concurrency problem the project doesn't actually have at this scale or in this context — a course exercise, not a deployed multi-user service.

## Open Questions

- If this project continued past the course, would the next step be swapping in a real database directly, or introducing a storage interface first so the rest of the app doesn't need to change when that swap happens?
- Is the read-then-write race in update_task worth a cheap fix (a simple lock) even without a database, just so it's not a known gap sitting in the code, or is that solving a problem this project will never actually hit?

I would do this differently by adding a lightweight storage interface (even with the dict as the only implementation) from the start, so a future move to a real database wouldn't require touching every function in storage.py individually.
