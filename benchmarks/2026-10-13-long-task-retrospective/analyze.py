"""Aggregate summary.json into report tables (stdout, Markdown) and aggregates.json.

Revision 2: totals also without the dominant Claude session, per-session medians, counts per
active hour, Codex exec waits and wait-only responses, helper orchestration calls, and the
redo measure counted from helper return.
"""
import collections
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent
S = json.loads((ROOT / 'summary.json').read_text())
DOMINANT = '1ef22ddd'


def split(runtime, t):
    """Return (processed, uncached_input, cached_input, output) for one token record."""
    if not t:
        return None
    if runtime == 'claude':
        unc = t.get('input_tokens', 0) + t.get('cache_creation_input_tokens', 0)
        cached = t.get('cache_read_input_tokens', 0)
        out = t.get('output_tokens', 0)
    else:
        cached = t.get('cached_input_tokens', 0)
        unc = t.get('input_tokens', 0) - cached
        out = t.get('output_tokens', 0)
    return unc + cached + out, unc, cached, out


def add(a, b):
    return tuple(x + y for x, y in zip(a, b)) if b else a


def fmt(n):
    if n is None:
        return '—'
    if n >= 1e9:
        return f'{n / 1e9:.2f}G'
    if n >= 1e6:
        return f'{n / 1e6:.1f}M'
    if n >= 1e3:
        return f'{n / 1e3:.0f}k'
    return str(n)


rows, agg = [], collections.defaultdict(lambda: collections.Counter())
role_tok = collections.defaultdict(lambda: [0, 0, 0, 0, 0])  # n, processed, uncached, cached, output
fork_ctx = collections.defaultdict(list)
redo = []
for f in S['families']:
    rt = f['runtime']
    parent = split(rt, f['tokens']) or (0, 0, 0, 0)
    helpers = (0, 0, 0, 0)
    missing = 0
    for h in f['helpers']:
        ht = split(rt, h['tokens'])
        if ht is None or ht[0] == 0:
            missing += 1
            continue
        helpers = add(helpers, ht)
        key = (rt, h.get('kind', 'spawn') if rt == 'codex' else 'agent',
               h.get('agent_type') or h.get('agent_role') or 'unspecified')
        r = role_tok[key]
        r[0] += 1
        for i in range(4):
            r[i + 1] += ht[i]
        if rt == 'codex' and h.get('kind') == 'spawn' and h.get('context_first10_median') is not None:
            fork_ctx['forked' if h.get('forked') else 'fresh'].append(h['context_first10_median'])
        if rt == 'claude':
            redo.append(dict(depth=h.get('depth'), background=h.get('background'), located=h.get('return_located'),
                             child_reads=h['child_files_read'], rereads=h.get('parent_rereads_of_child_files')))
    total = add(parent, helpers)
    orch = sum((f.get('orchestration_calls') or {}).values())
    helper_orch = sum(sum((h.get('orchestration_calls') or {}).values()) for h in f['helpers'])
    wake = sum((f.get('automated_wakeups') or {}).values())
    rows.append(dict(session=f['session'][:8], rt=rt, project=Path(f['project']).name.replace('-home-hao-', ''),
                     start=(f['start'] or '')[:10], active_h=(f['active_s'] or 0) / 3600,
                     prompts=f['user_prompts'], responses=f['responses'], compactions=f['compactions'],
                     ctx_max=f['context_max'], helpers=len(f['helpers']), helpers_missing_usage=missing,
                     parent=parent, helper=helpers, total=total,
                     helper_share=helpers[0] / total[0] if total[0] else None,
                     helper_share_uncached_out=(helpers[1] + helpers[3]) / (total[1] + total[3]) if total[0] else None,
                     orch=orch, helper_orch=helper_orch, wake=wake, corrections=f['correction_candidates'],
                     interrupts=f['interrupts'], tool_calls=f['tool_calls'], rereads=f.get('unchanged_rereads'),
                     post_compact_rereads=f.get('post_compaction_rereads'),
                     repeats=f['repeated_commands_no_edit'], errors=f.get('tool_errors'),
                     exec_waits=sum((f.get('exec_waits') or {}).values()),
                     wait_only=f.get('wait_only_responses'), wait_agent_only=f.get('wait_agent_only_responses'),
                     counter_resets=f.get('counter_resets', 0) + sum(h.get('counter_resets') or 0 for h in f['helpers']),
                     ctx_mean=f.get('context_mean'), live=f.get('live_at_freeze')))
    groups = [rt] + ([f'{rt} without {DOMINANT}'] if f['session'][:8] != DOMINANT and rt == 'claude' else [])
    for g in groups:
        a = agg[g]
        a['families'] += 1
        a['active_s'] += f['active_s'] or 0
        a['prompts'] += f['user_prompts']
        a['responses'] += f['responses']
        a['compactions'] += f['compactions']
        a['helpers'] += len(f['helpers'])
        a['orch'] += orch
        a['helper_orch'] += helper_orch
        a['exec_waits'] += rows[-1]['exec_waits']
        a['wait_only'] += f.get('wait_only_responses') or 0
        a['wait_agent_only'] += f.get('wait_agent_only_responses') or 0
        a['wake'] += wake
        a['tool_calls'] += f['tool_calls']
        a['tool_errors'] += f.get('tool_errors') or 0
        a['repeats'] += f['repeated_commands_no_edit']
        a['unchanged_rereads'] += f.get('unchanged_rereads') or 0
        a['post_compact_rereads'] += f.get('post_compaction_rereads') or 0
        a['corrections'] += f['correction_candidates']
        a['interrupts'] += f['interrupts']
        a['counter_resets'] += rows[-1]['counter_resets']
        for k, v in (f.get('repeated_command_kinds') or {}).items():
            a['repeats_' + k] += v
        if rt == 'codex':
            for k, v in (f.get('wait_agent_timeouts') or {}).items():
                a['wait_agent_timeout ' + k] += v
            a['wait_only_input'] += f.get('wait_only_input_tokens') or 0
            a['parent_input'] += (f['tokens'] or {}).get('input_tokens', 0)
        for i, k in enumerate(('processed', 'uncached', 'cached', 'output')):
            a['parent_' + k] += parent[i]
            a['helper_' + k] += helpers[i]

print('## Families\n')
print('| Session | RT | Project | Start | Active h | Prompts | Compactions | Max ctx | Helpers | Helper share (all / uncached+out) | Orchestration calls | Auto wake-ups | Correction cand. | Interrupts | Repeat cmds |')
print('|' + '---|' * 15)
for r in sorted(rows, key=lambda r: (r['rt'], r['start'])):
    hs = '—' if r['helper_share'] is None else f"{r['helper_share']:.0%} / {r['helper_share_uncached_out']:.0%}"
    print(f"| {r['session']} | {r['rt']} | {r['project']} | {r['start']} | {r['active_h']:.1f} | {r['prompts']} | "
          f"{r['compactions']} | {fmt(r['ctx_max'])} | {r['helpers']} | {hs} | {r['orch']} | {r['wake']} | "
          f"{r['corrections']} | {r['interrupts']} | {r['repeats']} |")

print('\n## Totals by runtime\n')
for rt, a in agg.items():
    tot = a['parent_processed'] + a['helper_processed']
    unc_out = a['parent_uncached'] + a['parent_output'] + a['helper_uncached'] + a['helper_output']
    hours = a['active_s'] / 3600
    print(f"- **{rt}**: {a['families']} families, {hours:.1f} active h, {a['prompts']} prompts, "
          f"{a['responses']} parent model calls, {a['helpers']} helper/guardian sessions, {a['orch']} parent "
          f"orchestration calls (+{a['helper_orch']} by helpers), {a['exec_waits']} exec waits, {a['wait_only']} "
          f"wait-only parent calls ({a['wait_agent_only']} wait_agent only), {a['wake']} automated wake-ups, "
          f"{a['compactions']} compactions ({a['compactions'] / hours:.2f}/h), {a['counter_resets']} counter resets, "
          f"{a['tool_errors']} tool errors, {a['interrupts']} interrupts, {a['repeats']} repeated commands, "
          f"{a['unchanged_rereads']} unchanged rereads, {a['post_compact_rereads']} post-compaction rereads, "
          f"{a['corrections']} correction-regex prompts. Tokens processed {fmt(tot)} "
          f"(parent {fmt(a['parent_processed'])}, helpers {fmt(a['helper_processed'])} = {a['helper_processed'] / tot:.0%}). "
          f"Uncached input + output {fmt(unc_out)}, helpers {(a['helper_uncached'] + a['helper_output']) / unc_out:.0%}. "
          f"Cached share of input {(a['parent_cached'] + a['helper_cached']) / (a['parent_cached'] + a['helper_cached'] + a['parent_uncached'] + a['helper_uncached']):.0%}.")

    if rt == 'codex':
        print(f"  - Wait-only parent calls carried {a['wait_only_input'] / a['parent_input']:.1%} of parent input tokens. "
              f"Repeated commands: {a['repeats_inspect_or_wait']} contain an inspection or wait word, "
              f"{a['repeats_other']} do not. wait_agent timeouts: "
              + ', '.join(f"{k.split()[-1]} {v}" for k, v in sorted(a.items()) if k.startswith('wait_agent_timeout')))

print('\n## Per-session distribution (median [min–max])\n')
per_h = lambda r, k: r[k] / r['active_h'] if r['active_h'] else 0
for rt in ('claude', 'codex'):
    rs = [r for r in rows if r['rt'] == rt]
    def dist(vals):
        vals = [v for v in vals if v is not None]
        return f"{statistics.median(vals):.2f} [{min(vals):.2f}–{max(vals):.2f}]" if vals else '—'
    print(f"- **{rt}** (n={len(rs)}): active h {dist([r['active_h'] for r in rs])}; helper share processed "
          f"{dist([r['helper_share'] for r in rs if r['helper'][0]])} (sessions with helpers: "
          f"{sum(1 for r in rs if r['helper'][0])}); helper share new {dist([r['helper_share_uncached_out'] for r in rs if r['helper'][0]])}; "
          f"mean context per call {dist([(r['ctx_mean'] or 0) / 1e3 for r in rs])} k; prompts/h {dist([per_h(r, 'prompts') for r in rs])}; "
          f"compactions/h {dist([per_h(r, 'compactions') for r in rs])}; orchestration/h {dist([per_h(r, 'orch') for r in rs])}")

print('\n## Helpers by role\n')
print('| Runtime | Kind | Role | Sessions | Processed | Uncached in | Output | Processed per session |')
print('|---|---|---|---|---|---|---|---|')
for (rt, kind, role), (n, p, u, c, o) in sorted(role_tok.items(), key=lambda kv: -kv[1][1]):
    print(f'| {rt} | {kind} | {role} | {n} | {fmt(p)} | {fmt(u)} | {fmt(o)} | {fmt(p // n)} |')

print('\n## Codex spawned helpers: starting context (median of first 10 calls)\n')
for k, v in fork_ctx.items():
    print(f'- {k}: n={len(v)}, median {fmt(statistics.median(v))}, upper quartile {fmt(statistics.quantiles(v, n=4)[2]) if len(v) > 3 else "—"}')

by_model = collections.defaultdict(lambda: [0, 0])  # helper sessions, new tokens (uncached input + output)
for f in S['families']:
    if f['runtime'] != 'claude':
        continue
    for h in f['helpers']:
        family = next((m for m in ('opus', 'sonnet', 'haiku') if m in (max(h['models'], key=h['models'].get)
                                                                         if h['models'] else '')), 'none')
        t = split('claude', h['tokens'])
        by_model[family][0] += 1
        by_model[family][1] += t[1] + t[3]
new_total = sum(v[1] for v in by_model.values())
print('\n## Claude helpers by main model (most responses)\n')
for k, (n, new) in sorted(by_model.items(), key=lambda kv: -kv[1][0]):
    print(f'- {k}: {n} sessions, {new / new_total:.0%} of helper new tokens')

redo_summary = dict(
    helpers=len(redo), depth2=sum(1 for r in redo if r['depth'] == 2),
    background=sum(1 for r in redo if r['background']),
    return_located=sum(1 for r in redo if r['located']),
    located_with_reads=sum(1 for r in redo if r['rereads'] is not None),
    reread_any=sum(1 for r in redo if r['rereads']))
print('\n## Claude redo-after-helper (planned measure, window opens at helper return)\n')
print(f"- {redo_summary}")

(ROOT / 'aggregates.json').write_text(json.dumps(dict(
    families=rows, by_runtime={k: dict(v) for k, v in agg.items()},
    helpers_by_role=[dict(runtime=k[0], kind=k[1], role=k[2], sessions=v[0], processed=v[1], uncached=v[2],
                          cached=v[3], output=v[4]) for k, v in role_tok.items()],
    codex_spawn_start_context={k: dict(n=len(v), median=statistics.median(v)) for k, v in fork_ctx.items()},
    claude_helpers_by_model={k: dict(sessions=n, new_tokens=new) for k, (n, new) in by_model.items()},
    claude_redo=redo_summary), indent=1, default=list) + '\n')
