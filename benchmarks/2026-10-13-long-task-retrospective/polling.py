"""Claude responses whose only tool calls are waiting. Post-hoc measure (not in PLAN.md). Read-only.

A response counts as polling when every tool call in it is a Bash command whose parts
(split on ; && || and newlines) are all `date`, `sleep N`, `true`, `:` or an `echo` of at
most 80 characters, or a Read of a path that session has read more than 5 times since its
last Edit/Write of that path. Tokens are deduplicated by message ID (last record wins).
Shape only: it does not prove the response was avoidable.

Revision 2: per-rule and per-session breakdowns, results without session 1ef22ddd, Read
count reset after an edit, fractional sleeps and chained commands matched.
"""
import collections
import json
import re
from pathlib import Path

import extract as X

ROOT = Path(__file__).resolve().parent
PART = re.compile(r'^(date(\s+\+\S+)?|sleep\s+\d+(\.\d+)?|true|:|echo\b.{0,80})$')
SPLIT = re.compile(r'\s*(?:;|&&|\|\||\n)\s*')
FIELDS = ('input_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens', 'output_tokens')
DOMINANT = '1ef22ddd'


def bash_parts(cmd):
    parts = [p.strip() for p in SPLIT.split(cmd or '') if p.strip()]
    if parts and all(PART.match(p) for p in parts):
        return [p.split()[0] for p in parts]
    return None


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
            if not (isinstance(b, dict) and b.get('type') == 'tool_use'):
                continue
            inp = b.get('input') or {}
            if b['name'] == 'Read':
                path = inp.get('file_path')
                reads[path] += 1
                entry['tools'].append(['read'] if reads[path] > 5 else None)
            elif b['name'] in X.EDIT_TOOLS:
                reads.pop(inp.get('file_path') or inp.get('notebook_path'), None)
                entry['tools'].append(None)
            elif b['name'] == 'Bash':
                entry['tools'].append(bash_parts(inp.get('command')))
            else:
                entry['tools'].append(None)
    poll, total, parts, n_poll = collections.Counter(), collections.Counter(), collections.Counter(), 0
    by_rule = collections.Counter()
    for e in by_id.values():
        vals = {k: int((e['usage'] or {}).get(k) or 0) for k in FIELDS}
        total.update(vals)
        if e['tools'] and all(t is not None for t in e['tools']):
            poll.update(vals)
            n_poll += 1
            kinds = {p for t in e['tools'] for p in t}
            for t in e['tools']:
                parts.update(t)
            by_rule['read only' if kinds == {'read'} else 'bash only' if 'read' not in kinds else 'mixed'] += 1
    return n_poll, len(by_id), poll, total, parts, by_rule


def share(poll, total):
    new = ('input_tokens', 'cache_creation_input_tokens', 'output_tokens')
    return dict(processed=sum(poll.values()) / max(1, sum(total.values())),
                new=sum(poll[k] for k in new) / max(1, sum(total[k] for k in new)))


def main():
    sample = json.loads((ROOT / 'sample.json').read_text())
    parent_of = {e['path']: Path(e['path']).stem[:8] for e in sample['entries'] if e['role'] == 'parent'}
    groups = collections.defaultdict(lambda: dict(n=0, responses=0, poll=collections.Counter(),
                                                  total=collections.Counter(), parts=collections.Counter(),
                                                  rules=collections.Counter()))
    per_session, heavy = collections.defaultdict(lambda: [0, 0, 0]), []
    for e in sample['entries']:
        if e['runtime'] != 'claude':
            continue
        n, total_n, poll, total, parts, rules = session_polling(X.read_prefix(e))
        role = 'parent' if e['role'] == 'parent' else 'helper'
        family = parent_of[e['path'] if role == 'parent' else e['parent']]
        for g in (role, f'{role} without {DOMINANT}' if family != DOMINANT else None):
            if g:
                a = groups[g]
                a['n'] += n
                a['responses'] += total_n
                a['poll'].update(poll)
                a['total'].update(total)
                a['parts'].update(parts)
                a['rules'].update(rules)
        s = per_session[family]
        s[0] += n
        s[1] += total_n
        s[2] += sum(poll.values())
        if n >= 100:
            heavy.append(dict(family=family, role=role, model=e.get('meta', {}).get('model'),
                              description=e.get('meta', {}).get('description'), polling_responses=n,
                              responses=total_n, polling_processed=sum(poll.values()), parts=dict(parts)))
    out = {g: dict(polling_responses=a['n'], responses=a['responses'], polling_tokens=dict(a['poll']),
                   all_tokens=dict(a['total']), share=share(a['poll'], a['total']), parts=dict(a['parts']),
                   by_rule=dict(a['rules'])) for g, a in groups.items()}
    out['by_family'] = {k: dict(polling_responses=v[0], responses=v[1], polling_processed=v[2])
                        for k, v in sorted(per_session.items(), key=lambda kv: -kv[1][2])}
    out['sessions_with_100_plus_polling_responses'] = sorted(heavy, key=lambda r: -r['polling_processed'])
    (ROOT / 'polling.json').write_text(json.dumps(out, indent=1) + '\n')
    for g in sorted(groups):
        o = out[g]
        print(f"{g}: {o['polling_responses']} of {o['responses']} responses; processed share "
              f"{o['share']['processed']:.1%}, new-token share {o['share']['new']:.1%}; parts {o['parts']}; "
              f"rules {o['by_rule']}")
    for k, v in out['by_family'].items():
        if v['polling_responses']:
            print(' family', k, v)
    for r in out['sessions_with_100_plus_polling_responses']:
        print(' ', r['family'], r['role'], r['model'], r['polling_responses'], '/', r['responses'],
              round(r['polling_processed'] / 1e6), 'M', r['parts'], r['description'])


if __name__ == '__main__':
    main()
