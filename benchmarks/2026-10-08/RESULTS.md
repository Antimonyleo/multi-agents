# Benchmark results: scientific-workflow, 2026-10-08

50 scored headless runs in four phases (list-price cost about $18.1 in total), Claude Code
2.1.294, main model Sonnet 5.5. Protocols were frozen before each phase
(`protocol.md`, `protocol_phase2.md`, `protocol_phase3.md`, `protocol_phase4.md`). Per-run data is in `data/`;
the harness is `bench.py`. Registered outcomes are reported as scored.

## Verdict

| Goal | Result |
| --- | --- |
| No overhead when the workflow stays out of the way | **Pass.** Cost ratio W/B 1.06 (T1) and 0.97 (T2); cost ranges overlap. About +800 tokens of main-thread context from the always-present skill and agent descriptions. |
| No large overhead when the skill is invoked | **Pass.** X/B 1.05 (T3b) and 1.08 (T5). Skill load adds 2 to 5 turns. |
| Saves tokens | **Not shown.** No comparison favored the workflow. All cost ranges overlapped, and routing a review to the reviewer cost much more (below). |
| Delegates by itself when useful | **Never happened.** 0 delegations in the 14 workflow runs that did not name the reviewer (8 passive, 6 with the skill invoked). The tasks were small (under $0.40 for the baseline). |
| Reviewer finds more than the main model | **No detectable difference** (0/5 vs 0/5 correct; see the detail). |
| Reviewer cost | **Fail (F3).** Median R/B cost ratio 4.98 ($1.145 vs $0.230). The Opus call alone had a median of $0.85; the main-thread cost was unchanged ($0.24 vs $0.23). |
| Cheaper than Opus alone (phase 4) | **Yes, about half, but only because the main thread is Sonnet.** Workflow vs Opus alone (medians): T1 0.090 vs 0.174, T2 0.207 vs 0.417, T3b 0.336 vs 0.583 (ratios 0.52, 0.50, 0.58). Plain Sonnet gives the same saving, so the workflow adds nothing on these tasks. With the review routed to the reviewer it was dearer than Opus alone: 1.145 vs 0.503 (2.28 times). Correctness equal: 3/3 for all arms on T1, T2, T3b. |
| Keeps long or complex tasks on track | **Untested.** No task here was long. The longest baseline run was 14 turns and under $0.40. |

## Detail by phase

**Phase 1 (passive: skill and agents visible, prompts natural).** T1 (quick fact) 3/3 vs 3/3
correct, median $0.090 vs $0.086. T2 (161-file extraction) 3/3 vs 3/3, $0.207 vs $0.213.
T3 (long audit with constraints) 0/2 vs 0/2 as registered. D1 pass, D2 pass; D3 passed
only vacuously, because both arms scored 0. The W arm loaded no skill and delegated
nowhere in any of its 8 runs, so phase 1 measured passive overhead only.

**Ground-truth error in T3 (mine).** `truth_t3.py` skipped options whose value is
transformed on the way into `ControllerConfig`. `--temperatures` and `--eligibility-mode`
are real mismatches (verified in source), so there are 7 required mismatches, not 5. Post
hoc rescore: W 2/2 and B 1/2 correct. In W the workflow never loaded, so W and B behaved
the same; the gap is run-to-run variance, not an effect.

**Phase 2 (workflow invoked by the user: prompt starts "Use the scientific-workflow skill.").**
T3b 3/3 vs 3/3 correct, $0.336 vs $0.321 (X/B 1.05). T5 (seeded review) 0/3 vs 0/3, $0.223 vs
$0.207 (X/B 1.08). The skill loaded in every X run, and still no delegation: the main thread
did the review itself. E1 pass, E2 and E3 passed only vacuously.

**Second ground-truth error (mine).** Planted defect B (removed CLI guard) is not a blocking
defect, because `ControllerConfig.__post_init__` enforces the same rule. All six runs rated
it minor, correctly. Phase 2 T5 is vacuous; it was not rescored.

**Phase 3 (user routes the review to the reviewer: fresh runs, corrected truth).** n=5 per
arm. Reviewer called in 5/5 R runs, Opus in all five (F1 pass). Both arms: defect C
(`reopen_max_attempts` default plus the loosened test) found as blocking in 5/5; defect A
(`nucleation_fraction` default) seen in 5/5 but rated minor in 10/10, with the argument that
the CLI always passes its own default. Registered score: 0/5 vs 0/5 (A is required as
blocking). F2: no detectable difference. F3 fail on cost. Whether A deserves "blocking" is a
judgment call; the registered truth said yes and both arms disagreed with it.

**Phase 4 (Opus alone, plain Claude Code with `--model opus`; n=3 per task).** Opus as the main
model cost 1.8 to 2.2 times plain Sonnet on every task (T1 2.04, T2 1.96, T3b 1.82, T5v3 2.18)
with the same correctness: 3/3 on T1, T2 and T3b. On T5v3, Opus alone matched the other two arms
exactly: defect C blocking in 3/3, defect A seen in 3/3 but rated minor. So across 13 runs of
three setups (Sonnet alone, Opus alone, Sonnet with an Opus reviewer) the detection pattern is
identical. The reviewer call (median $0.85) cost more than Opus doing the whole review alone
($0.50): the reviewer reads files without a shell, thinks at high effort, and produced a median
of 21,000 output tokens against 5,800 for Opus alone. Comparator arms were run earlier the same
day, not interleaved with O.

## What this does and does not show

- On small and medium tasks the workflow is nearly free when idle and costs about 5 to 8%
  more when the skill is invoked. It does not make those tasks cheaper.
- The reviewer is expensive relative to small tasks (3 to 5 times the whole baseline task)
  and gave no extra detection on this change set. Its value on a defect that a plain
  Sonnet pass misses is not shown. This test could not show it, because Sonnet missed
  nothing that the truth required except the contested severity of A.
- The efficiency and on-track claims for long tasks remain open. Savings, if any, would
  come from isolating very large reads and from catching expensive wrong turns. Neither
  regime was tested.

## Limits

Small n; one repository; one main model; headless mode; list-price cost estimate; scorers
match tokens, not explanations; all seeded truths were written by me and two were wrong.
The Phase 3 truth was fixed after seeing phase 2 outputs (only fresh runs count).
Lesson for the next benchmark: have a fresh reviewer verify the truth before any run.

## Next experiments (not run)

1. Reviewer at medium effort (Opus 5.5 default) on the same T5v3, to see whether the cost
   falls without losing the finding of C. Cheapest; about $3.
2. A genuinely long task with an objective check (for example a multi-file change with the
   test suite as the check), n=3 per arm, about $3 to $8 per run.
3. A large-log triage task for `scientific_explorer`, the only role never invoked.
4. Any seeded-defect task: have a fresh reviewer verify the truth first.
