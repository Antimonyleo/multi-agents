# Workflow repository guidance

This repository maintains a shared Codex/Claude scientific workflow. Read the [skill](skill/scientific-workflow/SKILL.md) and only the active runtime adapter before changing routing. Use the [maintenance guidance](skill/scientific-workflow/maintenance.md) for validation.

At session start read [current state](docs/STATE.md); the user starts `/handoff`, which updates its `Current work` section.

Preserve native runtime differences. Claude agent definitions remain in `agents/scientific_*.md`; Codex profiles remain in `agents/codex/*.toml`. Do not rewrite either runtime's native agents, links, models, tools or settings merely to support the other. Native-agent changes need their own explicit scope. Keep frozen benchmark evidence and historical migration snapshots unchanged.

Stage changes away from live links. Complete the authorized maintenance through its named checks and local Git checkpoint. Keep consolidation and coordination-policy changes in separate commits. Validate with `python scripts/validate.py`, `python -m unittest discover -s tests -v` and the skill structure checker where available. Use temporary homes for installer checks. Do not automatically launch a model-backed benchmark, change account settings or push.

Workflow maintenance does not resume any paused scientific objective or authorize scientific tests, prediction, acquisition, construction or MD. Project authority and explicit pauses remain with their projects. Preserve other sessions' jobs and edits.
