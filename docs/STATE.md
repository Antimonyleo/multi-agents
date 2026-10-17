# Current state

One rolling file, read at session start. Update `Current work` in place at handoff and keep it short; move finished detail to [history](history.md). Git and the linked records hold the rest.

## Current work

Updated 2026-10-16. The continuity-v2 audit is checkpointed in the
[audit report](continuity-audit-20261016.md). Candidate `c298775` is on the separate
`continuity-v2-20261016` branch; live skill source remains at `c20214a`. Do not
merge or broadly activate it: native qualification is incomplete and the pilot
exposed semantic failures. No push or real scientific work was performed.

Three independent fresh-context reviews and separate adjudication were performed.
Final candidate checks passed: 229 repository tests, 107 supplied tests (serial),
validators and temporary-home installation/rollback. Retained failures include an
optional wrapper defect, one timing failure, contaminated Claude startup, a false
report claim and premature contract retirement. The scope-change probe was blocked
by native approval; no policy bypass or alternate edit was used.

Both runtimes completed the toy plan without a "continue" prompt. Real manual
compactions were observed after completion, not during unfinished science. There
is no long-session reliability or savings claim. Raw local evidence remains in
`out/continuity-v2-{audit,pilot}/` (Git-ignored); the uploaded ZIP and isolated source
worktree `/home/hao/.cache/codex-scratch/continuity-v2.dby2dhwe/upstream` are retained.
Owned native pilot processes exited and project-only hook bindings were retired;
shared services, model settings, global hooks and permissions were not changed.

Next qualification requires useful unfinished work through native compaction,
Claude resume-hook/current-version checks, permitted scope amendment and memory
isolation. This does not authorize more model sessions or resume paused science.
The [reusable task prompt](long-task-prompt.md) works with the current workflow.

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
