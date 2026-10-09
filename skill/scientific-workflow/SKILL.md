---
name: scientific-workflow
description: Route substantial scientific software, analysis, literature or hypothesis work to the scientific_* sub-agents (explorer, researcher, worker, analyst, reviewer) and decide when independent review is required. Use when planning or starting a substantial scientific task, when the user names a scientific_* agent or asks for an independent review, or when deciding whether to delegate. Skip routine small edits and simple questions.
---

# Scientific workflow (Claude Code)

Own the requested outcome through its authorized checks. Work alone when that is enough: Anthropic measured multi-agent research at about 15x the tokens of chat. Project instructions, pauses, frozen inputs and gates outrank this skill. Read the project's own plan and authority files before execution.

## Roles

Agent files are in `~/.claude/agents/`. Call a role by name; the files do not self-trigger.

| Role | Model / effort | Use | Never |
| --- | --- | --- | --- |
| `scientific_explorer` | haiku / high | Simple mechanical lookups: find files or symbols, count matches, list or diff names, read a log tail, check a path exists | Interpret, trace logic, judge results, write |
| `scientific_researcher` | sonnet / medium | Primary-source retrieval for one bounded question | Edit files |
| `scientific_worker` | sonnet / medium | Bounded change with owned files and named checks | Start jobs the brief does not name |
| `scientific_analyst` | sonnet / high | Evidence synthesis, authorized bounded analysis | Authorize new experiments |
| `scientific_reviewer` | opus / high | Independent review at the gates below | Edit or run anything |

Main thread: Sonnet 5.5, effort high. For plan or protocol design, use `opusplan` or `/model opus`. Deterministic work (run jobs, poll status, score) is ordinary scripts with no model.

## When to delegate

- Default is no delegate. Delegate independent, sizeable work (wide search, disjoint file sets, long logs) or an independent challenge.
- Tracing caller paths, mapping tests and reading design stay with the main thread or the analyst. The explorer only does mechanical lookups.
- At most 3 agents at once. No nested agents (set in `settings.json`). Give each writer separate files.

## Required review

Use `scientific_reviewer` before costly or consequential execution, for scientific claim or protocol changes, after a recurring failure or evidence that invalidates the direction, at substantial completion where the project requires it, and whenever the user asks. Project-required reviews are mandatory. Do not use it for routine edits or to double-check your own small steps.

Brief it with the original requirements, decisions, exact artifact versions (paths and git ref) and raw-evidence paths. Give no desired verdict. It has no shell, so write diffs and log excerpts to files first. It reports every finding with a severity; you filter. Its disposition is not a project gate.

## Brief for any delegate

A delegate has no conversation history. Give: deliverable, scope, authority (pauses, frozen inputs), artifact identity, checks to run, resource limit, stop boundary, output format.

## Calling and overrides

- Call by name with the Agent tool (`subagent_type` = role). If the user names a role or writes `@agent-scientific_reviewer`, that exact role must run.
- Per-call settings win over the agent file. "Use fable" for a review: pass `model: "fable"`. If that call errors, is refused or runs another model, rerun once with `model: "opus"` and say so.
- For a hard or long worker or researcher task, pass `effort: "high"`.

## After a delegate returns

- Check the result against artifacts (paths, test output), not the narrative. A "done" with no evidence is not done.
- Then continue the authorized task to its next step without asking. Stop only at a declared boundary, an explicit pause or a real blocker.
- Review says revise: fix blocking and major findings, rerun the affected checks. Re-review only for a concrete unresolved finding.
- Work that depends on a running delegate waits for it. Independent work may continue.
- A review or a passing check does not authorize new scientific execution (a new run, campaign or retry). Only the user's task and the project plan do.
- Report execution success separately from scientific improvement. Reviewer approval is not scientific acceptance.

## Evolving this workflow

Do not edit this skill or the agent files on your own. When daily work shows a failure (wrong tier, missed finding, over-delegation, bad model), propose the edit with the evidence and wait for approval. `maintenance.md` has the model-check procedure, the evolution log and open questions. Record each accepted change there.
