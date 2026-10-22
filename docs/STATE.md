# Current state

One rolling file, read at session start. Update `Current work` in place at handoff and keep it short; move finished detail to [history](history.md). Git and the linked records hold the rest.

## Current work

Updated 2026-10-22. User authorized compact improvements from the supplied
Workbench lessons, verification, commit and push. Verification rigor is separate
from execution shape; assignments carry their overall purpose. Long-task guidance
now covers bounded investigation and baseline/evaluator/limit discipline for
improvement. Core plus long-task reference: 855 words (previously 767).

All 289 tests, repository validation and skill structure checks passed (exit 0).
Independent routing review accepted the change. These offline/source checks do
not establish improved live behavior. No scripts, native
profiles, strict recovery protocol or other projects were changed. No new runtime
trial is authorized by this maintenance. Prior [native evidence and limits](native-continuity-20261017.md)
remain: bounded Codex manual-compaction passes, Claude lifecycle unqualified,
and multi-hour reliability and savings unmeasured. Earlier compact update
`ad43dfd` was pushed on the user's request.

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
