"""Add the three longest user requests per session to labels.csv as memory cues. Read-only on transcripts."""
import csv
import json
from pathlib import Path

import extract as X

ROOT = Path(__file__).resolve().parent


def main():
    sample = json.loads((ROOT / 'sample.json').read_text())
    cues = {}
    for e in sample['entries']:
        if e['role'] != 'parent':
            continue
        records = X.read_prefix(e)
        m = X.claude_metrics(records) if e['runtime'] == 'claude' else X.codex_metrics(records)
        longest = sorted(m['_prompts'], key=len, reverse=True)[:3]
        cues[Path(e['path']).stem[-36:][:8]] = ' || '.join(X.excerpt(p, 200) for p in longest)
    rows = list(csv.DictReader(open(ROOT / 'labels.csv')))
    fields = list(rows[0])
    if 'key_requests' not in fields:
        fields.insert(fields.index('last_request') + 1, 'key_requests')
    for r in rows:
        r['key_requests'] = cues.get(r['session'], '')
    with open(ROOT / 'labels.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print('enriched', len(rows))


if __name__ == '__main__':
    main()
