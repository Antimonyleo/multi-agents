# Minimal continuity update

This release adds **experimental, opt-in source support** for keeping long tasks
on track. It installs no hooks, goals, memory settings, wake service or reviewer
team. The earlier [native pilot](continuity-audit-20261016.md) does not qualify the
new checks or establish long-session reliability.

## What changed

| Need | Smallest implementation |
| --- | --- |
| Keep the active task distinct | Project/episode-bound recovery with a pinned scope section; reuse the current plan/checkpoint |
| Retain unfinished items | Optional Markdown task IDs, checked against the pinned list, plus explicit status/next item |
| Detect unsupported completion | Checked tasks require current, nonempty, hashed evidence; completion refuses pending items |
| Continue after reports | Use authorized native goals; continue another authorized item when one is blocked |
| Return from unhelpful detours | Check progress against acceptance at existing milestone boundaries; no new monitor agent |
| Replace state safely | Explicit combined-record replacement preserves prior bytes, boundaries, episode and structured pauses; it never rebinds a hook |

`recover.py check` is read-only and does not run or interpret project acceptance
checks. Its output distinguishes complete records from scientific acceptance.
The replacement command assumes one writer; it is not a concurrent-editor or
multi-file transaction. Evidence verification caches resolved paths and limits
references/files/accepted bytes. Hook output stays capped at 4,096 UTF-8 bytes and
never silently clips source. No transcript or memory-store scanning is added.

The main skill gains **191 bytes** versus `c20214a`; its full entrypoint is 4,131
bytes. The conditional reference is 4,225 bytes. Code/tests are not injected as
instructions, and there are no per-tool reminders. These are byte counts, not
token measurements or savings claims.

## PStack inspiration

Reviewed the official Cursor plugin again on 2026-10-16:

- [Session pickup](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/session-pickup.md): reconcile completed/pending work and verify inherited claims against artifacts.
- [Autonomous run](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/autonomous-run.md): keep a checkable exit condition and return to it after detours.
- [Plan checker](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/scripts/check-plan.mjs): encode checkable requirements in code.

These ideas were adapted to the existing workflow, without copying PStack code or
installing its playbooks, model settings, multi-lane panels or heartbeat system.
An additional verification skill would duplicate the repository's existing checks.

## Verification and corrections

The full repository suite passed **256/256 tests**, including **74 recovery/task
tests** (27 new here). Repository validation, skill structure, instruction health,
temporary-home installation/check and receipt rollback passed with exit 0.

One independent native `scientific_reviewer` reviewed the change without inherited
conversation: `01a14749-a7ca-7623-94f6-2860ed090a9f` (configured Astra/high).
Its disposition permits source-only experimental support after the named checks.
Three findings were corrected: a default-path pause guard, excessive repeated
evidence reads, and wording that put newly obtained negative results in the pinned
contract. The reviewer independently reproduced the evidence-read fix in memory.

Initial validation rejected a nonexistent example link; the documentation now
describes its placeholder without presenting it as a real repository link. A
focused test initially retained a Next pointer after completing that fixture task;
the fixture was corrected. Failed logs remain beside the final passing receipts
under local, Git-ignored `out/continuity-minimal/`. Raw evidence is not in a clone.

No new model-backed pilot was launched. The new checks/replacement have offline
evidence only. Useful unfinished work through native compaction, current Claude
resume-hook delivery, memory-enabled isolation and successful native scope
amendment remain unqualified. Prior classifier blocks remain intact; this update
does not complete the denied toy edits or change approval policy.

## Use and rollback

The [on-demand reference](../skill/scientific-workflow/references/long-running.md)
describes the optional format and helper commands. The [task prompt](long-task-prompt.md)
works with the existing workflow without a hook. Automatic recovery requires a
separately verified project-local binding. Installed links expose the source
update; models, native agent profiles and global settings are unchanged.

Rollback the two source commits on `continuity-minimal-20261016` (`df1cf90` and
the following implementation commit) in reverse order. No global settings need
restoring. Preserve any prior-record backups and retire owned project bindings
before removing a callback target. No remote push is part of this maintenance.
