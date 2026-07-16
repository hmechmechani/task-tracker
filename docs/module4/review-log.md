# AI Review Log — Dockerfile / .dockerignore (commit e495708)

Reviewed with: Claude Code (R1 review prompt)

| # | File/Section | Severity | Category | Issue | Bucket | Reasoning |
|---|---|---|---|---|---|---|
| 1 | .github/workflows/ci.yml (nearby) | medium | CI | Docker image is never built in CI, so a Dockerfile-breaking change wouldn't be caught automatically | Useful (deferred) | Real gap, verified against ci.yml's actual content (pytest -v only). Out of Part 4.2's stated CI scope, so logged as a follow-up rather than fixed now. |
| 2 | Dockerfile:4-6 | medium | Docker | requirements.txt includes pytest/httpx, so test-only deps get baked into the runtime image | Useful (deferred) | Real, verified against requirements.txt content. Fixing properly means splitting requirements-dev.txt and reworking the CI install step — more scope than this module asked for. |
| 3 | Dockerfile:1,8 | low | Docker | No exact version/digest pinning on the base image or dependencies | Noise | Technically valid but beyond what the module required (explicit slim base, not latest — already satisfied). |
| 4 | Dockerfile:4-6 | low | Docker | No build toolchain fallback if a platform lacks prebuilt wheels for pydantic-core | Noise | Speculative; the actual build succeeded, and prebuilt wheels exist for all mainstream Docker Desktop target platforms. |
| 5 | .dockerignore:6-7 | low | maintainability | __pycache__/ and **/__pycache__/ are redundant | Useful (fixed) | Verifiably true, trivial one-line fix applied. |
| 6 | .dockerignore | low | Docker | tests/, docs/, frontend/ aren't excluded from build context despite never being copied | Useful (fixed) | Verifiably true against Dockerfile's COPY lines, trivial fix applied to shrink build context. |

## Personal AI-review rule
I will use Claude Code review for a broad first pass on real diffs, but I will only act on a comment after re-checking it against the actual file myself — and I will only fix issues that stay within the current module's stated scope, logging anything bigger as a follow-up instead of expanding scope mid-review.
