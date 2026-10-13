"""Merge two independent agent labellers per session (PLAN.md, Amendment 2).

  python merge_labels.py disagreements   # write labelers/disagreements.json for adjudication
  python merge_labels.py final           # apply labelers/adjudication.json, write agent-labels.csv
"""
import collections
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LAB = ROOT / 'labelers'
KEYS = ('outcome', 'on_track', 'rework', 'helpers_useful')


def load():
    a, b = {}, {}
    for k in range(3):
        for r in json.loads((LAB / f'batch{k}-A.json').read_text()):
            a[r['session']] = r
        for r in json.loads((LAB / f'batch{k}-B.json').read_text()):
            b[r['session']] = r
    assert set(a) == set(b), set(a) ^ set(b)
    return a, b


def disagreements():
    a, b = load()
    out = []
    for sid in sorted(a):
        diff = [k for k in KEYS if a[sid][k] != b[sid][k]]
        if diff:
            out.append(dict(session=sid, labels=diff,
                            A={k: dict(value=a[sid][k], confidence=a[sid]['confidence'][k], evidence=a[sid]['evidence'][k])
                               for k in diff},
                            B={k: dict(value=b[sid][k], confidence=b[sid]['confidence'][k], evidence=b[sid]['evidence'][k])
                               for k in diff},
                            objective_A=a[sid]['objective'], objective_B=b[sid]['objective']))
    (LAB / 'disagreements.json').write_text(json.dumps(out, indent=1) + '\n')
    agree = {k: sum(a[s][k] == b[s][k] for s in a) for k in KEYS}
    print('sessions', len(a), 'exact agreement', agree, 'sessions with any disagreement', len(out))


def final():
    a, b = load()
    adj = {(r['session'], r['label']): r for r in json.loads((LAB / 'adjudication.json').read_text())}
    rows, agree = [], collections.Counter()
    for sid in sorted(a):
        row = dict(session=sid)
        for k in KEYS:
            same = a[sid][k] == b[sid][k]
            agree[k] += same
            row[k] = a[sid][k] if same else adj[(sid, k)]['value']
            row[k + '_A'], row[k + '_B'] = a[sid][k], b[sid][k]
            row[k + '_how'] = 'agreed' if same else 'adjudicated'
        row['evidence'] = ' | '.join(f"{k}: {(adj[(sid, k)]['reason'] if (sid, k) in adj else a[sid]['evidence'][k])}"
                                     for k in KEYS)[:900]
        rows.append(row)
    with open(ROOT / 'agent-labels.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(rows)
    (ROOT / 'agent-label-agreement.json').write_text(json.dumps(dict(sessions=len(rows), exact_agreement=dict(agree)),
                                                               indent=1) + '\n')
    print('wrote agent-labels.csv;', dict(agree), 'of', len(rows))


if __name__ == '__main__':
    {'disagreements': disagreements, 'final': final}[sys.argv[1]]()
