# Step 2: labelling outcomes

Only you know whether a long session got you what you wanted. The scripts
measure tokens and activity; your labels say which sessions were worth them.
The comparisons are fixed in advance in [PLAN.md](PLAN.md) (Amendment 1).

## How to fill in `labels.csv`

Each row is one long session. The sheet shows its project, start date, active
hours, number of prompts and helpers, your first and last requests and your
three longest requests. Judge from memory and these clues; do not reread
transcripts. Spend about 30 seconds per row. `unsure` is a valid answer and is
better than a guess.

| Column | Question | Values |
|---|---|---|
| `outcome` | Judged now, with hindsight: did the session deliver what you wanted from it? | `achieved`, `partial`, `failed`, `abandoned`, `unsure` |
| `on_track` | Did the work go in the direction you meant (whatever its speed)? | `yes`, `some` (it wandered at times), `no` (you had to restart or rescue it), `unsure` |
| `rework` | Did you or a later session have to redo or fix its work? | `none`, `some`, `major`, `unsure` |
| `worth_cost` | For what you got, were the time and usage reasonable? | `yes`, `no`, `unsure` |
| `stop_wanted` | When the agent stopped or asked before finishing, did you want those stops? | `yes`, `some`, `no` (it stopped when it should have continued), `none` (it did not stop early), `unsure` |
| `helpers_useful` | Did the helpers' results get used? | `yes`, `some`, `no`, `none` (no helpers), `unsure` |
| `notes` | Optional, one line: what went wrong or right | free text, e.g. "result later found wrong", "paused by me" |

Rules of thumb:

- Hindsight counts. A result that looked done but was later found wrong is
  `failed` or `partial`, with `rework` set.
- A session you paused on purpose is `abandoned` only if the work was lost.
  If it stopped at a clean checkpoint, judge the part it finished.
- Judge the session's main objective, not every small request.
- Rows with `live_at_freeze = yes` were still running when the sample was
  frozen. Judge them as of now, or use `unsure`.
- `on_track` is about direction. Stopping too often belongs in `stop_wanted`,
  not in `on_track`.
- If a session mixed several unrelated tasks, use `notes` to say which one you
  judged.

If a spreadsheet is inconvenient, reply with one line per session in column
order, for example `01a0591d partial some some no no yes`.

With 7 Claude and 20 Codex sessions, any pattern is a lead to check, not a
conclusion.
