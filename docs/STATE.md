# Current state

One rolling file, read at session start. Update `Current work` in place at handoff and keep it short; move finished detail to [history](history.md). Git and the linked records hold the rest.

## Current work

Updated: 2026-10-14 (branch `codex-claude-shared-workflow-20261009`; published to GitHub).

- **README (2026-10-14):** compact introduction covering purpose, agent roles/models, installation and use. All 182 tests, documentation/skill checks and installer dry-run/check passed (exit 0). Logs and test scratch: `~/.cache/codex-scratch/task.g7Bm2Q` (about 2.3 MiB retained).

- **Active rules:** a checkpoint is not a stop (`e0f5592`); waits are sized to the job within runtime limits (`6c91cce`). Codex's own runtime instructions cap blocking waits at 60 s, and all 20 studied Codex sessions carry that cap, so the wait rule changes little for Codex.
- **Monitor:** `python scripts/long_task_monitor.py <session-id>` compares one long session with the 27-session baseline, offline (`35030d8`). Run it after the next long tasks. It shows whether stops and wait-only calls change, not whether outcomes improve.
- **Evidence behind the rules:** [long-task retrospective](../benchmarks/2026-10-13-long-task-retrospective/REPORT.md) and [Step 2 labels](../benchmarks/2026-10-13-long-task-retrospective/STEP2.md). Session length tracks outcome more strongly than any workflow signal. `stop_wanted` and `worth_cost` are optional user labels.
- **Maintenance overhead cut (2026-10-14):** older detail of this file moved to `history.md`; `maintenance.md` limits evidence to commits plus one short results note. Earlier `staging/` copies stay because frozen records reference them. Removed as disposable: Claude's staging worktree and patches (copies in `docs/long-task-rules-2026-10-14/`) and Codex test scratch `~/.cache/codex-scratch/task.WIwVDF`.
- **Unmeasured:** effects of both rules on early stops, outcomes and cost; helper break-even; long-task benefit of the workflow.

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

claude-mem's observer allowance is exhausted (again on 2026-10-13), so it records nothing; this file carries state between sessions. User-level skills installed 2026-10-09: `handoff`, `wait-what`, `writing-for-agents`, `retro`.
