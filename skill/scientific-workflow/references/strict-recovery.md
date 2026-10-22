# Strict recovery and verification

Use this optional protocol when configuring or maintaining bound recovery, or when
the project requires these strict checks. Existing bindings retain their checks;
the lightweight execution path does not waive them.

Reuse the existing plan/checkpoint. Put objective, acceptance conditions, units,
evidence-retention rules and cumulative limits in `## Execution contract`, with
`Episode: id`. Pin its digest; progress and method choices stay outside it.
Keep `## Boundaries` and `## Current work` current: same episode, next meaningful
action, results (including negative evidence), decisions, jobs and remaining budget.
One owner writes after consequential changes and before handoff, not every tool.

## Recover and continue

Use an explicitly authorized native goal to retain the objective between turns.
Continue the next authorized, unblocked item after checkpointing. A blocked item
does not block independent authorized work. Preserve user pauses, scientific
gates and cumulative budgets across restarts; never reset accounting to continue.
This skill adds no Stop loop or wake service for an exited host.

`scripts/bind.py` previews an optional, experimental project/session-bound native hook. Supply runtime,
project, plan/state, episode, anchor digest and actual native session ID; consult
`--help`. `--apply` changes only that project's native config and preserves unrelated
entries. Existing owned bindings need inspection and explicit `--replace-owned`.
Review/trust through the host's native `/hooks` flow; setup never bypasses it.
Trust, `hooks/list` and on-disk equality do not prove the active callback binding.
Before relying on recovery, observe matching-session SOURCE_MATCHED_ONLY from a
real native event. A mismatch requires manual reconciliation, never automatic repinning.
Use a stable callback path; retain it until every owned binding is retired.

The read-only recovery hook returns whole selected sections within 4,096 UTF-8
bytes or HANDOFF_UNVERIFIED. New bindings use strict checks and reject other-session
state. Rebind a new session or changed task only after reconciling current authority.
A changed request within the same session still needs owner judgment; saved files
cannot independently identify live user intent. Memory summaries are leads, not
replacement authority. Reconcile source/artifacts/jobs before acting; missing job
evidence is unknown, not permission to rerun. Keep history outside injected sections.

## Check task meaning and completion

Reuse a single-line checklist under `## Tasks` with `- [ ] id: description` rows.
The contract's `Tasks:` lists IDs; `Task definitions:` pins the output of
`recover.py tasks-digest`. Checked rows append a Markdown link labelled `evidence`,
with destination `receipt.log#sha256=ACTUAL_SHA256`. Status/evidence updates do not
change task meaning. Authorized requirement changes need a new reviewed pin.

Current work has `Status: active|paused|blocked|complete` and `Next: pending-id|none`;
paused/blocked need `Reason:`. Run `recover.py check --strict` with the existing
binding arguments. It checks task meaning, exact coverage, next item and current
evidence. Legacy record-only checks disclose their weaker limits.

Pin one `Verify:` JSON policy in the contract: `argv` is the acceptance command
array, `inputs` maps frozen verifier/input paths to SHA-256 values, and `outputs`
lists required output paths. For completion, the existing acceptance harness writes
a JSON receipt with `episode`, `anchor_sha256`, `argv`, integer `exit_code`, `inputs`
and `outputs` (path-to-hash map). Record its project-relative path and hash in
`Verification: receipt.json#sha256=ACTUAL_SHA256` in Current work.

`check --completion` requires strict records, zero exit, matching command/identity,
frozen inputs and current outputs. Failed, missing or stale receipts do not pass.
The helper never executes saved commands or interprets arbitrary logs. Receipts
are recorded assertions, not authenticated execution or scientific truth; run real
acceptance and required review. A negative scientific result can validly complete.
Reads are bounded: 256 KiB/file, 32 unique files, 128 references, 1 MiB accepted
bytes. Use concise receipts pointing to retained full logs.

## Retain focus and replace safely

At existing milestones, check whether work advanced acceptance or resolved a real
dependency. Keep necessary scientific detours; defer unrelated cleanup. Repeated
unproductive attempts call for a changed approach or an exact blocker. Reuse
required reviewers; add no permanent monitoring team.

For one combined record, `recover.py replace` validates a candidate, checks the
expected current-file hash, preserves prior bytes and atomically replaces the file.
Boundaries, episode and structured pause remain; `--check-tasks` validates progress.
It assumes one writer, not a concurrent-editor or multi-file transaction. Retire
the old source only after success, verify, then separately rebind. Until then a
changed contract gives an unverified handoff. A denied/failed edit leaves the old
source authoritative; never label it superseded early or weaken acceptance.
