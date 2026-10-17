# Prompt for a long task

Use this with the scientific workflow. Replace the bracketed parts. For runtimes
with a verified native goal command, explicitly create a goal with the text below
to retain the objective between turns. A saved plan alone does not cause automatic
continuation.

```text
Complete [outcome] through every authorized item in [existing plan], verified by
[named tests, evidence and deliverables]. Preserve [scientific standards, units,
controls, negative evidence and protected inputs]. Work within [paths, resource
limits and cumulative budget]. A negative or inconclusive result is valid.

Reuse the existing plan and rolling checkpoint. Keep the question and acceptance
conditions distinct from progress. Save consequential results, decisions, owned
jobs, remaining budget and the next meaningful action before a handoff. After
context loss, reread the original authority and checkpoint, then reconcile files
and jobs before continuing. Missing job evidence is unknown; do not blindly rerun.

Choose methods and necessary scientific detours within scope. Defer unrelated
cleanup. Continue the next authorized, unblocked item after each checkpoint;
status reports do not end the task. Stop at an explicit user pause, a genuine
permission/resource/capability boundary, a failed check needing my decision, or
verified completion. Report remaining work and the exact boundary if blocked.
```

For a project with experimental recovery already configured and verified, add:

```text
Use the bound Execution contract and Current work sections for this episode.
A source digest confirms identity, not scientific truth or authority to resume.
Reconcile any mismatch with the current instruction; never repin merely to silence
an error. Preserve user pauses and cumulative budgets across compaction or resume.
```

The optional source helpers are experimental. Automatic recovery requires a
verified project-local binding; no hooks or goals are installed by default. This
prompt also works without a hook.
