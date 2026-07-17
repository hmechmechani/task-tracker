# Personal AI Usage Rules — Task Tracker (Module 5, Part 5.3)

These rules come from my actual governance worksheet and code-tracing exercise in `docs/governance-worksheet.md`, not generic policy language.

## 1. What I will never paste

Credentials, tokens, production config, or real user/customer data — none of these arose during this course, since the project intentionally has no auth and no real users (see `docs/decisions/in-memory-task-storage.md`), but this is the standing rule going forward.

Also: uncropped, full-desktop screenshots. Across Modules 3-5 I repeatedly shared screenshots that exposed my Windows username and my employer's OneDrive folder name (`OneDrive - MenaRest FZCO`) in file paths and terminal prompts. Not a secret, but not something I was being deliberate about. Going forward I crop screenshots to just the relevant panel before sharing.

## 2. What I will always verify before accepting

Any AI claim that a file was written, applied, or behaves a certain way — confirmed by directly reading the file, checking `git status`, or running the actual code, never by trusting the tool's narration alone. This course caught multiple real instances of "applied" claims that weren't actually true on disk.

Concrete evidence this rule is real, not aspirational: when Codex explained why `app/models.py` uses `mode="before"` on its Pydantic tag validators instead of the default `mode="after"`, I didn't accept the explanation. I temporarily changed the code to `mode="after"`, restarted the server, and sent a deliberately bad request. The result: the same input that returns a clean `422` under `mode="before"` instead crashes the server with an unhandled `500 Internal Server Error` under `mode="after"`. I saw the real traceback, reverted the change, and confirmed all 29 tests still pass before moving on.

## 3. How I will record AI contributions

Evidence-based `docs/` files with file citations and confidence levels — for example, `docs/security-review.md`'s findings table cites exact files and marks confidence per claim, rather than a narrative summary that just asserts conclusions.

Commit messages name which module or task the change supports (for example, "Module 5: security review"), so the history itself is a record of what AI-assisted work happened when.

## 30-Day Re-read Commitment

I will re-read this file in 30 days (by 2026-08-16) and check whether these three rules still match how I actually work, or whether they've quietly become aspirational rather than descriptive.
