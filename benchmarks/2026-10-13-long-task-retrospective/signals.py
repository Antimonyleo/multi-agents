"""Prompt categories (post-hoc, regex) and their hand-coded precision. Read-only on transcripts.

Reads prompt-context.json (written by `extract.py extract`). Writes signals.json and
prompt-matches.csv, the sheet for hand-coding. Hand codes live in prompt-coding.csv; when
that file exists, precision per category is computed from it.

Revision 2: `continue_no_pause` now needs an explicit no-stop phrase; the old broad pattern
is kept as `continue_broad` for comparison. `drift` was added because wandering was
otherwise unmeasured. The Bash-aware redo measure was dropped (it matched basenames and
helper outputs, so it could not separate redo from reading results).
"""
import collections
import csv
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
CATEGORIES = {
    'continue_no_pause': re.compile(r"no need to (stop|pause|ask|wait|check)|do ?n[o']t (stop|pause|ask)|"
                                    r"without (stopping|pausing|asking)|(never|not) stop|this is an override", re.I),
    'continue_broad': re.compile(r"no need to (stop|pause|ask|wait)|do ?n[o']t (stop|pause)|without (stopping|pausing)|"
                                 r"(continue|keep going|proceed)\b.{0,40}\b(all|until|through|execut)|this is an override", re.I),
    'overengineering': re.compile(r"over-?engineer|too defensive|so defensive|too cautious|too conservative", re.I),
    'drift': re.compile(r"off[- ]track|drift|off[- ]topic|lost (sight|focus)|not the (goal|point)|stay (on|focused)|"
                        r"scope creep|side-?track|back to the (main|goal|task)", re.I),
    'disagreement': re.compile(r"i (do not|don'?t) (think|believe|agree)|that'?s (wrong|not right|not what)|incorrect|"
                               r"not what i|you (misunderstood|didn'?t|did not|forgot|missed)", re.I),
    'status_check': re.compile(r"\b(status|progress|still running|any update|how is it going|is it done|finished\?)", re.I),
    'repeat_request': re.compile(r"\b(again|as i said|i said|i already|i told you)\b", re.I),
}
CODED = ('continue_no_pause', 'continue_broad', 'overengineering', 'drift', 'disagreement')
# Hand codes (one coder, from the prompt and the assistant message before it; see REPORT.md):
#   continue_*: reactive (agent stopped part-way through assigned work, or asked, and the user says not to
#     stop) | upfront (no-stop authority given with a new or renewed instruction after a finished unit or
#     plan) | plain (bare "continue" after a stop, no no-stop phrase) | other (not about the agent stopping)
#   overengineering: reactive (complaint about work seen) | preventive (instruction in advance) | question
#   drift: reactive (user or agent states it drifted) | question (asks whether it drifted) | other
#   disagreement: yes | no;  any category: dup (same prompt resent)
GENUINE = {'continue_no_pause': {'reactive', 'upfront'}, 'continue_broad': {'reactive', 'upfront'},
           'overengineering': {'reactive', 'preventive', 'question'}, 'drift': {'reactive', 'question'},
           'disagreement': {'yes'}}


def excerpt(s, n):
    s = ' '.join((s or '').split())
    return s[:n] + ('…' if len(s) > n else '')


def main():
    summary = json.loads((ROOT / 'summary.json').read_text())
    runtime = {f['session'][:8]: f['runtime'] for f in summary['families']}
    ctx = json.loads((ROOT / 'prompt-context.json').read_text())
    rows, matches = [], []
    for sid, prompts in ctx.items():
        counts = collections.Counter()
        for p in prompts:
            for k, rx in CATEGORIES.items():
                if rx.search(p['prompt']):
                    counts[k] += 1
                    if k in CODED:
                        matches.append(dict(session=sid, runtime=runtime[sid], i=p['i'], of=len(prompts),
                                            category=k, prompt=excerpt(p['prompt'], 160), before=excerpt(p['before'], 160)))
        rows.append(dict(session=sid, runtime=runtime[sid], prompts=len(prompts), categories=dict(counts)))
    with open(ROOT / 'prompt-matches.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(matches[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(matches)
    totals = {k: dict(prompts=sum(r['categories'].get(k, 0) for r in rows),
                      sessions=sum(1 for r in rows if r['categories'].get(k))) for k in CATEGORIES}
    precision = {}
    coding = ROOT / 'prompt-coding.csv'
    if coding.exists():
        # code: first coder (report author); code2: blind second coder (separate subagent, same codebook)
        coded = list(csv.DictReader(open(coding)))
        for k in CODED:
            rs = [r for r in coded if r['category'] == k]
            precision[k] = dict(matches=len(rs), agreement=sum(r['code'] == r['code2'] for r in rs),
                                genuine_agreement=sum((r['code'] in GENUINE[k]) == (r['code2'] in GENUINE[k]) for r in rs))
            for col in ('code', 'code2'):
                genuine = [r for r in rs if r[col] in GENUINE[k]]
                reactive = [r for r in rs if r[col] == 'reactive']
                precision[k][col] = dict(codes=dict(collections.Counter(r[col] for r in rs)), genuine=len(genuine),
                                         genuine_sessions=len({r['session'] for r in genuine}),
                                         reactive=len(reactive), reactive_sessions=len({r['session'] for r in reactive}))
    (ROOT / 'signals.json').write_text(json.dumps(dict(families=rows, totals=totals, precision=precision),
                                                  indent=1) + '\n')
    for k, v in totals.items():
        print(f"{k}: {v['prompts']} prompts in {v['sessions']} of {len(rows)} sessions")
    for k, v in precision.items():
        print(f"coded {k}: {v}")


if __name__ == '__main__':
    main()
