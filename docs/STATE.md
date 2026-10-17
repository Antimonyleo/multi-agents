# Current state

One rolling file, read at session start. Update `Current work` in place at handoff and keep it short; move finished detail to [history](history.md). Git and the linked records hold the rest.

## Current work

Updated 2026-10-17. User-authorized Astra findings addressed through required checks
and a limited experimental source checkpoint. [Results and limits](continuity-completion-20261017.md).
Task descriptions, structured verification receipts and bounded session binding now
have 93 focused / 275 full passing tests; validators and temporary-home installation
and rollback passed. Main skill entry and native agent/model settings unchanged.

Codex completed useful unfinished work after real native compaction with no continue
prompt; independent acceptance passed. Its recovery hook rejected the session binding,
so the full recovery endpoint FAILED. Claude native lifecycle remains UNTESTED after
a pasted-command driver error; follow-up command rejected by automatic review. No
retry or permission bypass. Optional hooks remain experimental; verify actual matching
native delivery before relying on them. No general reliability or savings claim.

Pilot goals/bindings and owned standalone processes retired; retained local evidence
in `out/continuity-completion/`. Shared services and scientific pauses preserved.
Fresh Astra design review against pstack found no required implementation change.
Freeze feature scope; native recovery qualification remains open. See the results
note for the review and exact next checks.
No further pilot, scientific work or push is authorized by this handoff. Start new
maintenance from current instructions and [the task prompt](long-task-prompt.md).

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
