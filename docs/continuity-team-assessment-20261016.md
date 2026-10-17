# Astra team assessment of long-task execution

Three fresh-context native reviewers assessed source revision `64a72c7` against
`c20214a`. All used `scientific_reviewer`, `gpt-6-astra`, high effort, verified from
their actual session/turn metadata. This was a source/evidence assessment, not a
new execution benchmark. The owner combined their separate findings.

**Conclusion:** expect a conditional improvement in recovering recorded work, not
yet dependable long-task execution or demonstrated whole-task savings. Default
installation adds guidance and helpers; automatic recovery needs a verified local
binding, and continuation needs an authorized native goal. The inspected project
has no active recovery binding; pilot hooks are retired. The owner also queried
the current thread goal and received `null`.

| Reviewer ownership | Actual session ID |
| --- | --- |
| Task identity, coverage and recovery | `01a14782-5ab5-7ef2-8118-da27fb52b402` |
| Context cost and orchestration | `01a14782-7cb5-7dd2-86c3-f8185dc80379` |
| Continuation, stops and native evidence | `01a14782-9e70-79d2-b5c1-ae4dfff18946` |

Each received a disjoint question without inherited parent conversation and was
asked not to read sibling or prior reviewer conclusions. This was not a blinded
experiment: required startup state was visible. The efficiency reviewer disclosed
exposure to historical verdicts and excluded them from its evidence. Filesystem
separation was procedural. Reviewers made no edits or mutating test runs.

## What should improve, and what remains conditional

| Concern | Assessment |
| --- | --- |
| Recover the active question and listed work | Plausibly better with a correct binding: complete source sections, episode checks and pinned scope reduce specific recovery errors |
| Keep working on planned items | Pending IDs and Next are useful checks when invoked; they do not automatically select or execute the next task |
| Avoid context growth | One injection is bounded at 4,096 UTF-8 bytes; full prompt growth, repeated reconciliation reads and total cost are not bounded by that cap |
| Use subagents efficiently | Existing compact assignments, one owner and consequential reviews are sensible; these orchestration rules are unchanged from the baseline |
| Avoid unnecessary stops | Policy tells the owner to continue authorized work; the helper does not start a goal, wake an exited host or prevent a premature final answer |
| Complete the actual objective | Record consistency helps; artifact acceptance and scientific judgment remain separate checks |

The efficiency reviewer measured the Git blobs: entrypoint 3,940 to 4,131 bytes;
Codex/triggers/coordination combined unchanged at 12,219 bytes; optional continuity
reference 4,225 bytes. Loading all five documents is 20,575 bytes, up 4,416 bytes.
These are source bytes, not tokens, recurring prompt size or billed cost.

## Important limits found in the implementation

1. The pinned task IDs do not pin mutable task descriptions. A read-only in-memory
   probe replaced a full acceptance-suite task with reading one file; both records
   passed with the same contract. Essential outcomes and acceptance conditions
   must remain explicit in the pinned contract.
2. A correctly hashed `TEST FAILED` receipt can yield `records_complete: true`.
   The helper correctly also returns `acceptance: not_evaluated`; callers must not
   treat record completeness as a passing project check.
3. A stale binding in the same project can inject an internally consistent older
   episode. Episode matching checks configuration against saved files, not the
   live user's intent. Source reconciliation remains necessary.
4. Evidence for actual recovery used an earlier helper version and compactions
   after toy-task completion. Subsequent audits were explicitly prompted. Current
   74/256-test receipts match the current helper, but are offline evidence. No
   useful unfinished work through compaction was demonstrated.

Stopping at an explicit user pause, exhausted allowance or approval denial is
valid. Stopping after a routine checkpoint, or when an independent authorized item
remains available, conflicts with the workflow policy. Source instructions alone
do not establish that a model will always make this distinction correctly.

## Relationship to PStack

The design aligns with PStack's emphasis on verifiable work, scoped delegation
and [encoding lessons in structure](https://github.com/cursor/plugins/blob/main/pstack/skills/principle-encode-lessons-in-structure/SKILL.md).
PStack's [autonomous-run playbook](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/autonomous-run.md)
explicitly connects a checkable exit condition to Cursor's native loop and wake
mechanisms. This implementation leaves that runtime connection to project setup.
The [README](https://github.com/cursor/plugins/blob/main/pstack/README.md) describes
quality before parallel throughput. That is a design aim, not evidence that either
workflow is generally reliable. Sources were retrieved from mutable upstream
`main` on 2026-10-17 UTC; no PStack equivalence test was run.

## Smallest decisive next step

Use one primary runtime, current source and a verified project binding/native
goal for a separately authorized, capped trial. Compact while useful, independently
checkable work remains unfinished; provide no extra "continue" message. Verify
remaining task meaning, productive resumption, accepted outputs, cumulative budget
and valid stopping. Include one useful independent lane and full cost accounting
only if testing orchestration efficiency too. Keep the existing scientific pauses
and approval policy. This assessment does not authorize that pilot or a new framework.

No implementation changes or additional model-backed pilot were made for this
review. Existing check receipts remain under local, Git-ignored
`out/continuity-minimal/`; detailed prior evidence is linked from the
[implementation report](continuity-minimal-20261016.md) and
[original audit](continuity-audit-20261016.md).
