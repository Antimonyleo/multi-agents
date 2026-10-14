#!/usr/bin/env python3
"""After-task check of one long Claude or Codex session against the 2026-10-13 baseline.

  python scripts/long_task_monitor.py <session-id-prefix> [--json OUT]

Read-only on transcripts; no model calls. Reuses the retrospective's extractor
(benchmarks/2026-10-13-long-task-retrospective/) so measures match its definitions.
The baseline is its 27 sessions (7 Claude, 20 Codex); sessions differ in task, so a
difference is a lead, not a verdict. Stop candidates are regex matches, not hand codes:
read the listed prompts and judge whether each stop was wanted.
"""
import argparse
import collections
import csv
import glob
import json
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]
RETRO = ROOT / 'benchmarks/2026-10-13-long-task-retrospective'
sys.path.insert(0, str(RETRO))
import extract as X  # noqa: E402
import polling as P  # noqa: E402
from signals import CATEGORIES  # noqa: E402

STOP_CATEGORIES = ('continue_no_pause', 'continue_broad')


def new_tokens(runtime, t):
    """Uncached input plus output, as in the retrospective's helper share."""
    if not t:
        return 0
    if runtime == 'claude':
        return sum(int(t.get(k) or 0) for k in ('input_tokens', 'cache_creation_input_tokens', 'output_tokens'))
    return int(t.get('input_tokens') or 0) - int(t.get('cached_input_tokens') or 0) + int(t.get('output_tokens') or 0)


def processed_tokens(runtime, t):
    if not t:
        return 0
    if runtime == 'claude':
        return sum(int(t.get(k) or 0) for k in P.FIELDS)
    return int(t.get('input_tokens') or 0) + int(t.get('output_tokens') or 0)


def find_session(prefix, claude_root=X.CLAUDE_PROJECTS, codex_root=X.CODEX_SESSIONS):
    hits = [('claude', Path(f)) for f in glob.glob(str(claude_root / '*' / f'{prefix}*.jsonl'))]
    hits += [('codex', Path(f)) for f in glob.glob(str(codex_root / '**' / f'rollout-*{prefix}*.jsonl'), recursive=True)
             if prefix in Path(f).stem[-36:]]
    if len(hits) != 1:
        sys.exit(f'{len(hits)} transcripts match {prefix!r}; give a longer ID prefix. '
                 + ', '.join(str(p) for _, p in hits[:5]))
    return hits[0]


def codex_children(path, codex_root=X.CODEX_SESSIONS):
    """Descendant rollouts linked by parent_thread_id, searched from the parent's date onward."""
    parent = X.codex_meta(path)
    day = path.parent.relative_to(codex_root).parts
    metas = {}
    for f in glob.glob(str(codex_root / '**' / 'rollout-*.jsonl'), recursive=True):
        if Path(f).parent.relative_to(codex_root).parts >= day and f != str(path):
            try:
                metas[f] = X.codex_meta(f)
            except (json.JSONDecodeError, OSError):
                continue
    by_parent = collections.defaultdict(list)
    for f, m in metas.items():
        if m.get('parent_thread_id'):
            by_parent[m['parent_thread_id']].append(f)
    out, stack, seen = [], [parent.get('id')], set()
    while stack:
        for c in by_parent.get(stack.pop(), []):
            if c not in seen:
                seen.add(c)
                out.append(Path(c))
                stack.append(metas[c].get('id'))
    return out


def measure(runtime, path, codex_root=X.CODEX_SESSIONS):
    records = list(X.safe_records(path))
    if runtime == 'claude':
        kids = []
        for c in sorted((path.parent / path.stem / 'subagents').glob('*.jsonl')):
            meta = c.with_suffix('.meta.json')
            kids.append(dict(records=list(X.safe_records(c)), meta=json.loads(meta.read_text()) if meta.exists() else {},
                             agent_id=c.stem.removeprefix('agent-')))
        m = X.claude_metrics(records, kids)
        helper_tokens = [h['tokens'] for h in m['helpers']]
        poll_n, _, poll, _, parts, _ = P.session_polling(records)
        poll_processed = sum(poll.values())
        for k in kids:
            n, _, kp, _, kparts, _ = P.session_polling(k['records'])
            poll_n += n
            poll_processed += sum(kp.values())
            parts.update(kparts)
    else:
        m = X.codex_metrics(records)
        helper_tokens = [X.codex_metrics(list(X.safe_records(c)))['tokens'] for c in codex_children(path, codex_root)]
    active_h = (m['active_s'] or 0) / 3600
    helper_new = sum(new_tokens(runtime, t) for t in helper_tokens)
    total_new = new_tokens(runtime, m['tokens']) + helper_new
    total_processed = processed_tokens(runtime, m['tokens']) + sum(processed_tokens(runtime, t) for t in helper_tokens)
    candidates = [dict(i=i, category=cat, prompt=X.excerpt(p, 300), before=X.excerpt(a, 300))
                  for p, a, i in m['_prompt_ctx'] for cat in STOP_CATEGORIES if CATEGORIES[cat].search(p)]
    prompts = m['user_prompts']
    out = dict(runtime=runtime, path=str(path), start=m['start'], last_record=m['last_record'],
               active_h=active_h, prompts=prompts, responses=m['responses'], helpers=len(helper_tokens),
               new_tokens=total_new, processed_tokens=total_processed,
               helper_share_new=helper_new / total_new if helper_tokens and total_new else None,
               continue_broad_per_prompt=sum(c['category'] == 'continue_broad' for c in candidates) / prompts
               if prompts else None,
               continue_no_pause_per_prompt=sum(c['category'] == 'continue_no_pause' for c in candidates) / prompts
               if prompts else None,
               stop_candidates=candidates)
    if runtime == 'claude':
        out.update(polling_responses=poll_n, polling_share=poll_processed / total_processed if total_processed else None,
                   polling_parts=dict(parts))
    else:
        timeouts = m['wait_agent_timeouts']
        out.update(wait_only_share=m['wait_only_responses'] / m['responses'] if m['responses'] else None,
                   wait_only_input_tokens=m['wait_only_input_tokens'], wait_agent_timeouts=timeouts,
                   wait_agent_short_share=timeouts.get('<=60s', 0) / sum(timeouts.values()) if timeouts else None,
                   compactions_per_h=m['compactions'] / active_h if active_h else None,
                   orchestration_per_h=sum(m['orchestration_calls'].values()) / active_h if active_h else None)
    return out


def baseline(runtime):
    """Per-session values for the retrospective's sessions of one runtime."""
    agg = {f['session']: f for f in json.loads((RETRO / 'aggregates.json').read_text())['families'] if f['rt'] == runtime}
    summary = {f['session'][:8]: f for f in json.loads((RETRO / 'summary.json').read_text())['families']}
    poll = json.loads((RETRO / 'polling.json').read_text())['by_family']
    with open(RETRO / 'prompt-matches.csv') as fh:
        matches = collections.Counter((r['session'], r['category']) for r in csv.DictReader(fh))
    rows = []
    for sid, f in agg.items():
        h, p = f['active_h'], f['prompts']
        row = dict(active_h=h, helper_share_new=f['helper_share_uncached_out'] if f['helper'][0] else None,
                   continue_broad_per_prompt=matches[(sid, 'continue_broad')] / p if p else None,
                   continue_no_pause_per_prompt=matches[(sid, 'continue_no_pause')] / p if p else None)
        if runtime == 'claude':
            row['polling_share'] = poll.get(sid, {}).get('polling_processed', 0) / f['total'][0] if f['total'][0] else None
        else:
            t = summary[sid].get('wait_agent_timeouts') or {}
            row.update(wait_only_share=f['wait_only'] / f['responses'] if f['responses'] else None,
                       wait_agent_short_share=t.get('<=60s', 0) / sum(t.values()) if t else None,
                       compactions_per_h=f['compactions'] / h if h else None,
                       orchestration_per_h=f['orch'] / h if h else None)
        rows.append(row)
    return rows


def compare(result):
    keys = ['active_h', 'helper_share_new', 'continue_no_pause_per_prompt', 'continue_broad_per_prompt']
    keys += ['polling_share'] if result['runtime'] == 'claude' else [
        'wait_only_share', 'wait_agent_short_share', 'compactions_per_h', 'orchestration_per_h']
    rows = baseline(result['runtime'])
    table = []
    for k in keys:
        xs = sorted(r[k] for r in rows if r.get(k) is not None)
        v = result.get(k)
        table.append(dict(measure=k, session=v, n=len(xs), median=statistics.median(xs) if xs else None,
                          min=xs[0] if xs else None, max=xs[-1] if xs else None,
                          below=sum(x < v for x in xs) if v is not None else None))
    return table


def show(result, table):
    g = lambda v: '—' if v is None else f'{v:.3g}'  # noqa: E731
    print(f"{result['runtime']} session {Path(result['path']).stem[-36:]} — {g(result['active_h'])} active h, "
          f"{result['prompts']} prompts, {result['responses']} parent responses, {result['helpers']} helpers, "
          f"{result['new_tokens']:,} new / {result['processed_tokens']:,} processed tokens (family)\n")
    print('| Measure | This session | Baseline median [min–max] (n) | Baseline sessions below |')
    print('|---|---:|---:|---:|')
    for r in table:
        print(f"| {r['measure']} | {g(r['session'])} | {g(r['median'])} [{g(r['min'])}–{g(r['max'])}] ({r['n']}) | "
              f"{'—' if r['below'] is None else r['below']} |")
    if result['runtime'] == 'codex':
        print(f"\nwait_agent timeouts: {result['wait_agent_timeouts']}; "
              f"wait-only calls reread {result['wait_only_input_tokens']:,} input tokens")
    else:
        print(f"\npolling responses: {result['polling_responses']}; parts {result['polling_parts']}")
    print(f"\nStop candidates ({len(result['stop_candidates'])}; regex, judge each):")
    for c in result['stop_candidates']:
        print(f"- prompt {c['i']} [{c['category']}]: {c['prompt']}\n  after agent: {c['before']}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('session', help='session ID or its prefix (Claude session or Codex rollout)')
    ap.add_argument('--json', type=Path, help='also write the result here')
    a = ap.parse_args()
    runtime, path = find_session(a.session)
    result = measure(runtime, path)
    table = compare(result)
    show(result, table)
    if a.json:
        a.json.write_text(json.dumps(dict(result=result, baseline=table), indent=1) + '\n')


if __name__ == '__main__':
    main()
