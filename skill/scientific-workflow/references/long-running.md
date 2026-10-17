# Long-task continuity

Use for authorized multi-milestone work, not trivial requests. This is an extension
of scientific-workflow, not another planner or permission system.

## Preserve the question; keep the method flexible

In the existing plan, retain a short `## Execution contract` section: `Episode: id`,
research question, deliverable/evidence standard, allowed exploration, resource
limits, and essential conventions or patterns that must survive recovery. Include
only consequential invariants; link detailed methods, known failures, units and
reference results. A null or inconclusive result can complete the agreed inquiry.
Never make a desired positive result the only stopping condition.

Pin that section's digest when binding a long episode. Normal milestones and
method choices do not change the pin. Work outside the section may evolve freely
within scope. An explicitly authorized scope change may update the section and
pin with its authority recorded; a mismatch alone is not permission to repin.
This detects accidental drift, not a hostile writer with configuration access.

## One rolling checkpoint

Reuse the existing state record. Keep `## Boundaries` current and put `Episode: id`
in `## Current work`. Preserve the current milestone and its purpose, verified
results/evidence paths, essential decisions and rejected paths, open uncertainties,
owned jobs, remaining budget, and the next meaningful action. Use concise prose,
not another database. Save before expensive work, after consequential results or
changed instructions, and before handoff. Replace atomically when practical.
Do not summarize summaries: reconcile with the original plan and evidence.

After recovery, read the bound source, then verify files and owned jobs before
relaunching or claiming completion. The hook supplies complete source sections or
an explicit unverified-handoff warning; it never silently clips a next action.
Keep the selected content small enough for the 4,096-byte injection cap. Archive
historical detail rather than removing active constraints or negative evidence.
The hook cannot save facts that were never written or validate scientific claims.

## Continue the science, not the housekeeping

Continue the next authorized, unblocked milestone after checkpointing. Choose
methods and useful detours autonomously within the plan. A detour should resolve
an actual dependency or uncertainty affecting that milestone; otherwise defer it.
If successive attempts add no relevant evidence, change approach or report the
specific blocker instead of polishing logs, formatting, or repeating the same try.
Do not add a new approval, checklist, review agent or state update per tool call.

Use the host's native goal/continuation mechanism where verified available. An
active plan alone does not implement turn continuation. Preserve live user pauses,
existing review gates and cumulative budgets across restarts; native counters may
reset. Do not claim overall success merely because a bounded episode ended.

## Jobs and delegates

Prefer existing native background jobs, scheduler receipts and completion events.
Record command/config identity, owner/job ID, logs, outputs and the expected
completion signal before launching. Missing terminal evidence means unknown, not
permission to rerun. Process exit zero is not scientific acceptance. Keep execution inside the actual allocation; a submission receipt alone does not
establish job completion.

Give delegates bounded questions and the relevant plan/evidence paths. They return
concise findings; only the owner writes shared state. Use task-specific worktrees
or bindings for concurrent owners. Long-lived delegates need their own handoff;
do not inject the parent's active task into every child automatically.

When only waiting remains, use a native completion event rather than model polling.
An exited runtime needs an explicitly authorized native/external wake mechanism;
this extension does not supply one. On pause, pause the native goal and revoke
applicable wake ownership. Recovery never overrides a user pause.
