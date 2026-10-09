# scientific-workflow-skill

One shared scientific workflow skill for **Codex and Claude Code**, with separate native adapters. Project authority, explicit pauses and scientific gates remain in the projects. Claude's existing agents and settings are preserved.

| Path | Purpose |
| --- | --- |
| `skill/scientific-workflow/SKILL.md` | Shared ownership, execution, review, evidence and pause rules |
| `skill/scientific-workflow/references/` | Runtime-specific dispatch and supporting rationale |
| `agents/scientific_*.md` | Existing Claude native agents, unchanged |
| `agents/codex/*.toml` | Codex profiles, separately installed |
| `settings/settings.snippet.json` | Optional existing Claude snippet; never automatically merged |
| `scripts/install.sh` | Runtime selection, dry-run, all-destination preflight, backup receipts and rollback |
| `scripts/validate.py`, `tests/` | Local structure and temporary-home installer checks |
| `benchmarks/2026-10-08/` | Preserved Claude benchmark, including its original limitations |
| `docs/migration/2026-10-09/` | Historical Codex sources and source identity inventory |
| `docs/consolidation.md` | Migration contract, checks and activation record |

## Install

Python 3.11+ is required. The default remains Claude for backward compatibility:

```sh
scripts/install.sh --dry-run
scripts/install.sh
scripts/install.sh --check
scripts/install.sh --target codex --dry-run
scripts/install.sh --target codex --migrate
scripts/install.sh --target both --check
scripts/install.sh --rollback /absolute/path/to/receipt.json
```

Claude installation links the skill and the existing root agent files. Codex installation links the same skill under `~/.agents/skills/` and copies TOML profiles into `~/.codex/agents/` to preserve the tested native discovery shape. No duplicate skill is created under `~/.codex/skills/`. Agent and CLI settings are never rewritten.

A conflict blocks the entire installation before mutation. `--migrate` explicitly backs up conflicts; it does not discard them. Each changing install writes a receipt under `~/.local/state/scientific-workflow/transactions/`. Rollback first verifies every installed destination and backup; later edits block rollback rather than being overwritten. Automatic failure recovery also preserves concurrent edits, records conflicts and restores only unchanged owned paths. An interrupted or conflicting receipt requires manual inspection; it is never reported as a clean rollback. Check copied Codex profiles after source edits and reinstall with `--migrate` when needed.

`CLAUDE_HOME`, `CODEX_HOME`, `AGENTS_HOME` and `--state-dir` support temporary-home checks. Optional `--legacy-manual /path/to/SCIENTIFIC_AGENT_WORKFLOW.md` installs a compatibility pointer for Codex, preserving the old file through the same backup/receipt mechanism. See `scripts/install.sh --help`.

Legacy Claude `--uninstall` removes only exact owned links. Use a receipt rollback to undo a migration or Codex copied profiles; uninstall never deletes an unrelated real file. Restart sessions after changing native agents. Source skill edits become visible through links; stage and validate before publishing.

## Maintenance and evidence

Use `skill/scientific-workflow/maintenance.md` for native model checks and historical results. Explicit approval for a proposed workflow change authorizes its scoped implementation and validation; ordinary project work does not authorize self-modifying the skill or agents.

The preserved Claude benchmark reports 50 small-task runs and list-price estimates, with seeded-truth corrections. It does not establish long-task token savings, a universal model hierarchy or Codex behavior. The benchmark harness has machine-specific origamifolder7 paths. Raw run logs and generated fixtures remain outside this repo. No scientific project is resumed by installation or workflow testing.
