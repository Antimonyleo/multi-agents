"""Attribute Claude parent and helper responses whose only tool calls are polling. Read-only.

A response counts as polling when every tool call in it is: Bash `date`, `sleep ...`,
a short `echo` tick, or a Read of a path already read at least 5 times by that session.
Tokens of those responses (deduplicated by message ID) are polling tokens. This is a
lower bound for busy-waiting and an upper bound for nothing; review the examples.
"""
import collections
import json
import re
from pathlib import Path

import extract as X

ROOT = Path(__file__).resolve().parent
POLL_BASH = re.compile(r'^\s*(date|sleep\s+\d+(\s*;\s*(date|echo\b[^;|&]{0,40}))?|echo\s+\S{1,12}|true)\s*$')


def session_polling(records):
    reads = collections.Counter()
    by_id = {}
    for r in records:
        if r.get('type') != 'assistant':
            continue
        m = r.get('message') or {}
        mid = m.get('id')
        if not mid:
            continue
        entry = by_id.setdefault(mid, dict(usage=None, tools=[]))
        if isinstance(m.get('usage'), dict):
            entry['usage'] = m['usage']
        for b in m.get('content') or []:
            if isinstance(b, dict) and b.get('type') == 'tool_use':
                inp = b.get('input') or {}
                if b['name'] == 'Read':
                    reads[inp.get('file_path')] += 1
                    entry['tools'].append(('read', reads[inp.get('file_path')]))
                elif b['name'] == 'Bash':
                    entry['tools'].append(('bash', bool(POLL_BASH.match(inp.get('command') or ''))))
                else:
                    entry['tools'].append(('other', False))
    poll = collections.Counter()
    total = collections.Counter()
    n_poll = 0
    for e in by_id.values():
        u = e['usage'] or {}
        vals = {k: int(u.get(k) or 0) for k in ('input_tokens', 'cache_creation_input_tokens',
                                                 'cache_read_input_tokens', 'output_tokens')}
        total.update(vals)
        if e['tools'] and all((k == 'bash' and v) or (k == 'read' and v > 5) for k, v in e['tools']):
            poll.update(vals)
            n_poll += 1
    return n_poll, len(by_id), poll, total


def main():
    sample = json.loads((ROOT / 'sample.json').read_text())
    agg = dict(parent=[0, 0, collections.Counter(), collections.Counter()],
               helper=[0, 0, collections.Counter(), collections.Counter()])
    rows = []
    for e in sample['entries']:
        if e['runtime'] != 'claude':
            continue
        n, total_n, poll, total = session_polling(X.read_prefix(e))
        a = agg[e['role'] if e['role'] == 'parent' else 'helper']
        a[0] += n
        a[1] += total_n
        a[2].update(poll)
        a[3].update(total)
        if n >= 100:
            rows.append(dict(role=e['role'], description=e.get('meta', {}).get('description'),
                             polling_responses=n, responses=total_n,
                             polling_processed=sum(poll.values())))
    out = {}
    for k, (n, t, poll, total) in agg.items():
        out[k] = dict(polling_responses=n, responses=t, polling_tokens=dict(poll), all_tokens=dict(total),
                      polling_share_processed=sum(poll.values()) / max(1, sum(total.values())),
                      polling_share_uncached_and_output=(poll['input_tokens'] + poll['cache_creation_input_tokens'] + poll['output_tokens'])
                      / max(1, total['input_tokens'] + total['cache_creation_input_tokens'] + total['output_tokens']))
    out['sessions_with_100_plus_polling_responses'] = sorted(rows, key=lambda r: -r['polling_processed'])
    (ROOT / 'polling.json').write_text(json.dumps(out, indent=1) + '\n')
    for k in ('parent', 'helper'):
        o = out[k]
        print(k, o['polling_responses'], 'of', o['responses'], 'responses;',
              f"processed share {o['polling_share_processed']:.1%}, uncached+output share {o['polling_share_uncached_and_output']:.1%}")
    for r in out['sessions_with_100_plus_polling_responses']:
        print(' ', r['role'], r['polling_responses'], '/', r['responses'], round(r['polling_processed'] / 1e6), 'M', r['description'])


if __name__ == '__main__':
    main()
