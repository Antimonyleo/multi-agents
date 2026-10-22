# Long-task execution and recovery

Use the project's existing plan and rolling checkpoint, including for single-agent
work. Ordinary execution needs no new record format or hook.

1. Read the current objective, authority, acceptance checks and remaining items.
   After context loss, reconcile completed evidence, changed requirements and owned
   jobs before acting. Missing job evidence is unknown, not permission to rerun.
2. Work on the next incomplete, authorized item. Resolve dependencies that advance
   acceptance; defer unrelated cleanup. If an item is blocked, continue independent
   authorized work. Preserve explicit pauses, review gates and cumulative limits.
3. After meaningful progress and before handoff, update completed checks, decisions,
   failures, owned jobs, remaining budget and the next action in that same record.
   Continue after checkpointing; a progress report is not a completion condition.
4. Finish when the requested deliverables and named acceptance checks are complete.
   Otherwise report the exact unresolved boundary and remaining work.

Use an explicitly authorized native goal when continuation between turns is needed.
A saved plan alone cannot wake an exited host; this skill adds no wake service.

For optional bound hooks, digest-pinned tasks, structured verification receipts or
atomic record replacement, read [strict recovery](strict-recovery.md). Read it also
when an existing binding or project gate requires those checks; retain their
validation and pause protections.
