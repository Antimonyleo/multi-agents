# Step 2: labelling outcomes

Only you know whether a long session got you what you wanted. The scripts
measure tokens and activity; your labels say which sessions were worth them.
Together they show whether drift, repeated work or heavy delegation goes with
worse outcomes.

## How to fill in `labels.csv`

Each row is one long session. The sheet shows its project, start date, active
hours, number of prompts and helpers, and your first and last requests. Judge
from memory and these clues; do not reread transcripts. Spend about 30 seconds
per row. `unsure` is a valid answer and is better than a guess.

| Column | Question | Values |
|---|---|---|
| `outcome` | Judged now, with hindsight: did the session deliver what you wanted from it? | `achieved`, `partial`, `failed`, `abandoned`, `unsure` |
| `on_track` | Did it go where you meant without you steering it back? | `yes` (minor corrections only), `some` (several redirects), `no` (you had to stop, restart or rescue it) |
| `rework` | Did you or a later session have to redo or fix its work? | `none`, `some`, `major`, `unsure` |
| `worth_cost` | For what you got, were the time and usage reasonable? | `yes`, `no`, `unsure` |
| `notes` | Optional, one line: what went wrong or right | free text, e.g. "result later found wrong", "paused by me", "helpers duplicated work" |

Rules of thumb:

- Hindsight counts. A result that looked done but was later found wrong is
  `failed` or `partial`, with `rework` set.
- A session you paused on purpose is `abandoned` only if the work was lost.
  If it stopped at a clean checkpoint, judge the part it finished.
- Judge the session's main objective, not every small request.
- If a session mixed several unrelated tasks, use `notes` to say which one you
  judged.

When the sheet is filled in, the analysis compares your labels with the
measured signals (corrections, compactions, helper share, orchestration calls,
repeated commands). With fewer than about 30 sessions, any pattern is a lead
to check, not a conclusion.
