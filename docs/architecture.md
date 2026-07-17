# Task Tracker Architecture — Context Engineering Comparison (Module 5, Part 5.5)

The same architecture-document task was run three ways in Codex App, in separate fresh threads, to observe how context quality affects agent output. Full drafts are in `docs/architecture-A.md`, `docs/architecture-B.md`, and `docs/architecture-C.md`.

## Strategy Comparison

| Strategy | What it got right | What it got wrong, missed, or invented | Best suited for |
|---|---|---|---|
| A — Minimal context | Surprisingly complete — Codex chose to inspect files anyway despite minimal task framing, so it ended up close to fully-grounded. Correctly cited transition rules, storage mechanics, and conventions. | Nothing factually wrong, but conflated "inspecting files" with "minimal" — didn't actually test whether a truly context-starved run would invent things, since Codex read broadly on its own initiative anyway. | Tasks where the agent has enough autonomy and trust to explore and decide what's relevant on its own. |
| B — Structured context | Most complete and confident. AGENTS.md supplied pre-verified business rules (transition table, tag limits) without needing to re-derive them from raw code, so it stated things with full confidence and got all of them right. | Missed nothing factually here, but this strategy is only as good as the context fed into it — if AGENTS.md had contained an error, this run would have confidently repeated it without independently re-checking. | Tasks where verified, trustworthy context already exists (like a checked AGENTS.md) and fast, confident, complete output is the goal. |
| C — Targeted context | Narrowest but most honest. Correctly refused to state anything about `business_rules.py`, tests, frontend, or CI, because it was told to read only 3 files and stuck to that boundary rather than inferring from framework convention. | Missed real content that exists (transition rules, overdue logic, tests, frontend, CI) — not because it got anything wrong, but because the file list was too narrow for a genuinely complete onboarding doc. | Narrow, high-stakes questions where an honest "not visible" is more valuable than a confident guess — e.g. auditing one specific subsystem. |

## Verdict

Strategy B was chosen as the working architecture reference. Its underlying AGENTS.md had already been independently verified against real files during Part 5.1 (transition table, tag limits, and run/test commands were all cross-checked directly against `app/business_rules.py` and `app/models.py`), so its confidence in this run is earned, not assumed. It is also the most complete of the three without sacrificing accuracy — unlike Strategy C, which is honest but too narrow to be a useful standalone onboarding document on its own.

The chosen content is `docs/architecture-B.md` in full; this file records the comparison and the reasoning, not a fourth copy of the content.

## Context-Engineering Rule

For tasks where I already have a verified, trustworthy project-guidance file, I use structured context (Strategy B) because it produces complete, confident output without re-deriving facts from scratch. For narrow or high-stakes questions where guessing would be worse than an honest gap, I use targeted context (Strategy C) because its "not visible" answers are more trustworthy than a broad strategy's confident-but-unverified claims.
