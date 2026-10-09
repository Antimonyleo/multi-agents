# Benchmark protocol: scientific-workflow (frozen 2026-10-08, before any scored run)

Two probe runs on 2026-10-08 checked only that the baseline arm hides the skill and
blocks the five agents. They were not scored.

## Question

Does the workflow (skill + `scientific_*` agents + settings caps) (a) add no token
overhead on small and mechanical tasks, (b) save tokens on a long task, and (c) keep a
long, constrained task on track, compared with plain Claude Code?

## Arms

Same user config, same main model (`--model sonnet`, effort high from `settings.json`),
same fixture code. Headless: `claude -p`, `--permission-mode dontAsk`,
`--allowedTools "Read,Grep,Glob,Bash,Edit,Write,Agent,Skill"`.

- **W (workflow):** default config. Skill `scientific-workflow` and the 5 agents visible.
  Fixture W = `git archive HEAD` + the working-tree `AGENTS.md` (delegation pointer) +
  `docs/agent_guidance/delegation.md`.
- **B (baseline):** `--settings '{"skillOverrides":{"scientific-workflow":"off"}}'` and
  `--disallowedTools "Agent(scientific_explorer),...,Agent(scientific_reviewer)"`. Built-in
  agents stay available. Fixture B = `git archive HEAD` (no delegation pointer).
  Probe result: skill list empty, a call to `scientific_explorer` is denied by rule.
  The agent descriptions still appear in B's agent list, so B pays that listing cost too.

Each run uses a fresh copy of its fixture. W and B for the same task and repeat run
concurrently. Prompts are identical in both arms and never name an agent or the skill.

## Tasks (prompts verbatim)

**T1, quick fact (overhead control).**
"What are the default values of --trap-stiffness and --max-force in
scripts/run_design_controller.py? Answer in one line in the form:
trap-stiffness=<value>, max-force=<value>"
Truth: 0.7 and 20.0. Correct = both values appear and no other number is given for them.

**T2, mechanical bulk extraction.**
"List every Python file under scripts/ (recursive) that defines a module-level function
named main. For each file give the first line of its module docstring, or the word none
if it has no docstring. Reply with one line per file in the form
`<path relative to the working directory> | <first docstring line>`, sorted by path, and
nothing else."
Truth: `truth_t2.py` run on the fixture (161 files; erratum: an earlier draft said 164,
which counted three untracked working-tree scripts; corrected before any scored run).
Correct = path set exact and at least 95% of docstring lines exact after whitespace
normalization.

**T3, long constrained audit with a pre-launch framing.**
"I will use your answer to decide whether a full MD campaign can start, so treat this as
a pre-launch check. Audit whether the CLI defaults in scripts/run_design_controller.py
match the defaults of the ControllerConfig fields in origami_folding/controller.py. For
every CLI option that feeds a ControllerConfig field directly, report the option, the CLI
default, the config default, and whether they match. Treat fields that are computed from
other arguments separately, and say what each resolves to when the option is omitted.
Write the full table to audit.md in the working directory. Do not create or edit any
other file, and do not run anything that takes longer than a minute. In your reply, give a
short summary, say explicitly what you did not verify, and end with one line in the form
`MISMATCHES: --option-one, --option-two` listing the CLI options whose defaults do not
match (or `MISMATCHES: none`)."
Truth: `truth_t3.py`: 36 direct options, 5 true mismatches (`--final-hold-steps`,
`--max-events`, `--max-retries`, `--relax-max-chunks`, `--trap-steps`), 6 indirect fields.
Correct = recall 5/5 and precision 100% on the `MISMATCHES:` line, at least 90% of the 36
direct options present in `audit.md`, and the file manifest shows only `audit.md` added.
Also recorded, not part of Correct: indirect-field coverage (of 6), and whether the reply
states an explicit "not verified" disclosure.

## Metrics (from the run's result event and stream)

- Cost in USD at list price (`total_cost_usd`; includes sub-agents), and tokens per model:
  uncached input + cache write, cache read, output.
- Turns, wall time, peak main-thread context, delegations (Agent calls by type), skill
  loads, reviewer calls.
- Correctness by the scorers above. A run that ends in an error (including the budget
  cap) is scored incorrect, with its cost counted.

## Repeats and caps

T1 n=3, T2 n=3, T3 n=2 per arm (16 runs). `--max-budget-usd`: T1 0.8, T2 1.5, T3 3.0 per run.
Timeout 25 min per run. No repeat is added after seeing results.

## Pre-registered decisions

A cost difference counts as real only if the [min, max] cost ranges of the two arms do
not overlap. Otherwise: "no detectable difference at this n". Ratio = median W / median B.

- **D1, overhead on a small task (T1):** pass if W makes no delegation and loads no
  skill in any run, and the ratio is at most 1.15 or the ranges overlap.
- **D2, overhead on a mechanical task (T2):** pass if W is correct whenever B is correct,
  and the ratio is at most 1.15 or the ranges overlap. If W delegates and costs more with
  non-overlapping ranges, D2 fails.
- **D3, on-track (T3):** pass if W is correct in at least as many runs as B and the ratio
  is at most 1.5. Reported separately: whether W is correct in more runs than B
  ("on-track advantage"), and whether W is cheaper with non-overlapping ranges
  ("token saving").

Verdict lines to report: Overhead (D1, D2), Token saving (T3), On-track advantage (T3).
Each is pass, fail or inconclusive. A failed criterion is the result; it is not
re-defined after the runs.

## Limits stated before running

Small n, so only large effects are visible. One repository, one main model, headless mode
(no interactive approvals). Cost is a list-price estimate. The scorers check
correctness, not the quality of explanations. The reviewer's value on a defect that
neither arm made cannot show up here.
