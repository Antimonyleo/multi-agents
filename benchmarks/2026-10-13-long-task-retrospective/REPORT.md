# Long-task retrospective, Step 1: where tokens and time went (revision 2)

Offline, read-only, no model calls. The sample and first measures were fixed in
[PLAN.md](PLAN.md) before extraction. Polling, price weighting, prompt
categories, wait measures and the without-`1ef22ddd` results were added later;
they are exploratory (PLAN.md, Amendment 1). Outcome quality is not measured
yet; it comes from the user's labels in [labels.csv](labels.csv) (see
[LABELING.md](LABELING.md)).

Revision 2 follows an independent review on 2026-10-13: a methods reviewer, a
recomputation from independent code, and a code review. The recomputation
reproduced every first-report number to within one response. The code review
found seven bugs, now fixed. Changes are listed under
[Corrections](#corrections-from-revision-1).

## Main results

1. **Helpers did most of the work in real long sessions.** Helpers took 82% of
   Claude tokens processed and 61% of Codex tokens. Of new tokens (uncached
   input plus output) they took 66% and 73%. One Claude session (`1ef22ddd`)
   inflates the Claude figures. Without it, the shares are 63% of tokens
   processed and 59% of new tokens. The per-session median is 83% of tokens
   processed (range 29–95%, 5 sessions with helpers).
2. **Helpers seldom used smaller models.**
   - Claude: 238 of 283 helper sessions ran mainly on Opus, 44 on Sonnet and 1
     on Haiku. Opus produced 84% of helper new tokens.
   - Codex: helpers whose main model was Luna carried 17% of the weighted
     family total (assumed price ratios, below).
3. **Under assumed price ratios, re-reading context is the largest cost.**
   Cached input was 74% of the weighted Claude total and 64% of the Codex
   total. This depends on the assumed cache-read ratio: across 0.05× to 0.25×,
   it ranges from 59% to 88% (Claude) and from 47% to 82% (Codex). Mean context
   per call, per session, had a median of 303k tokens (range 205k–477k) for
   Claude and 123k (range 99k–134k) for Codex. Codex compacted 443 times in 536
   active hours (per-session median 0.79 per hour).
4. **Claude busy-waiting happened at scale in one session; it is not a general
   pattern in this sample.**
   - 11,181 of 31,844 Claude helper responses (35%) contained only
     polling-shaped calls: `date`, `sleep`, short `echo` ticks, or a sixth or
     later Read of an unchanged file. They were 54% of helper tokens processed
     and, weighted, 34% of all Claude usage.
   - Session `1ef22ddd` (2026-09-12) holds 10,548 of them (94%). Five
     helpers carry most of it. One ran 3,308 `date` calls in 3,416 responses.
   - Without that session, polling is 635 of 13,685 helper responses and 4% of
     weighted Claude usage.
   - That session alone is 53% of weighted Claude usage. Spot checks (10 random
     responses, by the recomputation reviewer) were all genuine waiting.
5. **Codex parents often spent a model call just to wait.**
   - 13,347 of 61,687 parent model calls (22%) contained only wait calls, and
     they carried 22% of parent input tokens.
   - Of those, 7,908 were `wait_agent`, which is the native completion wait the
     skill prescribes. 6,857 of all 7,908 `wait_agent` calls had a timeout of
     60 s or less, so each short wait re-read the full context (about 120k tokens per call).
   - Parents also made 19,427 orchestration calls, and helpers made another
     15,386. A fresh helper started with a median context of 55k tokens; a
     forked one with 59k.
6. **The agent often stopped before the work was done.** Two coders (the
   report author and a blind subagent) coded every regex match:
   - **Stopped mid-work:** in 12 to 14 of 27 sessions, the user had to say
     "do not stop" or "continue" after the agent stopped part-way through
     assigned work (17 or 18 prompts).
   - **Authority given up front:** 7 or 8 sessions got no-stop authority up
     front. In 1 or 2 of those, the agent still stopped mid-work later, for
     example "i am said many times … DO NOT STOP".
   - **Overengineering:** all 15 overengineering matches (10 sessions) are
     genuine. Most are advance instructions (8 or 10) or questions (3 or 4).
     Only 1 to 4 complain about work already seen.
   - **Drift and disagreement:** drift was raised in 3 or 4 sessions. In two
     sessions the agent itself said it had drifted ("I drifted from the main
     goal", "much of the later work went off track"). Clear disagreement
     appears in 3 or 4 prompts.
   - The regexes miss some cases, so these counts are lower bounds. Status and
     repeat matches were not coded and are not used.

## What this means for the workflow (inferred, not tested)

- **Context per call times the number of calls is the cost lever, not model
  choice alone.** Most helper work ran on large models with large contexts.
- **Waiting is a measurable lever in Codex.** About a fifth of Codex parent
  calls only waited, mostly with timeouts of 60 s or less.
  [coordination.md](../../skill/scientific-workflow/references/coordination.md)
  allows bounded waits "up to 60 seconds per wait for user responsiveness", so
  this pattern would comply with the current rule. Whether longer native waits
  would cut cost without hurting responsiveness is untested.
- **The Claude polling rule addresses a real but rare failure.** It cost a lot
  once and was near-absent in the other six Claude sessions.
- **Stopping early is the main steering problem the user reported.** Up-front
  authority did not always prevent it. Pause and review gates could add to
  it. Whether the stops were wanted is unknown, so the `stop_wanted` label is
  needed before changing a rule.
- **Timing caveat.** The current wait and ownership rules were added on
  2026-10-08/09. Only three sessions (`bf134f2c`, `01a121d6`, `01a1248e`)
  started on or after 2026-10-09. `01a113d6` (2026-10-07) used an earlier
  version of the skill.
- **Helper value is unknown.** The planned redo measure found no parent
  re-reads, but it sees only `Read` calls. The `helpers_useful` label is
  needed.

## Measured totals

Numbers are in [aggregates.json](aggregates.json), [signals.json](signals.json),
[polling.json](polling.json), [weighted.json](weighted.json) and
[summary.json](summary.json). Logs show each script's printed output.

| | Claude | Codex |
|---|---:|---:|
| Long sessions (parents) | 7 | 20 |
| Helper or guardian sessions | 283 | 1,149 (736 spawned, 413 guardian) |
| Active hours (gaps capped at 10 min) | 179.9 | 536.1 |
| User prompts (automated turns excluded) | 318 | 498 |
| Parent model calls | 5,055 | 61,687 |
| Compactions | 13 | 443 |
| Tokens processed | 10.35G | 19.91G |
| Helper share, processed / new tokens | 82% / 66% | 61% / 73% |
| Cached share of input | 98% | 97% |
| Parent orchestration calls (helpers' own) | — | 19,427 (15,386) |
| Exec waits (`wait`, `sleep`) | — | 3,708 |
| Automated wake-ups of the parent | 561 | not counted |
| Tool errors | 100 | not measured |
| User interrupts | 1 | 19 |
| Correction-regex prompts (uncoded) | 3 | 13 |
| Repeated identical commands, no edit between | 23 | 4,110 (3,633 contain an inspection or wait word) |
| Unchanged rereads / rereads after compaction (parents) | 0 / 1 | not measured |
| Live at freeze | 3 | 1 |

Redo after a helper (Claude, planned measure):

- 210 of 283 helper returns could be located: 92 helpers ran in the background
  and 6 were launched by another helper.
- 112 of the located helpers had read files.
- In 0 of those 112 did the parent `Read` one of the same files within 30
  calls of the return.

## Corrections from revision 1

| Item | Revision 1 | Revision 2 | Cause |
|---|---|---|---|
| Codex tokens processed | 18.68G | 19.91G | cumulative counter reset in 105 files; segments now summed |
| Codex helper share, processed / new | 58% / 72% | 61% / 73% | same |
| Codex parent model calls | 67,587 | 61,687 | repeated token events counted as calls |
| Codex orchestration calls | 21,514 | 19,427 | `wait` (2,087) is an exec-cell wait, not agent orchestration |
| Luna share of weighted Codex | 14% | 17% | token fix and helper model taken as main model |
| Claude polling responses | 11,164 | 11,181 | Read count resets after an edit; chained and fractional sleeps matched |
| Polling, "largest single waste" | general claim | one session (94%); 4% elsewhere | scope |
| "Had to say continue": 40 prompts, 19 sessions | regex count | 17–18 reactive prompts in 12–14 sessions | hand-coded by two coders |
| "Stalling, not wandering" | stated | removed; drift was not measured, and occurred | overclaim |
| Disagreement "rare (8)" | regex count | 3–4 genuine, recall unknown | hand-coded |
| Up-front "continue until X" authority as the fix | proposed | did not prevent later stops in 1–2 of 7–8 sessions | evidence |
| Redo after helper | "not measurable" (271 of 275 overlap) | planned measure: 0 of 112 | window now opens at return; basename overlap measure dropped |
| User prompts | 322 / 505 | 318 / 498 | `/compact` and Codex injected context filtered |
| Weighted figures | inline, no script | `weighted.py` | reproducibility |
| `labels.csv` | could be overwritten by a rerun | written only while empty | reproducibility |

## Limits

- **Observational.** Tasks, models and dates differ, so nothing here is causal
  or a savings estimate.
- **Assumed price ratios.** Relative to new input: Claude cache read 0.1×,
  cache write 1.25×, output 5× (Anthropic's published ratios); Codex cached
  input 0.1×, output 8× (assumed). Neither is verified for these model
  versions, and plan-based usage limits may not follow list prices. Token
  counts are exact; the weights are not.
- **Concentration.** One Claude session is 53% of weighted Claude usage. Claude
  results are shown with and without it where it matters.
- **Codex tokens** may still omit compaction calls.
- **Polling** is matched by call shape. It misses polling inside longer
  commands, and Codex polling inside `exec` wrappers is not detected.
- **Codex wait-only calls** count `wait_agent` and `list_agents`, which can be
  legitimate progress checks.
- **Prompt codes** come from one author-coder and one blind subagent coder.
  Exact agreement was 32 of 40 for the broad continue matches. The coders
  agreed on genuine versus not for 36 of 40. Most disagreements fall on the
  boundary between "stopped mid-work" and "up front". Regex recall is unknown.
- **Redo** sees only exact-path `Read` calls by the parent. Codex helper
  messages are encrypted.
- **Live sessions** were frozen at their byte length on 2026-10-13. Four were
  still active.

## Next

Step 2 is done with agent labels: see [STEP2.md](STEP2.md). Session length
explains outcome better than any workflow signal; two leads remain among long
sessions. The user may still add `stop_wanted` and `worth_cost` in
`labels.csv`.

Two cheap checks need no paid benchmark:

1. On the next real long task, count wait-only calls and their timeouts.
2. Ask whether early stops were wanted.
