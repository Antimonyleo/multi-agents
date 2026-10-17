# Current state

One rolling file, read at session start. Update `Current work` in place at handoff and keep it short; move finished detail to [history](history.md). Git and the linked records hold the rest.

## Current work

Updated 2026-10-16. The [minimal continuity update](continuity-minimal-20261016.md)
adds experimental source helpers: bound task recovery, optional task/evidence/next
checks and explicit safe replacement of one combined record. Existing plans and
native goals are reused. No hooks, goals, wake loops or memory settings are installed.

Staged and reviewed on `continuity-minimal-20261016`, based on `7721585` plus the
reviewed core (`df1cf90`, equivalent to original `c298775`). Named final checks
passed: 256 repository tests (74 continuity tests), validators and temporary-home
installation/check/receipt rollback. One independent reviewer cleared the source
for opt-in experimental support after three fixes. Logs/receipts remain local in
`out/continuity-minimal/`; the uploaded ZIP and prior audit/pilot are preserved.

The [earlier native audit](continuity-audit-20261016.md) has limited fixed-scope
observations only. New task/replacement helpers have offline evidence. Useful
unfinished work through native compaction, current Claude resume hooks, normal
memory-enabled isolation and a permitted scope amendment remain unqualified.
Do not claim solved long-session drift, automatic completion or savings. No new
native model pilot or remote push was performed. Original pilot hooks remain
retired; shared services, approvals and native agent/model settings are unchanged.

Three fresh-context Astra/high reviewers assessed source `64a72c7` on the user's
request. Their [team assessment](continuity-team-assessment-20261016.md) expects
conditional recovery benefits; default continuation and whole-task efficiency
remain unproved. No source changes or new native execution pilot were made.

Use the [task prompt](long-task-prompt.md). Source support is opt-in experimental;
automatic recovery requires a verified project-local binding. No further scientific
or model-backed qualification campaign is authorized by this handoff.

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
