# Power-use gaps: online research, 2026-10-22

Research candidates (narrowed by the independent review below) were operational: propagate changed intent, recover safely
from ambiguous failures, verify runtime capabilities, and measure behavior at those
boundaries. The shared skill already has substantial planning, evidence, budget,
review and context guidance. Adding a larger planning framework is not justified.
The final implementation accepts only two guidance changes; see the decision below.
Neither the research nor the source review demonstrates improved runtime performance.

## Scope and method

Compared repository revision `fcc894b` with primary vendor documentation, first-party
engineering reports and current pstack source. Covered execution/recovery, context,
coordination, evaluation, environment/tool interfaces, observability and trust.
A bounded research subagent covered durable execution; the owner inspected the
local implementation and synthesized the other areas. In that research phase, no new model-backed pilot,
scientific execution, runtime reconfiguration or production skill edit was performed.

Sources were opened on 2026-10-22. Live docs and GitHub `main` are mutable; this is
not a reproducible snapshot of external implementations or an exhaustive literature
review. Vendor reports show designs in their environments, not causal evidence for
our installation. Proposals below are our inferences from those sources and the
local gap analysis. Search results alone were not used as supporting evidence.

## Existing coverage worth keeping

- `SKILL.md`: one execution owner, selective support, separate verification rigor,
  project authority, scientific claims and explicit pause protection.
- `references/long-running.md`: existing checkpoint, dependency investigation,
  bounded improvement, and explicit distinction between saved state and wake-up.
- `references/strict-recovery.md` and `scripts/recover.py`: pinned contract/task
  identity, bounded recovery context, artifact hashes and verification receipts.
- `references/coordination.md`: cumulative budgets, terminal evidence after timeout,
  one progress owner, whole-task accounting and independent evidence.
- `scripts/native_calibration.py`: comparison manifests, native capability inventory
  and permission evidence for evaluation. Reuse these concepts rather than adding
  a second evaluation framework.
- Existing continuity tests cover stale evidence, changed task definitions, session
  mismatch, pauses and malformed inputs. The gap is not an absence of such tests;
  it is incomplete qualification of actual runtime transitions and sustained work.

The [native results](native-continuity-20261017.md) remain the local evidence:
bounded Codex passes after manual compaction, a five-minute productive episode,
and an unqualified Claude goal/compaction path. The later 289-test passes establish
software regression checks, not multi-hour reliability or improved discovery.

## 1. Changed intent must reach active workers

**Source finding.** Cognition describes conflicting implicit decisions among parallel
writers and reports useful patterns with shared context and controlled writes.
Cursor's scaling experiment also reports failures of shared-file self-coordination.
These are different designs at different scales, not a universal ban on parallelism.
[Cognition](https://cognition.com/blog/multi-agents-working),
[Cursor](https://cursor.com/blog/scaling-agents).

**Local gap.** Assignments now carry purpose and constraints at dispatch. The skill
does not specify how a later user correction reaches already-running delegates, or
what to do with a result produced against superseded requirements. Contract hashes
can detect changed records but do not distribute a live instruction.

**Small proposal.** At a material change, record its revision in the existing plan,
identify affected owners, deliver the change through native messaging, and reconcile
returned artifacts against the current requirement before integration. Record an
acknowledgment at a supported execution boundary; do not pretend this makes a pending
tool call instantly interruptible. A pause takes effect immediately in coordination
policy and is not delayed until acknowledgment. No second message queue.

**Acceptance.** In a disposable future native test, change a requirement while a
worker is active. Verify obsolete output is not silently accepted and a pause does
not trigger more execution. Offline checking alone cannot prove message delivery.

## 2. Recover operations, not just conversation

**Source finding.** Temporal restores workflow state from durable event history.
LangGraph retains successful node writes across a failed super-step. AWS recommends
bounded retries at one layer and warns against retrying persistent errors or
non-idempotent operations. These mechanisms are more specific than a text checkpoint.
[Temporal](https://docs.temporal.io/encyclopedia/event-history),
[LangGraph](https://docs.langchain.com/oss/python/langgraph/checkpointers),
[AWS](https://docs.aws.amazon.com/wellarchitected/2024-06-27/framework/rel_mitigate_interaction_failure_limit_retries.html).

**Local gap.** Timeout reconciliation is already required. There is no concise
classification of transient failure, persistent failure, unknown effect and confirmed
cancellation. A crashed response may follow a successful write or job submission.

**Small proposal.** In the existing optional recovery reference, distinguish safe
retry from unknown effect. For consequential operations, retain the native operation
or job ID and inspect its outcome. Retry only within existing authority/budget when
transient failure and safe repetition or deduplication are established. Otherwise
reconcile or report the boundary. Never reset the budget to retry.

GitHub cancellation involves conditional jobs and staged process signals. The
transferable lesson is that cancellation requested and cancellation confirmed are
different states; its exact timings are not Codex/Claude guarantees.
[GitHub cancellation](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-cancellation).

**Acceptance.** Simulate a completed side effect followed by lost acknowledgment;
recovery must not duplicate it. A canceled controller with a surviving child must
remain nonterminal/unknown until owned process evidence resolves it.

**Defer.** Do not adopt Temporal, LangGraph, a database, or an always-on scheduler
unless an actual unattended deployment needs them. Skills cannot supply durable
wake-up, atomic external writes, or exactly-once execution by instruction.

## 3. Declare which capabilities actually work

**Source finding.** Anthropic's harness work combines persistent artifacts with
working environment setup. Its infrastructure study demonstrates that resource
configuration affects agentic evaluation outcomes. Configuration belongs in the
measurement, not merely the installation instructions.
[Long-running harness](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents),
[Infrastructure noise](https://www.anthropic.com/research/infrastructure-noise).

**Local gap.** Installer checks establish paths/profile consistency; historical native
trials establish narrow behavior at tested versions. They do not certify every current
runtime/environment. Capability inventory already exists in evaluation tooling but
is not a compact user-facing readiness result.

**Small proposal.** Reuse existing checks to summarize skill path/revision, runtime
version, available native goal/recovery mode, effective permissions where observable,
and enforced versus advisory budgets. Separate `configured`, `observed working`, and
`unverified`; offline checks must not claim native delivery. Cache unchanged results
by relevant version/configuration, rather than launching model probes every task.

**Acceptance.** A broken link, unsupported hook, stale observation or unavailable hard
quota must be visible. A configuration-only pass must never become a runtime pass.
Do not invent a universal cross-runtime adapter for absent capabilities.

## 4. Evaluate lifecycle behavior and evaluator validity

**Source finding.** Anthropic distinguishes capability tests from regression tests,
recommends cases grounded in real failures and known-good reference solutions, and
separates occasional success from consistency across repeated trials. METR time
horizons use human task duration and a specified success probability; they are not
agent wall-clock uptime measurements.
[Agent evaluations](https://www.anthropic.com/research/demystifying-evals-for-ai-agents),
[METR methodology](https://metr.org/time-horizons/).

**Local gap.** Unit coverage is substantial, but the actual lifecycle remains only
partly qualified. The after-task monitor's textual stop candidates are not verified
unwanted stops, and raw token totals do not measure useful progress.

**Small proposal.** Extend the existing evaluation lane with a small failure matrix:
changed requirement, pause during work, real compaction with pending work, ambiguous
job completion, stale evidence, unsupported runtime feature, and resource exhaustion.
Use known-good and known-bad controls for each evaluator. Label offline fixtures,
real native transitions, and productive long-session evidence separately.

For ordinary authorized work, retain completed/required outcomes, unwanted stops
requiring manual adjudication, repeated owner work, invalidated evidence and total
owner/helper/integration cost. These are diagnostic dimensions, not one invented
quality score. Compare like workloads and environments before asserting savings.
No benchmark launches are authorized by this research note.

## 5. Make the environment easier to use and verify

**Source finding.** OpenAI describes repository-local knowledge, machine-enforced
architecture, and accessible application observability. Anthropic recommends focused
tools with bounded relevant output rather than broad tools that flood context.
[Harness engineering](https://openai.com/index/harness-engineering/),
[Tool design](https://www.anthropic.com/research/writing-tools-for-agents).

**Local gap.** The skill teaches good evidence handling, but cannot guarantee that a
project has a reproducible environment, a useful acceptance command, or runtime
observability. More prose cannot repair those project-level defects.

**Small proposal.** Prefer the project's existing lint/types/schema checks, test
entrypoint and application diagnostics. Where repeated failures justify an interface
repair, make commands return concise status/errors plus a full-log path. Keep
versioned setup and test commands discoverable. Fix the real caller/test seam once
rather than adding repeated review instructions. No universal tool wrapper is needed.

**Acceptance.** A fresh authorized environment can run the documented check, detect
a seeded failure and return usable diagnostics. Tool summaries retain references to
full evidence, including negative outcomes.

## 6. Invalidate stale evidence and integration assumptions

**Source finding.** pstack's pickup playbook reconstructs operational state, compares
done versus pending work and verifies inherited claims on the actual artifact.
Its pause playbook distinguishes explicit suspension from continued execution.
[Session pickup](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/session-pickup.md),
[Pause safely](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/pause-safely.md).

**Local gap.** Strict receipts invalidate changed pinned outputs and inputs. Semantic
assumptions, dependency changes, environment changes and conflicting design choices
can still invalidate results even when different workers edited different files.

**Small proposal.** Carry source/base identity and consequential assumptions in existing
returns. Before integration, check compatibility and run affected acceptance on the
combined artifact. Reopen only evidence affected by a concrete change. Record the
reason an old conclusion is no longer current; preserve its historical result.

Use existing worktrees/ownership for independent writers. Shared live environments,
ports, caches and data need explicit ownership too; file separation alone does not
isolate those resources. Do not introduce a distributed locking system for one owner.

Do not copy pstack's automatic WIP commit, transcript-authority wording or `/tmp`
checkpoint location into this project: our user authority, storage and pause rules
remain controlling. Its mutable playbook is inspiration, not governing policy.

## 7. Treat context as versioned evidence with a trust boundary

**Source finding.** Anthropic recommends retrieving relevant context through lightweight
references. MCP maintainers explicitly say tool annotations are hints, not security
guarantees. These are distinct issues: relevance does not establish trust.
[Context engineering](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents),
[MCP annotations](https://blog.modelcontextprotocol.io/posts/2026-03-16-tool-annotations/).

**Local gap.** The strict helper already separates memory from authority, validates
paths and bounds injected bytes. Broader project use can still import stale decisions
or third-party instructions through retrieved material and delegate summaries.

**Small proposal.** Keep source identity, scope and freshness beside consequential
retrieved facts; load details on demand. Preserve the distinction between user
instructions and source material. Use native sandbox/permission controls for tool
access; a reader role or `readOnlyHint` is not isolation. Retain minimal evidence,
with secrets excluded from shared summaries and exported traces.

**Acceptance.** A retrieved page or prior transcript asking for unrelated actions does
not gain authority. A changed source invalidates dependent conclusions when relevant.
Do not add broad scanning, automatic memory deletion or a home-grown injection filter.

## 8. Make accounting and enforcement legible

**Source finding.** OpenTelemetry maintains GenAI conventions for spans, metrics and
events, offering a vocabulary for instrumentation. It is an interoperability option,
not a requirement to operate an agent. The older docs path now redirects readers to
its separate conventions repository.
[Current GenAI conventions](https://github.com/open-telemetry/semantic-conventions-genai).

**Local gap.** The monitor correctly handles current token counters, but incomplete
telemetry cannot establish complete cost. Recorded budgets do not necessarily have
runtime enforcement. A long wait, active computation and useful completed work are
different quantities.

**Small proposal.** Reuse native session/task/operation IDs and existing logs. Add
observed enforcement and missing-accounting status to the existing task record when
needed. Associate consequential tool results and acceptance evidence with task IDs.
Only add a trace exporter if existing logs prove insufficient for a concrete diagnosis;
keep full sensitive content out of default exports.

**Acceptance.** Parent, helper and integration costs can be reconciled without double
counting; missing values remain unknown. A policy-only deadline is never reported as
an enforced process timeout. Account for infrastructure failures separately.

## Initial recommendations (narrowed by the final decision below)

1. **Compact optional guidance:** changed-intent propagation and interruption/retry
   reconciliation. These directly target drifting workers and duplicate work.
2. **Reuse existing tooling:** a read-only readiness summary and a small lifecycle
   failure matrix. Specify what is offline versus native before implementing tests.
3. **Learn from real tasks:** manually adjudicate a bounded sample of stop candidates,
   missed requirements and duplicate work. Improve the tool/project seam responsible.
4. **Only if demonstrated necessary:** an external durable runner, enforced quotas,
   deeper traces or stronger concurrency isolation, implemented in the runtime/project
   layer rather than the skill entrypoint.

Keep the production core near its current size. Reuse existing references, tests and
checkers. Do not add a permanent reviewer team, recursive coordinator, another planner,
custom Stop loop, blanket reruns, or provider-wide settings changes.

## Evidence limits and verification of this note

This survey supports candidate designs and priorities, not reliability percentages,
cost savings or availability of a feature on this account. Vendor anecdotes are not
matched experiments. METR's cited page was last updated 2026-09-08 and says it is no
longer actively updated; only its definitions are used here. Mutable source links were
checked for relevant content, not archived as immutable dependency pins.

The local gap assessment used the skill entrypoint, both runtime adapters, continuity
and coordination references, strict recovery, maintenance guidance, test names and
selected calibration/monitor code. It was not a complete security audit or proof of
absence across every project. Reader subagents supplied sources; the owner verified
sources used for the major recommendations and wrote this combined note.

## Independent review and implementation decision

The user requested a team challenge and execution of a minimal plan. Two separate,
history-free `scientific_reviewer` agents (configured Astra/high) independently
inspected revision `fcc894b`, the research and implementation:
`/root/minimal_gap_review` and `/root/independent_scope_review`.
Both recommended two guidance edits and rejected additional machinery. These are
actual native agent identifiers, not simulated reviewer roles. A separate
`/root/named_source_check` researcher checked attribution. The runtime exposed
these canonical identifiers; no separate provider session UUID is claimed.

Accepted: notify affected delegates of material intent changes, apply pauses
immediately, and reconcile returned artifacts with current requirements. Extend
recovery to unknown write/submission outcomes and distinguish requested
cancellation from confirmed termination. Changes live in the existing coordination
and long-task references. The core remains 583 words; the ordinary long-task
reference grows from 272 to 307 words. No scripts, hooks, profiles or schemas change.

Deferred: readiness wrapper/cache, new lifecycle harness, failure taxonomy,
revision registry, retry engine, scheduler and permanent reviewer team. Existing
checks already cover installation drift and several recovery invariants. They
cannot certify effective runtime capability. Add code only at an actual failed
operation or evaluator seam; a wrapper would not repair the historical Claude
command-entry failure.

### What the named sources actually support

- **Lauren Tan:** pstack's [session pickup](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/session-pickup.md)
  reconstructs done/pending work from the prior trail and checks inherited claims
  against the actual artifact. Our existing checkpoint and acceptance rules cover
  this. Preserve its principle without copying Cursor-specific machinery.
- **Sam Altman:** [Three Observations](https://blog.samaltman.com/three-observations)
  describes prospective engineering agents with uneven abilities that still need
  human direction. This supports retaining authority and oversight; it supplies
  no concrete recovery implementation or measured benefit for this skill.
- **Dario Amodei:** the [March 10, 2025 CFR transcript](https://www.cfr.org/event/ceo-speaker-series-dario-amodei-anthropic)
  distinguishes writing code from specifying conditions, design and integration
  with existing code. Existing purpose/constraints and acceptance rules cover
  most of this; keeping changed requirements current is our local inference.
  His dated predictions are not acceptance evidence.
- **Tibo:** assumed to mean Thibault Sottiaux; the user has not confirmed the
  identity/post. The source lead is [OpenAI podcast episode 6](https://www.youtube.com/watch?v=OXOypK7_90c).
  Page extraction did not expose a full primary transcript of his detailed
  prescriptions, so no Tibo-specific requirement is claimed. OpenAI's engineering articles are not
  automatically statements by Sottiaux or Altman.

### Validation plan and evidence boundaries

| Concern | Existing check / evidence | Limit |
| --- | --- | --- |
| Pending work concealed by completion | `test_continuity_progress.py::test_invalid_completion_does_not_hide_pending_work` | Structured record, not free-form agent behavior |
| Pause retained after record updates | `test_continuity_progress.py::test_scope_replacement_cannot_resume_paused_record` | Offline helper behavior |
| Changed task meaning or stale outputs | `test_definitions_pin_meaning_but_allow_status_and_evidence_changes`, `test_changed_frozen_verifier_and_stale_outputs_fail` in that module | Does not deliver changes to workers |
| Paused or unresolved dispatch | `test_behavioral_fixture.py::test_completed_paused_dispatch_is_rejected_but_unresolved_is_unknown` | Evaluator control, not native cancellation |
| Real compaction and continuation | [Retained native evidence](native-continuity-20261017.md) | Bounded historical Codex runs; Claude unqualified; no multi-hour claim |
| New steering / lost acknowledgment guidance | Independent source review; no executable seam changed | Native message delivery and safe retry behavior remain untested |

Run repository validation, all unit tests and the skill checker in isolation;
obtain fresh final source review, then activate and check installation/instruction
health. No wording-matching tests or synthetic replay will be presented as native
behavior. This maintenance launches no new lifecycle pilot or scientific work.

Rollback: revert the maintenance commit, preserving later unrelated work, and
rerun repository and installation checks. No runtime settings need restoration.
Reusable prompt: "Use the existing plan and checkpoint. Complete authorized items
through their checks. Propagate changed requirements to affected delegates and
check returns against current requirements. Reconcile unknown action outcomes
before retrying; preserve pauses and limits. Report evidence and unresolved work."

### Required check results

Staged outside live links at `/home/hao/.cache/codex-scratch/task.k9a9hM/stage`.
`python scripts/validate.py`, `python -m unittest discover -s tests -v`
(289 tests, 67.834 seconds), and the skill structure checker all exited 0.
The full suite includes installer tests with temporary homes. Logs and exit
receipts are in that staging directory's sibling `checks/` directory; this note
is the durable summary. No new implementation tests were added for prose alone.
Fresh final source reviewer `/root/final_compact_review` (Astra/high, no inherited
conversation or plan authorship) accepted the candidate after checking the diff,
word counts, named checks and receipts. After activation,
`bash scripts/install.sh --target both --check` passed all 12 destinations and
`agent-workflow check --repo .` passed, both exit 0. Shared links now expose the
references to Codex and Claude; existing sessions must reread them. No native
profiles changed and no profile restart is needed. Local commit only; no new
push was requested for this maintenance.
