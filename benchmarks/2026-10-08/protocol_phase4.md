# Benchmark phase 4 protocol (frozen 2026-10-08, before any phase 4 run)

## Question

Is the workflow cheaper than using Opus alone (an Opus main thread, no workflow), on
the same small tasks? Phases 1 to 3 used Sonnet as the main model in every arm, so
"Opus alone" has not been measured.

## New arm

- **O (Opus alone):** plain Claude Code with `--model opus` as the main model, effort from
  `settings.json` (Opus 5.5: high), skill off, the five `scientific_*` agents denied,
  built-in agents on. Prompts, permissions, fixtures and scorers as for arm B.

## Tasks and comparators

n=3 per task for arm O. The comparator arms come from phases 1 to 3 (same day, same
code and harness, not re-run). Cost is list price, so it does not drift between runs.

| Task | Arm O compared with |
| --- | --- |
| T1 quick fact | W (workflow installed, not named), B (Sonnet alone) |
| T2 extraction | W, B |
| T3b audit, corrected truth | X (skill invoked), B |
| T5v3 pre-launch review, corrected truth | R (review routed to `scientific_reviewer`), B |

Caps (`--max-budget-usd` per run): T1 1.5, T2 3.0, T3b 4.0, T5v3 4.0. Timeout 25 min.
No repeat is added after seeing results.

## Pre-registered decisions

For each task, compare the median cost of the workflow arm with arm O. A difference is
real only if the [min, max] cost ranges do not overlap.

- **G1, cost:** "workflow cheaper than Opus alone" if its median is lower and the ranges
  do not overlap. "Opus alone cheaper" if the reverse. Otherwise "no detectable difference".
  Reported per task, not pooled.
- **G2, quality:** correct runs per arm, as scored by the phase 1 to 3 scorers. A difference
  of 1 run is not evidence.
- Reported but not decided: the cost of O relative to B (the price of using Opus as the
  main model), and cost per correct run.

## Limits stated before running

n=3 for O and the comparator cells are n=2 to 5. One repository, headless mode. The
comparators were run earlier the same day, not interleaved with O. Task sizes are small
(under $0.4 for Sonnet), which is the regime the question asks about.
