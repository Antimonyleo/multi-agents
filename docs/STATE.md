# Current state

One rolling file, read at session start. Update `Current work` in place at handoff and keep it short; move finished detail to [history](history.md). Git and the linked records hold the rest.

## Current work

Updated 2026-10-22. Completed the authorized power-use plan: two independent
Astra reviews narrowed scope; a fresh third reviewer accepted the final patch.
Changed-intent propagation and unknown-outcome recovery now live in existing
references. Core stays 583 words; long-task reference is 307 words (was 272).
No new scripts, profiles, hooks, planner or readiness layer were added.

All 289 tests, repository validation, skill structure, both-runtime installation
(12 destinations) and instruction health passed. The skill links expose the
changes to Codex and Claude; existing sessions need to reread changed guidance.
No profile restart is needed. These source/offline checks do not demonstrate
improved multi-hour behavior, native steering delivery or safe external retries.
Historical [native evidence and limits](native-continuity-20261017.md) remain.

[Research, decisions, agent identifiers, checks and rollback](power-use-research-20261022.md)
are recorded outside the production skill. Local Git checkpoint completes this
maintenance; no new push was requested. Earlier `fcc894b` is already pushed.
Uploaded ZIP, other sessions and paused projects are preserved.

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
