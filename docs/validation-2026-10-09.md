# Consolidation validation and activation - 2026-10-09 UTC

Outcome: one shared skill is active for Codex and Claude Code. Separate native runtime adapters retain the existing agent systems. All named local migration checks are complete. Project 2 remains `USER_PAUSED_DO_NOT_RESUME`; no paused-project tests, executors, workers or scientific artifacts were changed by this maintenance.

## Checkpoint

Local branch: `codex-claude-shared-workflow-20261009`. Nothing was pushed.

| Checkpoint | Commit | Scope |
| --- | --- | --- |
| Recovery baseline | `c0174f8` | Original Claude skill, agents, settings snippet and benchmark |
| Consolidation | `36cacc2` | Shared entrypoint, runtime references, separate Codex profiles, installer, tests and source archive |
| Efficiency rules | `2648897` | Dependent execution ownership, evidence-ready review, compact changes and durable job progress |
| Validation record | This checkpoint | Review disposition, actual installation and preservation results |

## Required checks

| Check | Observed result |
| --- | --- |
| Temporary-home installer suite | 21/21 tests passed, 3.186 seconds; terminal output in `install-tests-2026-10-09.txt` |
| Shared skill structure | skill-creator `quick_validate.py`: valid |
| References and native profiles | `python scripts/validate.py`: 5 local links resolve; 5 Codex TOML profiles parse with expected configured settings |
| Protected repository sources | 74 original Claude/benchmark/settings-snippet file hashes unchanged |
| Installed/source preservation | 87 protected identities unchanged, including Claude native source files and live links, installed Claude settings, Codex config and all five existing Codex profiles |
| Installed destinations | `scripts/install.sh --target both --legacy-manual /home/hao/SCIENTIFIC_AGENT_WORKFLOW.md --check`: passed, 13 destinations |
| Instruction health | `agent-workflow check` passed for this repo and the paused project; non-executing checks only |
| Independent staged review | Fresh scientific_reviewer configured gpt-6-astra/high: initially REVISE, then CONTINUE after a concrete recovery defect was corrected |
| Review scenarios | Six hypothetical cases evaluated for each adapter: small edit, extraction, probe implementation, incomplete review packet, unavailable reviewer and paused science plus maintenance |
| Receipt and backups | Completed transaction contains exactly the two intended changes; both backups verified; source revision `2648897` |
| Installation idempotence | Post-activation dry-run: 0 changes |

The regression suite exercises dry-run/no writes, Claude default compatibility, Codex isolation from Claude, shared target links, copied native TOML files, idempotence, conflict preflight, missing sources, overlapping/aliased destinations, invalid parent paths, migrations and full rollback, broken-link restoration, destination/backup drift rejection, unrelated-file preservation, partial-write cleanup and intervening destination/backup edits during automatic failure recovery.

The independent review found that automatic recovery could delete an intervening edit after a later failure. The corrected installer stages writes in temporary paths, verifies destination/backup identities, preserves detected edits and reports `failed_conflicts` with the retained receipt. The original partial-copy cleanup test and two new concurrent-edit regressions all pass. See `review-2026-10-09.md`.

## Activation and rollback

Claude's existing skill link continues to point to the same repository folder; all five native agent links and their contents are unchanged. The real Codex skill directory was backed up and replaced with a link to that same folder. The old home manual was backed up and replaced with a compatibility pointer. The existing Codex TOML files already match the new repository sources, so activation did not rewrite them. Both CLIs' installed settings/config are unchanged. No duplicate `~/.codex/skills/scientific-workflow` was created.

Receipt:

`/home/hao/.local/state/scientific-workflow/transactions/b2dc55cf2cef4b01a4ba9a53c7207cb1/receipt.json`

Backups:

- `/home/hao/.agents/.scientific-workflow-backups/b2dc55cf2cef4b01a4ba9a53c7207cb1/scientific-workflow`
- `/home/hao/.scientific-workflow-backups/b2dc55cf2cef4b01a4ba9a53c7207cb1/SCIENTIFIC_AGENT_WORKFLOW.md`

Undo activation with the retained receipt:

```sh
scripts/install.sh --rollback /home/hao/.local/state/scientific-workflow/transactions/b2dc55cf2cef4b01a4ba9a53c7207cb1/receipt.json
```

Receipt rollback restores these two prior global destinations; it does not revert repository source commits or alter Claude agents. Source reversions are separate Git operations. Later installed-path or backup edits block receipt rollback. Interrupted receipts and detected recovery conflicts require inspection; do not claim automatic crash recovery or general concurrent-writer isolation.

## Limits and next use

This establishes local structure, installation, source preservation and the reviewed scoped recovery behavior. It does not establish fresh native model dispatch, enforced child sandbox isolation, real scientific performance or token savings. No new headless model campaign was run. The earlier Claude benchmark remains historical evidence with its original limitations.

Use a new session to ensure the current skill and adapter are loaded; native agent definitions did not change. Read only the adapter for the active runtime. One execution owner keeps dependent work; consequential reviews receive evidence ready for their decision; mechanical helpers have bounded assignments. Maintain the shared policy here and change native profiles only within explicit runtime-specific scope. Scientific continuation still needs a direct user instruction resuming the paused Project 2 objective.
