# Benchmark phase 3 protocol (frozen 2026-10-08, before any phase 3 run)

## Why phase 3

Phase 2 T5 had a second ground-truth error of mine. Planted defect B (the removed
`adaptive_coupled_release` CLI guard) is not a blocking defect: `ControllerConfig.__post_init__`
(`origami_folding/controller.py` lines 222-223) enforces the same rule, so only the time of
the error changes. All six phase 2 runs rated it minor, which was correct. The registered
phase 2 T5 result (0/3 vs 0/3) is vacuous and stands as scored.

Phase 2 also showed that with the skill loaded, the main thread reviewed the change set
itself and never called `scientific_reviewer` (0 delegations in 12 runs). So the value of
routing a review to the reviewer role has not been tested. Phase 3 tests it, with a
truth fixed before any run and fresh runs only (no phase 2 data is reused).

## Question

When the user routes a pre-launch review to `scientific_reviewer` (active specifying),
does the review find more of the real defects than the main model reviewing alone, and at
what cost?

## Arms

- **R (reviewer-routed):** workflow config. Prompt starts with: "Use the
  scientific-workflow skill. Have the scientific_reviewer agent review the change set.
  Then give me the result in the format below. "
- **B (baseline):** as before (skill off, five agents denied, built-in agents on). Plain prompt.

Same model, permissions and caps as before.

## Task T5v3

Fixture: the phase 2 `R_W` / `R_B` fixtures (unchanged). Prompt: the phase 2 T5 prompt with
its last sentence replaced by: "Do not modify any tracked file; you may write scratch files
named review_*.patch or review_*.md in the working directory." (The reviewer has no shell,
so the diff has to be written to a file for it.)

Corrected truth:
- Real defect A: `ControllerConfig.nucleation_fraction` default 0.5 changed to 0.35 (CLI
  unaffected; other callers change; no test pins it).
- Real defect C: `ControllerConfig.reopen_max_attempts` default 2 changed to 5, which breaks
  two existing tests, and the default-value assertion loosened to hide it (the test
  `test_default_config_leaves_reopen_off` is the other half of the same defect).
- Not a blocking defect: the removed CLI guard (B). A finding about it is neutral at any
  severity: it is neither required nor a false positive.
- Decoys (harmless): reworded error message and reworded help text.

Scoring (token match on file, symbol and why text, lowercase):
- A found = a blocking finding containing `nucleation_fraction`.
- C found = a blocking finding containing `reopen_max_attempts` or
  `test_default_config_leaves_reopen_off`.
- Neutral tokens (not false positives when blocking): `adaptive_coupled_release`,
  `adaptive coupled release`, `adaptive-coupled-release`.
- False positive = any other blocking finding.
- Correct = A and C found, no false positive, a parsable `FINDINGS:` line, and no change to
  any file except new files named `review_*.patch` or `review_*.md`.
- Also recorded: minor-only detection of A or C ("seen but under-rated").

## Repeats and caps

n=5 per arm (10 runs). `--max-budget-usd` 3.0 per run. 25 min timeout. No repeat is added
after seeing results.

## Pre-registered decisions

- **F1, engagement:** pass if `scientific_reviewer` is called in at least 4 of 5 R runs
  and the transcript shows an Opus model (or the model the run reports for the reviewer).
- **F2, quality:** "advantage" if R is correct in at least 2 more runs than B. If the
  difference is 0 or 1 run, the result is "no detectable difference".
- **F3, cost:** pass if the median cost ratio R/B is at most 2.0. Also report cost per
  correct run.
- A failed criterion is the result. Nothing is re-defined after the runs.

## Limits stated before running

n=5 per arm, so only a large effect shows; a one-run difference is not evidence. One
repository, one change set, defects seeded by me, headless mode, main model Sonnet. Token
match scoring does not read the explanations. The defect truth was fixed after seeing phase
2 outputs, so phase 2 data cannot confirm it; only the fresh phase 3 runs count.
