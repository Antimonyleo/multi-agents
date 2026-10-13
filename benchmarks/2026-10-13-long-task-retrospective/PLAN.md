# Long-task retrospective: plan (frozen before extraction)

Written 2026-10-13, before any outcome inspection. Offline and read-only: no
model calls, no runtime or settings change, no scientific execution. Project2
stays `USER_PAUSED_DO_NOT_RESUME`; reading its transcripts is inspection only.

## Question

In real long sessions on this machine, where do tokens and time go, how much
goes to helpers and orchestration, and which signals of drift or repeated work
appear? The answer should show where a workflow rule or helper could plausibly
help. It cannot show that one would. This is observational: tasks differ in
difficulty, so there is no causal comparison and no savings estimate.

## Sample (selection rule)

- **Claude parents:** main transcripts `~/.claude/projects/<P>/*.jsonl` whose
  project directory is a real work directory (`sequence-design`,
  `origamifolder7`, `origamifolder7-kinetic`, `AI-codex-direc`), with at least
  100 distinct assistant responses. Excluded: `-tmp-*` scratch projects,
  benchmark workspaces, claude-mem observer sessions and this repository
  (workflow maintenance, not project work).
- **Codex parents:** top-level sessions (source `cli`, `vscode` or `exec`)
  whose `cwd` is `sequence_design`, `origamifolder7` or `AI/codex_direc`, with
  at least 100 model-call token events.
- **Families:** each parent plus all its descendants. For Claude, that is
  `<session>/subagents/*.jsonl`. For Codex, it is sessions linked through
  `parent_thread_id`, recursively, including guardian reviews.
- **Freezing:** some sessions are still live. Each file is frozen at its byte
  length when sampled, with the SHA-256 of that prefix. Only complete lines
  inside the prefix are parsed.

## Measures (scripted; candidates are not proven waste)

| Area | Measure |
|---|---|
| Size | Wall span; active time (inter-record gaps capped at 10 min); user prompts; responses; tool calls; turn durations where recorded |
| Tokens | Claude: input, cache-creation, cache-read and output, deduplicated by message ID. Codex: input (includes cached), cached and output (includes reasoning), from the last cumulative counter, which may omit compaction calls. Per-call context size and its growth |
| Compaction | Count; rereads within the first 20 tool calls after each compaction |
| Delegation | Helper count by role and model; helper token share; Codex orchestration calls (spawn, wait, follow-up, send, list, interrupt); forked versus fresh helpers; guardian reviews |
| Redo after helper (Claude only) | Parent `Read` of a file the helper read, within 30 parent tool calls after the helper returned |
| Repeated work | Identical `Read` (path and range) with no intervening write to that path; identical shell command with no intervening edit |
| Drift signals | User interrupts; correction-like prompts (regex, precision checked by spot reading); tool errors |

Not measured: billed dollars (no verified price table for every model);
Codex redo-after-helper (helper messages are encrypted and file access sits
inside exec wrappers); scientific correctness. Outcome quality comes only from
the user's Step 2 labels.

## Deliverables

`sample.json` (frozen identities), `extract.py`, `summary.json` (aggregates
only, no transcript text beyond short prompt excerpts), `labels.csv` (Step 2
sheet), `REPORT.md`. Raw transcripts stay at their host paths.
