# My Personal AI Coding Playbook

## 1. When I reach for AI first

Repetitive or mechanical tasks where writing from scratch is slower than reviewing a draft — boilerplate CRUD routes, Docker/CI scaffolding, a first-pass structure I then check against the real repo.

## 2. When I do not reach for AI

Business rules or product flow decisions — e.g., whether deleting a task should also delete its comments. Those are calls I make myself, not something to accept from an AI suggestion.

## 3. My non-negotiables

Always review an AI suggestion before applying it — never accept a change blind. Use Git as a safety net so any AI-suggested change can be inspected or reverted.

## 4. My review rules

Physically test something before accepting it as correct, rather than trusting an explanation alone. This applies to my own claims too — during the final project I told my instructor a doc had been saved when it hadn't; a plain `dir` check caught it. Verify-before-trusting doesn't stop at AI output.

## 5. What I am still figuring out

Docker — how it actually works, what happens when you build and run an image, and how it fits into running an app end to end.

## Decision Card

Each line leads with *why* a tool's shape fits the task — the course evidence proves the reasoning held, not the reverse.

- **New feature → GitHub Copilot.** A tight write/see-it-break loop fits in-editor suggestions better than a tool I'd switch windows for. Proof: Module 3's Kanban board, drag-and-drop, and create/edit modal.

- **Code review → Claude Code.** Grading each claim deliberately (Useful/Noise/Wrong) fits a terminal tool's structured output better than inline suggestions. Proof: Module 4's `docs/module4/review-log.md`.

- **Debugging → GitHub Copilot.** Break-something-and-watch-the-tests-change needs a fast loop in the same window as the code. Proof: the Module 3 R1 debugging log.

- **Infrastructure → Claude Code.** Docker/CI work is multi-step and reads real command output over time — a persistent terminal fits better than autocomplete. Proof: Module 4's Dockerfile, CI pipeline, and a real green-red-green CI proof.

- **I never paste uncropped, full-desktop screenshots** — they've leaked identifying details repeatedly (`docs/governance-worksheet.md`); once sent I can't control retention.

- **My one rule: ask → inspect → run → test → refine.** Skipping "inspect" or "test" is my biggest error source. Proof: the `title: null` bug, a Pydantic `TypeError`/`ValueError` bug found only by testing the live app, and a stale README count.
