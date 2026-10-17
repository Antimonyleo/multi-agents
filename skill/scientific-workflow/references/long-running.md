# Long-task continuity

Reuse the existing plan and checkpoint. Keep the objective, acceptance conditions,
units, evidence-retention rules and cumulative limits in `## Execution contract`, with
`Episode: id`. Pin its digest when binding recovery; progress and method choices
belong outside that section. Null results can complete scientific inquiries.

Keep `## Boundaries` and `## Current work` current: same episode, next meaningful
action, results (including negative/inconclusive evidence), decisions, owned jobs
and remaining budget. One owner writes
after consequential changes and before handoff, not every tool call.

## Recover and continue

The optional `scripts/recover.py hook` restores whole selected sections within
4,096 UTF-8 bytes or reports HANDOFF_UNVERIFIED. Bind only the active project and
episode to verified native lifecycle events. Use `--help` for arguments. Keep
historical detail outside injected sections; avoid global or inherited bindings.

After recovery, reconcile the original task, checkpoint, artifacts and owned jobs.
Memory/transcript summaries are leads, not replacement authority or proof of done.
Another task's COMPLETE state cannot close this one. Missing job evidence means
unknown; consult existing receipts/completion events before considering a rerun.

Use verified native goals for continuation. After checkpointing, continue the next
authorized, unblocked item. Continue another authorized item when one is blocked. Preserve user pauses,
scientific gates and cumulative budgets when counters reset.
This skill supplies no wake mechanism for an exited host.

At existing milestone boundaries, check whether work advanced acceptance or
resolved a dependency. Necessary scientific detours are valid. Repeated attempts
without useful evidence call for a changed approach or an exact blocker. Defer
unrelated cleanup; reuse required reviewers without a standing monitoring team.

## Optional task check

Reuse the plan's checklist with stable IDs. List them in the pinned contract's
`Tasks:` field; put task rows under `## Tasks` and Status/Next in Current work:

```markdown
## Execution contract
Episode: repair-1
Repair with named regression checks; preserve public behavior.
Tasks: inspect, repair, verify
## Tasks
- [ ] inspect: reproduce
- [ ] repair: implement the correction
- [ ] verify: run final acceptance checks
## Boundaries
Use authorized files/budget; retain failures.
## Current work
Episode: repair-1
Status: active
Next: repair
```

Checked rows link local evidence: label `evidence`, destination
`repro.log#sha256=ACTUAL_SHA256` (actual file hash).
`recover.py check` checks episode/contract, exact task coverage, next item and
checked tasks' evidence hashes: nonempty, at most 256 KiB per file, 32 files,
128 links and 1 MiB total accepted bytes. Link short receipts for larger logs. `hook --check-tasks` adds a compact progress
summary, not the task list. Contradictions or changed/missing evidence make the
handoff unverified. Other projects can retain their existing format.

Status is `active`, `paused`, `blocked` or `complete`; paused/blocked need `Reason:`.
Next names a pending ID or `none`. `check --completion` exits nonzero unless every
task is evidenced and Status is complete. It does not run checks, interpret logs
or prove scientific truth. Run named acceptance commands and required review
before marking done.

## Change scope safely

An authorized scope change may revise contract and binding. A mismatch alone never
permits repinning. Preserve the original source and reason for the change.
For a combined record, `recover.py replace` validates a candidate,
checks the expected current file hash, preserves raw prior bytes and atomically
replaces the file. Boundaries/episode and structured paused status stay fixed; `--check-tasks`
also validates progress. This assumes one writer, not concurrent
editors or a multi-file transaction.

Retire the original only after success. Verify before separately rebinding; an
old binding reports an unverified handoff meanwhile. Denied approval or failed
writes leave the original authoritative. A draft is not active; never label the
original superseded early or weaken acceptance to declare success.
