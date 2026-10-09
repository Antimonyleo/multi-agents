# Current state

One rolling file. Update `Current work` in place at handoff; do not add dated copies. History lives in git and the linked records.

## Current work

Updated: 2026-10-09 (branch `codex-claude-shared-workflow-20261009`, HEAD `a6ba754`; no push recorded).

Goal: a shared Codex/Claude scientific workflow skill with separate native adapters, checked against measured execution.

Done, with the record that proves it:
- Shared skill, adapters, installer and rollback: `docs/consolidation.md`.
- Ownership, review-packet and progress rules: `docs/efficiency-validation-2026-10-09.md` (38 tests passed).
- Role triggers and milestone review schedule: `docs/trigger-refinement-2026-10-09.md`.
- Calibration preparation: `benchmarks/2026-10-09-calibration/PROTOCOL.md`. Six offline fixtures and a 13-test harness are ready.

Dead ends:
- The reused harness cannot test native `scientific_*` roles. Its isolated Claude mode cannot invoke the shared skill, so its results are not workflow evidence.
- Claude main is now `opus` at high effort (`RUNTIME_REFRESH.json`). Sonnet-main text in `maintenance.md` is stale for current runs; leave settings alone and freeze them per arm.

Next action: with the user's go-ahead, build the smallest native capture adapter named in the protocol. Do not launch live runs before it exists.

Open (user only): authorize the live pilot (4 top-level sessions, at most 2 support calls), or leave it unexecuted. Not authorized yet.

Boundaries that persist:
- Project2 stays `USER_PAUSED_DO_NOT_RESUME`. No scientific tests, prediction, acquisition, construction or MD.
- Native Claude agents, Codex profiles, settings and the 2026-10-08 benchmark stay unchanged.
- Other sessions' edits and jobs are preserved.

## Open questions

Kept in `skill/scientific-workflow/maintenance.md`, section "Open questions". Not copied here.

## Checks

```sh
python scripts/validate.py
python -m unittest discover -s tests -v
```

Use temporary homes for installer checks. Static checks do not prove live routing or savings.

## Session memory

claude-mem's observer allowance ran out on 2026-10-08, so it records nothing. This file carries state between sessions instead. Skills installed 2026-10-09 (user-level, not in this repo): `handoff`, `wait-what`, `writing-for-agents`, `retro`. Their session-start hook is not installed.
