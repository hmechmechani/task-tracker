# My Personal AI Coding Playbook

## 1. When I reach for AI first

I reach for AI first when a task is repetitive or mechanical enough that writing it from scratch would be slower than reviewing and correcting a draft — boilerplate CRUD routes, Docker/CI config scaffolding, a first-pass structure I can then check against the real repo.

## 2. When I do not reach for AI

I do not reach for AI when the decision is about business rules or product flow — for example, whether deleting a task should also delete its comments, or whether comments live nested under tasks or embedded in task responses. Those are calls I need to make myself, not something to accept from an AI's suggestion.

## 3. My non-negotiables

Always review an AI suggestion before applying it — never accept a change blind. Use GitHub (version control) as a safety net so any AI-suggested change can be inspected or reverted.

## 4. My review rules

Physically test something myself before accepting it as correct, rather than trusting an AI's explanation or claim on its own. This applies to my own claims too, not just AI's — during the final project, I told my instructor a file (`docs/final-ai-review.md`) had been saved when it hadn't actually been created yet. A plain `dir` check caught it immediately. "Verify before trusting" doesn't stop at AI output; it applies to my own untested assumptions about my own work.

## 5. What I am still figuring out

Docker. I'm not yet familiar with it and want to understand it better — how it actually works, what happens when you build and run an image, and how it fits into getting an app running end to end.

## Decision Card

Each line below leads with *why* that tool's characteristics fit the task shape — the course evidence is proof the reasoning held up in practice, not the reason itself.

- **For a new feature I reach for: GitHub Copilot** — because building a new feature is a tight loop of writing code and immediately seeing what breaks or renders wrong. An in-editor assistant that suggests as I type matches that rhythm better than a tool I'd have to switch windows to consult. Proof this holds: it's actually how Module 3's Kanban board, drag-and-drop, and create/edit modal got built.

- **For a code review I reach for: Claude Code** — because reviewing code well means slowing down, citing specific evidence, and grading each claim deliberately (Useful / Noise / Wrong) rather than reacting to an inline suggestion in the moment. A terminal-based tool that produces a structured, evidence-cited output fits that deliberate pace better than an editor autocomplete. Proof this holds: Module 4's AI-review triage (`docs/module4/review-log.md`) worked exactly this way.

- **For debugging I reach for: GitHub Copilot** — because my debugging process is break-something-on-purpose-and-watch-the-test-output-change, and that only works if the feedback loop is fast and stays in the same window as the code. Proof this holds: the Module 3 R1 deliverable, literally titled "Debugging log + reflection," was built entirely this way.

- **For infrastructure I reach for: Claude Code** — because infrastructure work (Docker, CI) is multi-step and depends on running real commands and reading their real output over time, not a single inline suggestion — a persistent terminal session is the right shape for that, not an editor autocomplete. Proof this holds: Module 4's Dockerfile, CI pipeline, and `docs/module4/docker-security-log.md` were built and verified this way end to end, including a real green-red-green CI proof.

- **I will never paste uncropped, full-desktop screenshots into an AI tool** — because a full-desktop capture can leak identifying details I never meant to share (my Windows username, my employer's folder path), and once it's sent I have no way to know what gets retained. Proof this is a real risk, not a hypothetical: `docs/governance-worksheet.md` documents this happening repeatedly, unintentionally, across Modules 3-5.

- **My one rule is: ask → inspect → run → test → refine** — because this course showed me repeatedly that AI narration and actual file/command output diverge often enough that skipping the "inspect" or "test" step is the single biggest source of real errors, not a rare edge case. Proof: the `title: null` validation bug, false "file applied" claims, the `mode="before"` vs `mode="after"` crash I only found by testing it myself, and the stale README test count all surfaced because this loop was followed, not skipped.