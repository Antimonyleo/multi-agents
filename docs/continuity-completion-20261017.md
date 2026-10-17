# Continuity fixes: 2026-10-17

Strict completion checks and optional session binding are ready for experimental
use. Native automatic continuation worked in one short Codex task after real
compaction. **The full recovery test did not pass:** the hook rejected its session
binding. Claude native continuation/compaction remains untested. This is not proof
of reliable long sessions or lower total cost.

## Changes

- Pin task descriptions as well as IDs. Checking rows and updating evidence leave
  the pin unchanged; silently changing a task fails strict validation.
- Require a structured verification receipt for completion: the pinned command,
  integer zero exit, frozen verifier/inputs and current output hashes must match.
  Failed, missing or stale receipts fail. Legacy completed records cannot bypass it.
- Preview or explicitly apply a project/session-bound hook with `scripts/bind.py`.
  Preserve unrelated native settings; require explicit replacement of owned bindings.
  Other-session state is withheld. Setup never trusts a hook or creates a goal.
- Bound callback/evidence reads and reject FIFOs, oversized inputs and escaped paths.
  Keep the 4,096-byte recovery cap and existing one-owner orchestration.

No new planner, Stop loop, permanent review team or global settings. The main skill
entry is unchanged by this update. Details load only when long-task recovery is used.
Receipts check recorded assertions and current bytes; they do not authenticate
execution, user intent or scientific truth. Explicit pauses still prevail.

## Evidence

| Check | Result |
| --- | --- |
| Focused continuity tests | 93 passed |
| Full repository tests | 275 passed |
| Repository validation, skill structure, instruction health | Passed |
| Temporary-home install, check and receipt rollback | Passed |
| Codex unfinished-work native compaction | Completed while repair/verify remained pending |
| Codex subsequent native continuation | Productive work; goal complete; one initial user turn, no continue prompt |
| Independent parser acceptance | 12 output records + 20 extra requirement cases passed; frozen inputs/task meanings unchanged; strict completion exit 0 |
| Codex bound-context recovery | **Failed:** startup and postcompact hooks returned HANDOFF_UNVERIFIED, session mismatch; each 547 bytes |
| Claude native goal/compaction | **Untested:** long `/goal` input became pasted text; native UI confirmed no goal set |

Codex 0.163.0, default gpt-6.1-sol/high, thread
`01a14b23-e7e4-7753-ac1e-b69ba4e45bdb`: 149.17 seconds elapsed against a
900-second limit. Exactly one compaction request. This was a finite parser-repair
mechanism test, not scientific acceptance or a matched performance comparison.
A pre-inference resume failure and trust-only setup failures were retained.

Claude 2.1.302, default Opus 5.5/high, session
`ac83cc26-12de-4a37-a8ea-209648385c80`: reproduction and checkpoint only.
Automatic review rejected a follow-up goal command because it could invalidate
the no-new-user-message protocol. No bypass or favorable-results retry. The enabled
memory plugin injected older project context; global plugin settings stayed unchanged.

Astra release reviewer `01a14b1a-5548-7fe1-903b-c6ce2cb2bf9d` verified the
source checks and permitted this limited experimental release. The bounded callback
read defect found in review was fixed before the final 275-test run.

## Use and limits

Use [the reusable prompt](long-task-prompt.md). Recovery is opt-in. Native trust,
`hooks/list` and on-disk equality do not prove the active callback binding. Require
SOURCE_MATCHED_ONLY from a real matching-session native event before relying on it.
The mismatch cause is unknown; stale cached configuration is only a hypothesis.
Manual reconciliation remains necessary on failure. No untested reload sequence is
presented as a fix. Multi-hour productivity, automatic compaction and orchestration
savings remain unmeasured; this update does not change agent profiles or models.

Raw evidence is retained locally under `out/continuity-completion/`: `final-*.json`
and logs, `codex-live.json`, `codex-live-events.jsonl`, `codex-grade.json`,
`claude-outcome.json`, terminal logs, `binding-retirement.json` and `evidence-notes.json`.
It is Git-ignored and is not uploaded by this checkpoint. Exact tested script hashes:

- recover.py: `b2f44087f7151e5819a99ff03651f9fdb6361b1ce73470dcdbec35925edf0f85`
- bind.py: `0e1ac91da2a7e83e5ecb4e0ffc848cd6c061704fbe8abdb2d1a1e0d71df6ebac`

Owned pilot bindings were retained inactive; the Codex goal was paused after native
completion and owned standalone processes exited. Shared services and scientific
pauses were preserved. An early disconnected trust-only shared UI was not independently
confirmed inactive; no task prompt or goal was sent to it and the shared daemon was
left untouched.

Rollback: revert the local commit titled “Pin task meaning and verification; add
experimental session binding”. For any later opt-in binding, first retire only its
owned hook, preserving unrelated entries; restore the saved prior config if needed.
Keep the stable callback and evidence until all bindings using them are retired.
No default hooks or goals require removal. No remote push is included.

## Final design review against pstack

A fresh Astra/high reviewer, session `01a14b33-ec03-7181-a090-220bfe8182cb`,
found no consequential source defect requiring another implementation change at
`9c5fcc9`. Owner compared current upstream pstack playbooks on 2026-10-17;
upstream `main` is mutable. This was read-only source/evidence review, with no
new model-backed execution pilot or repeated test suite.

Pstack's [autonomous-run playbook](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/autonomous-run.md)
also separates a checkable exit condition from native wake/continuation. Its
[orchestration playbook](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/orchestrate.md)
reserves persistent queues and coordinator layers for programs larger than one
agent can finish. Its [verification guidance](https://github.com/cursor/plugins/blob/main/pstack/skills/create-verification-skill/SKILL.md)
requires proof through the real user path, not configuration checks alone.

Decision: freeze feature scope. Keep one plan, one execution owner, bounded helpers
and existing verification checks. Do not add another planner, reviewer layer or
persistent queue. Reused-agent assignments already carry current requirements;
automatic propagation of later parent-only steering is not guaranteed.

Runtime qualification remains open. The next useful work is capturing the actual
callback arguments and native event identity to diagnose the Codex mismatch, then
proving recovery through the real lifecycle. Claude needs verified native goal
entry before its lifecycle test. Neither is replaced by this review or authorized
by this note. Only after that should a representative longer task assess sustained
focus and unnecessary stops; whole-task savings still need separate matched evidence.
