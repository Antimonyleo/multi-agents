"""Step 2 comparisons fixed in PLAN.md (Amendment 1), written before any labels were seen.

Inputs: agent-labels.csv (final agent labels, Amendment 2), labels.csv (user labels, which
override agent labels where present), aggregates.json, polling.json, prompt-coding.csv.
Writes compare.json and prints Markdown tables. Descriptive only; no tests.
"""
import collections
import csv
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOMINANT = '1ef22ddd'
OUTCOMES = ('achieved', 'partial', 'failed')


def load_labels():
    agent = {r['session']: r for r in csv.DictReader(open(ROOT / 'agent-labels.csv'))}
    user = {r['session']: r for r in csv.DictReader(open(ROOT / 'labels.csv'))}
    final, source = {}, collections.Counter()
    for sid in user:
        row = {}
        for k in ('outcome', 'on_track', 'rework', 'helpers_useful', 'stop_wanted', 'worth_cost'):
            u, a = user[sid].get(k, ''), agent.get(sid, {}).get(k, '')
            row[k] = u or a
            if row[k]:
                source[(k, 'user' if u else 'agent')] += 1
        final[sid] = row
    return final, source


def signals():
    agg = json.loads((ROOT / 'aggregates.json').read_text())
    poll = json.loads((ROOT / 'polling.json').read_text())['by_family']
    coded = list(csv.DictReader(open(ROOT / 'prompt-coding.csv')))
    out = {}
    for f in agg['families']:
        sid, rt = f['session'], f['rt']
        reactive = {c: sum(1 for r in coded if r['session'] == sid and r['category'] == 'continue_broad'
                           and r[c] == 'reactive') for c in ('code', 'code2')}
        s = dict(runtime=rt, active_h=f['active_h'], live=f['live'],
                 helper_share_new=f['helper_share_uncached_out'] if f['helper'][0] else None,
                 reactive_per_prompt_c1=reactive['code'] / f['prompts'] if f['prompts'] else None,
                 reactive_per_prompt_c2=reactive['code2'] / f['prompts'] if f['prompts'] else None)
        if rt == 'claude':
            s['polling_share'] = poll.get(sid, {}).get('polling_processed', 0) / f['total'][0] if f['total'][0] else None
        else:
            s['wait_only_share'] = f['wait_only'] / f['responses'] if f['responses'] else None
            s['compactions_per_h'] = f['compactions'] / f['active_h'] if f['active_h'] else None
            s['orchestration_per_h'] = f['orch'] / f['active_h'] if f['active_h'] else None
        out[sid] = s
    return out


def ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(xs, ys):
    if len(xs) < 10 or len(set(xs)) < 2 or len(set(ys)) < 2:
        return None
    rx, ry = ranks(xs), ranks(ys)
    mx, my = statistics.fmean(rx), statistics.fmean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return num / den if den else None


def by_label(rows, sig, label, values):
    out = {}
    for v in values:
        xs = [r[sig] for r in rows if r['labels'].get(label) == v and r.get(sig) is not None]
        out[v] = dict(n=len(xs), median=statistics.median(xs) if xs else None,
                      min=min(xs) if xs else None, max=max(xs) if xs else None)
    return out


def fmt(d):
    return '; '.join(f"{k}: n={v['n']}" + (f", median {v['median']:.3g} [{v['min']:.3g}–{v['max']:.3g}]" if v['n'] else '')
                     for k, v in d.items())


def main():
    labels, source = load_labels()
    sig = signals()
    rows = [dict(session=sid, labels=labels[sid], **s) for sid, s in sig.items()]
    result = dict(label_sources={f'{k}:{s}': n for (k, s), n in source.items()}, groups={})
    groups = dict(claude=[r for r in rows if r['runtime'] == 'claude'],
                  codex=[r for r in rows if r['runtime'] == 'codex'])
    groups[f'claude without {DOMINANT}'] = [r for r in groups['claude'] if r['session'] != DOMINANT]
    outcome_rank = {'failed': 0, 'partial': 1, 'achieved': 2}
    for g, rs in groups.items():
        sigs = ['helper_share_new', 'reactive_per_prompt_c1', 'reactive_per_prompt_c2']
        sigs += ['polling_share'] if g.startswith('claude') else ['wait_only_share', 'compactions_per_h',
                                                                  'orchestration_per_h']
        res = dict(n=len(rs), live=sum(1 for r in rs if r['live']),
                   label_counts={k: dict(collections.Counter(r['labels'].get(k) or 'blank' for r in rs))
                                 for k in ('outcome', 'on_track', 'rework', 'helpers_useful', 'stop_wanted', 'worth_cost')},
                   by_outcome={}, by_worth_cost={}, spearman_outcome={})
        print(f'\n## {g} (n={len(rs)}, live at freeze {res["live"]})\n')
        print('Label counts:', json.dumps(res['label_counts']))
        for s in sigs:
            res['by_outcome'][s] = by_label(rs, s, 'outcome', OUTCOMES)
            res['by_worth_cost'][s] = by_label(rs, s, 'worth_cost', ('yes', 'no'))
            pairs = [(r[s], outcome_rank[r['labels']['outcome']]) for r in rs
                     if r.get(s) is not None and r['labels'].get('outcome') in outcome_rank]
            res['spearman_outcome'][s] = spearman([a for a, _ in pairs], [b for _, b in pairs])
            rho = res['spearman_outcome'][s]
            print(f"- {s} by outcome — {fmt(res['by_outcome'][s])}"
                  + (f"; Spearman with outcome rank {rho:+.2f} (n={len(pairs)})" if rho is not None else ''))
            if any(v['n'] for v in res['by_worth_cost'][s].values()):
                print(f"  by worth_cost — {fmt(res['by_worth_cost'][s])}")
        res['helpers_vs_useful'] = by_label(rs, 'helper_share_new', 'helpers_useful', ('yes', 'some', 'no'))
        print(f"- helper_share_new by helpers_useful — {fmt(res['helpers_vs_useful'])}")
        res['reactive_vs_stop_wanted'] = by_label(rs, 'reactive_per_prompt_c1', 'stop_wanted', ('yes', 'some', 'no', 'none'))
        if any(v['n'] for v in res['reactive_vs_stop_wanted'].values()):
            print(f"- reactive_per_prompt_c1 by stop_wanted — {fmt(res['reactive_vs_stop_wanted'])}")
        result['groups'][g] = res
    (ROOT / 'compare.json').write_text(json.dumps(result, indent=1) + '\n')


if __name__ == '__main__':
    main()
