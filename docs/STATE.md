# Current state

One rolling file, read at session start. Update `Current work` in place at handoff and keep it short; move finished detail to [history](history.md). Git and the linked records hold the rest.

## Current work

Updated 2026-10-21. The user authorized a clearer discovery trigger and compact
long-task path. Staged implementation separates ordinary execution from optional
strict recovery, preserving existing bindings and project gates. The core plus
ordinary long-task reference is 767 words (previously 1,215). README includes a
project pointer and bundled-copy update policy; active projects were not edited.

Independent source review accepted the routing change. All 289 tests, repository
validation and the skill structure checker passed (exit 0). These are source and
offline checks, not evidence of better live skill selection or longer execution.
Native agents, scripts and models are unchanged. No new native trial or push.
Prior [native results and limitations](native-continuity-20261017.md) still apply:
Codex passed bounded manual-compaction episodes, Claude goal/compaction remains
unqualified, and multi-hour reliability and savings are unmeasured. Previous
commits through `7697f0a` were pushed after the user's explicit request.

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
