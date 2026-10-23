# Current state

One rolling file, read at session start. Update `Current work` in place at handoff and keep it short; move finished detail to [history](history.md). Git and the linked records hold the rest.

## Current work

Updated 2026-10-22. Added the authorized 24-word verification clarification:
use or establish a working check of the actual outcome, choose a proportionate
method, and keep project-specific procedures with the project. Core is now 607
words; long-task reference remains 307. No new workflow layer, prescribed method,
review gate, script or native profile was added. This wording refinement required
no additional reviewer under maintenance guidance.

Staged away from live links. Repository validation, all 289 tests (390.142 seconds),
and skill structure checks passed (exit 0). After activation, both-runtime
installation (12 destinations) and instruction health passed (exit 0).
Validation logs: `/home/hao/.cache/codex-scratch/task._uhw6t9k/checks/`.
Shared links expose the change to Codex and Claude; existing sessions need to
reread the guidance. No profile restart is required. Runtime benefit is untested.

Prior changed-intent and unknown-outcome guidance is committed in `e87dca8`;
[research and review decisions](power-use-research-20261022.md) and historical
[native evidence](native-continuity-20261017.md) retain their limits.
Local Git checkpoint only; no push requested. The separate Sottiaux/Tan research
note and uploaded ZIP remain untracked and preserved.

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
