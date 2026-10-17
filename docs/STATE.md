# Current state

One rolling file, read at session start. Update `Current work` in place at handoff and keep it short; move finished detail to [history](history.md). Git and the linked records hold the rest.

## Current work

Updated 2026-10-17. Authorized native tests and local integration are complete;
see [results and limits](native-continuity-20261017.md). Configured Codex recovery
passed in 155.257 / 900 seconds on unchanged helpers from `9c5fcc9`. A separate
Codex maintenance task finished 5/5 milestones after manual compaction with one
independent child in 305.641 / 1,800 seconds, without automatic recovery injection.
Claude startup delivery passed; goal-entry protocol failed, with no retry or
lifecycle acceptance. The old Codex mismatch cause remains unknown. Multi-hour
reliability and savings remain unmeasured; no further trial is authorized here.

Monitor repair `6f0ec54` now selects validated native counters and preserves unknown
usage. Final portable-source checks: 289 tests, validation, skill checker and
instruction health passed; installed links passed for both runtimes. Astra review
closed the fixture portability issue. Production skill, helpers and native settings
are unchanged. Goals/bindings retired; scientific pauses preserved. No push.
Raw evidence and original accepted worktree remain in ignored
`out/continuity-native-20261017/`; do not treat their terminal plans as new authority.

## Boundaries

- Project2 stays `USER_PAUSED_DO_NOT_RESUME`. No scientific tests, prediction, acquisition, construction or MD.
- Native Claude agents, Codex profiles, settings and frozen benchmark evidence stay unchanged.
- Other sessions' edits and jobs are preserved. No model-backed benchmark, settings change or push without the user.

## Fresh session

Start in `~/githubrepo/scientific-workflow-skill`; read `AGENTS.md` and this file, then linked records only as needed. Both installed skill links point into `skill/scientific-workflow/`, so edits there are live at once: stage elsewhere. Transcripts: Claude `~/.claude/projects/`, Codex `~/.codex/sessions/`. The evaluation runner is an external dependency in `~/githubrepo/sequence_design/tools/workflow_evaluation/` (see [history](history.md#exact-starting-point-and-checkpoints)); do not merge or run its broad suite automatically.

## Checks

```sh
python scripts/validate.py
python -m unittest discover -s tests -v
/usr/bin/python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skill/scientific-workflow
agent-workflow check --repo .   # instruction health, where available
```

Use temporary homes for installer checks. Static checks do not prove live routing or savings.

## Session memory

The 2026-10-13 observer allowance exhaustion is historical, not a current disabled-state guarantee. On 2026-10-16, enabled claude-mem injected another toy arm's results into startup; that comparison was invalid. The corrected pilot excluded it per invocation only; global settings/data remain unchanged. This file is the explicit project handoff. User-level skills installed 2026-10-09: `handoff`, `wait-what`, `writing-for-agents`, `retro`.
