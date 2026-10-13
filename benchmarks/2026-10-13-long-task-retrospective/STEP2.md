# Long-task retrospective, Step 2: outcome labels and comparisons

Agent-labelled, per [PLAN.md](PLAN.md) Amendment 2. The method and
[compare.py](compare.py) were committed (`c61e14b`) before any label existed.
The session-length check below was added after the labels were seen, so it is
post-hoc. No user labels yet: `stop_wanted` and `worth_cost` are blank, so
those comparisons did not run.

## Result

**No workflow signal separates good from bad outcomes once session length is
considered.** The pre-registered comparisons show worse Codex outcomes with
more reactive stops, more wait-only calls and more orchestration. But a session
that runs long is itself a sign the task went badly, and length tracks outcome
more strongly than any signal does. The data cannot tell whether these signals
cause bad outcomes or just come with long, hard tasks.

- **Claude:** all 7 sessions were labelled `partial`, so outcome cannot be
  compared. Helpers were used in all 5 sessions that had them.
- **Codex (19 sessions with an outcome):**

| Signal (per session) | achieved (n=5) | partial (n=11) | failed (n=3) | Spearman with outcome |
|---|---:|---:|---:|---:|
| Reactive stop prompts per prompt (coder 1) | 0 | 0.028 | 0.083 | −0.59 |
| Wait-only share of parent calls | 0.034 | 0.193 | 0.226 | −0.47 |
| Orchestration calls per active hour | 7.8 | 28.4 | 51.6 | −0.32 |
| Helper share of new tokens | 0.45 | 0.69 | 0.75 | −0.27 |
| Compactions per active hour | 1.21 | 0.72 | 0.91 | +0.37 |
| **Active hours (post-hoc)** | **1.65** | **30.4** | **67.5** | **−0.67** |

Values are medians. Spearman uses the outcome rank (failed < partial <
achieved); negative means more of the signal goes with worse outcomes.

**Post-hoc, sessions with at least 10 active hours** (n=14: 1 achieved, 10
partial, 2 failed):

- The two failed sessions still had more reactive stops: 0.088 per prompt,
  against 0.024 for partial.
- They had more wait-only calls: 0.256 of parent calls, against 0.207.
- They made more orchestration calls: 63 per hour, against 25.
- With two failed sessions, this is only a lead.

## Other label results

- **Helpers:** labelled useful in 19 of 20 Codex sessions (14 `yes`, 5
  `some`, 1 `unsure`) and in all 5 Claude sessions that had them. Helper output
  was usually built on. Whether it was worth its cost is not answered, because
  that needs `worth_cost`.
- **Direction:** `on_track` was `some` in 12 of 20 Codex sessions and 2 of 7
  Claude sessions. No session was labelled `no`.
- **Rework:** `rework` was `some` or `major` in 24 of 27 sessions. It was
  `major` in 3 (`01a08f31`, `01a0efc4`, `ac23eed6`).

## Label quality

- **Agreement.** The two Sonnet labellers agreed exactly on outcome in 21 of
  27 sessions, and on each other label in 23 of 27. An Opus reviewer settled
  the 18 differing labels in 13 sessions, citing evidence
  ([agent-labels.csv](agent-labels.csv), [labelers/](labelers/)).
- **Weakest evidence.** The labellers reported the least evidence for the
  following:
  - Codex helper use, because helper task texts are not available.
  - Rework in sessions with sparse Git history.
  - The four sessions still running at freeze. `01a1248e` was adjudicated
    `unsure`.
- **Blinding is partial.** The agent's own reports show where it stopped, and
  labellers could see the user redirect it.
- **Agent labels are proxies.** They judge the objective as stated in the
  prompts, not what the user privately valued.

## What this means for the workflow (inferred)

- **No support yet for a broad rule change.** The signals are confounded with
  task length and difficulty.
- **Two leads survive among long sessions.** Agents stopping mid-work, and
  parents spending calls only to wait, both go with failed outcomes. Both are
  cheap to watch on the next real long task:
  - count reactive "do not stop" prompts and wait-only calls;
  - record whether each stop was wanted.
- **Helpers were mostly used, not wasted.** The open question is cost, not
  usefulness.

## Not done

- `stop_wanted` and `worth_cost` need the user. They are optional, and the
  comparisons fill in if the user adds them to `labels.csv`.
- No adjustment for project or task type. With 19 sessions, stratifying would
  leave groups of 1 to 5.
