# Benchmark phase 2 protocol (frozen 2026-10-08, before any phase 2 run)

## Why phase 2

Phase 1 (`protocol.md`) found that in all 8 W runs the workflow never engaged: no skill
load, no delegation, even on T3 with its "pre-launch check" framing. Phase 1 therefore
measured only the passive overhead. It said nothing about whether the workflow, when it
does engage, saves tokens or keeps work on track. Phase 2 tests the engaged workflow.

Phase 1 also had a ground-truth defect, found after the runs. `truth_t3.py` skipped any
option whose value is transformed on its way into `ControllerConfig`. Two of those are
real mismatches (`--temperatures`: CLI `70,60,50,40,30` vs config `(80,70,60,50,40)`;
`--eligibility-mode`: CLI `effective-molarity` vs config `free_energy`). So phase 1 T3
has 7 true mismatches, not 5. The registered phase 1 result (0/4 correct) stands as
scored. A rescore against the corrected truth is reported as post hoc.

## Arms

- **X (engaged workflow):** same config as W, and the prompt starts with
  "Use the scientific-workflow skill. " (the user actively invokes it).
- **B (baseline):** as in phase 1 (skill off, five agents denied, built-in agents on).

Same model (`--model sonnet`), same permissions and caps as phase 1.

## Tasks

**T3b:** the T3 prompt verbatim (with the X prefix for arm X). Corrected truth v2:
required `MISMATCHES` set = the 5 original + `--temperatures` + `--eligibility-mode`.
`--trap-release-steps` is optional (its default `None` resolves to `--relax-steps` = 10000
against a config default of 2000, so listing it is acceptable). Any other option listed is
a false positive. Correct = all 7 required, no false positive, at least 90% of the 36
direct options in `audit.md`, and only `audit.md` added.

**T5, pre-launch review of a seeded change set (new).** Fixture = HEAD code with a
local git repo; a baseline commit, then uncommitted edits:
- Defect A: `ControllerConfig.nucleation_fraction` default 0.5 changed to 0.35 (the CLI
  default stays 0.5, so only direct callers change).
- Defect B: the guard `if args.adaptive_coupled_release and trap_release_steps == 0:
  raise ...` removed from `run_design_controller.py` (no test covers it).
- Defect C: `ControllerConfig.reopen_max_attempts` default 2 changed to 5, and the test
  assertion `assertEqual(..., 2)` in `test_controller_reopen.py` loosened to
  `assertGreaterEqual(..., 1)`.
- Decoys (harmless): a `ValueError` message reworded; a CLI help string reworded.

Prompt: "I made the uncommitted changes shown by `git diff` in this repository. We will
start a full MD campaign from this code next. Review the change set before launch. Reply
with a short summary, then end with one line starting with `FINDINGS:` followed by a JSON
array in which each item is {"file": ..., "symbol": ..., "severity": "blocking" or
"minor", "why": ...}. Mark as blocking only issues that should stop the launch and that
you can support from the code. Do not modify any file."
Correct = each of A, B, C matched by a blocking finding whose file, symbol or why text
contains its token (`nucleation_fraction`; `adaptive_coupled_release` / `adaptive coupled
release`; `reopen_max_attempts`), zero blocking findings that match none of A, B, C
(decoys flagged as blocking count as false positives), a parsable `FINDINGS:` line, and no
file changed.

## Repeats and caps

T3b n=3 and T5 n=3 per arm (12 runs). `--max-budget-usd` 3.0 per run. 25 min timeout.
No repeat is added after seeing results.

## Pre-registered decisions

- **E1, cost of the engaged workflow:** pass if the median cost ratio X/B is at most 1.5
  on each of T3b and T5.
- **E2, on-track on T5:** pass if X is correct in at least as many runs as B.
  "Quality advantage" if X is correct in more runs than B by at least 2 of 3.
- **E3, on-track on T3b:** pass if X is correct in at least as many runs as B.
- **Token saving:** reported as yes only if X is cheaper with non-overlapping cost ranges
  and no worse correctness. Otherwise no or inconclusive.
- Engagement is reported for every run: skill loads, delegations by type, reviewer calls.
  If X does not engage (no skill load) in a run, that run is counted as a failed
  engagement, and reported separately.

## Limits stated before running

n=3 per cell, so only large effects show. A one-run difference is not evidence. One
repository, one main model, headless mode. The T5 defects are seeded by me, so they
test one kind of defect (silent default changes, a removed guard, a weakened test).
The scorers check findings by token match, not by reading the explanation.
