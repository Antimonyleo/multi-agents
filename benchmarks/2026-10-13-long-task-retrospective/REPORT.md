# Long-task retrospective, Step 1: where tokens and time went

Offline, read-only, no model calls. The selection rule and measures were fixed in
[PLAN.md](PLAN.md) before extraction. Outcome quality is not measured yet; it
comes from the user's labels in [labels.csv](labels.csv) (see [LABELING.md](LABELING.md)).

## Main results

1. **In real long sessions most tokens went to helpers, unlike in the small benchmarks.**
   Helpers took 82% of Claude tokens processed and 58% of Codex tokens. Of new
   tokens (uncached input plus output) they took 66% for Claude and 72% for Codex.
   The benchmarks almost never delegated.
2. **Helpers seldom used smaller models.** For Claude, 238 of 283 helper
   sessions ran on Opus, 44 on Sonnet and 1 on Haiku. Opus produced 84% of
   helper new tokens. For Codex, Luna helpers carried 14% of the
   price-ratio-weighted family total (assumed ratios, below).
3. **Re-reading a large context, not writing, is the main cost of a long session.**
   Under assumed price ratios, cached input was 74% of the weighted Claude total
   and 64% of the Codex total. Claude parents ran at a mean of 205k to 477k
   tokens of context per call, peaking at 965k. Codex compacted 443 times in
   536 active hours and peaked at 240k.
4. **Busy-waiting helpers were the largest single waste found.** In Claude
   sessions, 11,164 helper responses (35% of 31,844) contained only polling:
   `date`, `sleep`, short `echo` ticks, or re-reading the same file. Each one
   re-read hundreds of thousands of tokens of context. That is 54% of helper
   tokens processed and, weighted, 34% of all Claude usage in the sample. It is
   concentrated: four Opus helpers in one session (`1ef22ddd`, 2026-09-12)
   account for most of it, for example 3,288 `date` calls and 2,494 `sleep`
   calls.
5. **Codex spent many parent calls on coordination.** There were 21,514
   orchestration calls against 67,587 parent model calls (one model call can
   contain several tool calls, so this is a ceiling on their share): 7,908
   `wait_agent`, 5,032 `send_message`, 3,722 `followup_task`, 2,087 `wait`, 1,731
   `list_agents`, 718 `spawn_agent` and 316 `interrupt_agent`. Each helper start
   carried about 54k tokens of context (median of the first 10 calls; 59k when
   forked). Guardian auto-reviews (413 sessions, 351 with usage) were 4% of the
   weighted Codex total.
6. **The main drift was stalling, not wandering.** In 19 of 27 sessions the user
   had to say "no need to stop or pause, continue" or similar (40 prompts).
   Fifteen prompts asked the agent not to overengineer or be "too defensive".
   Status questions (71, noisy match) show the user often had to ask where
   things stood. Clear disagreement with a result was rare (8 prompts).

## What this means for the workflow (inferred)

- The current skill's rules already target items 4 and 5. They say one
  progress owner, native completion instead of reasoning loops, deterministic
  watchdogs and no status-only assignments. Nearly all sampled sessions predate
  that skill (2026-10-08/09). Whether the rules fix the problem is untested. The
  three sessions from 2026-10-09 or later are too few to say.
- Waiting on a job is the expensive part of a long task. The fix is mechanical:
  the parent waits through native notifications or a script, and a waiting
  helper ends its turn instead of polling. Using a cheaper model does not fix a
  400k-token context polled 3,000 times.
- The stalling pattern pulls against the workflow's pause, authority and review
  gates. A rule that makes agents stop more often could add to it. Explicit
  "continue until X" authority at the start of a long task may matter more than
  routing.
- Helper value is still unknown. Helpers did most of the work, so the question
  is whether that work was accepted. The user's labels are needed to judge it.

## Measured, by session

Numbers are in [aggregates.json](aggregates.json), [signals.json](signals.json),
[polling.json](polling.json) and [summary.json](summary.json); the session table is
printed by `analyze.py`.

| | Claude | Codex |
|---|---:|---:|
| Long sessions (parents) | 7 | 20 |
| Helper or guardian sessions | 283 | 1,149 (736 spawned, 413 guardian) |
| Active hours (gaps capped at 10 min) | 179.9 | 536.1 |
| User prompts | 322 | 505 |
| Compactions | 13 | 443 |
| Tokens processed | 10.35G | 18.68G |
| Helper share, processed / new tokens | 82% / 66% | 58% / 72% |
| Cached share of input | 98% | 97% |
| Automated wake-ups of the parent | 557 (monitor and agent notifications) | not counted |

Sessions span 2026-08-31 to 2026-10-10 in `sequence_design`,
`origamifolder7` (including kinetic) and `AI/codex_direc`.

## Limits

- **Observational.** Tasks, models and dates differ, so nothing here is causal or a savings estimate.
- **Assumed price ratios.** Relative to new input: Claude cache read 0.1×,
  cache write 1.25×, output 5× (Anthropic's published ratios); Codex cached
  input 0.1×, output 8× (assumed). Neither is verified for these model
  versions, and plan-based usage limits may not follow list prices. Token
  counts are exact; the weights are not.
- **Codex token totals** come from each session's last cumulative counter and
  may omit compaction calls.
- **Polling** is matched by command shape. It undercounts polling inside
  longer commands and does not prove a whole response was avoidable.
- **Redo after a helper** could not be measured. After 271 of 275 Claude
  helpers (98.5%) the parent touched at least one of the helper's files within 30 calls, but
  that includes reading the helper's outputs and shared plan files. Codex
  helper messages are encrypted.
- **Prompt categories** are regex matches. Spot checks found "continue" and
  "overengineering" mostly genuine; status, repeat and disagreement matches
  are noisy.
- **Live sessions** were frozen at their byte length on 2026-10-13.

## Next

Step 2: the user fills in `labels.csv`. Then compare the labels with stalling,
polling, compaction, helper share and orchestration counts. With 27 sessions
any pattern is a lead to check, not a conclusion. If the polling rule is the
leading candidate, check it on the next real long task by counting polling
responses. That needs no paid benchmark.
