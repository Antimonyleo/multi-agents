"""Aggregate summary.json into report tables (stdout, Markdown) and aggregates.json."""
import collections
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent
S = json.loads((ROOT / 'summary.json').read_text())


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
        if rt == 'claude' and h.get('parent_rereads_of_child_files') is not None:
            redo.append((h['parent_rereads_of_child_files'], h['child_files_read']))
    total = add(parent, helpers)
    orch = sum((f.get('orchestration_calls') or {}).values())
    wake = sum((f.get('automated_wakeups') or {}).values())
    rows.append(dict(session=f['session'][:8], rt=rt, project=Path(f['project']).name.replace('-home-hao-', ''),
                     start=(f['start'] or '')[:10], active_h=(f['active_s'] or 0) / 3600,
                     prompts=f['user_prompts'], responses=f['responses'], compactions=f['compactions'],
                     ctx_max=f['context_max'], helpers=len(f['helpers']), helpers_missing_usage=missing,
                     parent=parent, helper=helpers, total=total,
                     helper_share=helpers[0] / total[0] if total[0] else None,
                     helper_share_uncached_out=(helpers[1] + helpers[3]) / (total[1] + total[3]) if total[0] else None,
                     orch=orch, wake=wake, corrections=f['correction_candidates'], interrupts=f['interrupts'],
                     tool_calls=f['tool_calls'], rereads=f.get('unchanged_rereads'),
                     post_compact_rereads=f.get('post_compaction_rereads'),
                     repeats=f['repeated_commands_no_edit'], errors=f.get('tool_errors')))
    a = agg[rt]
    a['families'] += 1
    a['active_s'] += f['active_s'] or 0
    a['prompts'] += f['user_prompts']
    a['compactions'] += f['compactions']
    a['helpers'] += len(f['helpers'])
    a['orch'] += orch
    a['wake'] += wake
    a['tool_calls'] += f['tool_calls']
    a['repeats'] += f['repeated_commands_no_edit']
    a['corrections'] += f['correction_candidates']
    a['interrupts'] += f['interrupts']
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
    print(f"- **{rt}**: {a['families']} families, {a['active_s'] / 3600:.1f} active h, {a['prompts']} prompts, "
          f"{a['helpers']} helper/guardian sessions, {a['orch']} orchestration calls, {a['wake']} automated wake-ups, "
          f"{a['compactions']} compactions. Tokens processed {fmt(tot)} (parent {fmt(a['parent_processed'])}, "
          f"helpers {fmt(a['helper_processed'])} = {a['helper_processed'] / tot:.0%}). Uncached input + output "
          f"{fmt(unc_out)}, helpers {(a['helper_uncached'] + a['helper_output']) / unc_out:.0%}. Cached share of "
          f"input {(a['parent_cached'] + a['helper_cached']) / (a['parent_cached'] + a['helper_cached'] + a['parent_uncached'] + a['helper_uncached']):.0%}.")

print('\n## Helpers by role\n')
print('| Runtime | Kind | Role | Sessions | Processed | Uncached in | Output | Processed per session |')
print('|---|---|---|---|---|---|---|---|')
for (rt, kind, role), (n, p, u, c, o) in sorted(role_tok.items(), key=lambda kv: -kv[1][1]):
    print(f'| {rt} | {kind} | {role} | {n} | {fmt(p)} | {fmt(u)} | {fmt(o)} | {fmt(p // n)} |')

print('\n## Codex spawned helpers: starting context (median of first 10 calls)\n')
for k, v in fork_ctx.items():
    print(f'- {k}: n={len(v)}, median {fmt(statistics.median(v))}, upper quartile {fmt(statistics.quantiles(v, n=4)[2]) if len(v) > 3 else "—"}')

if redo:
    with_reads = [r for r in redo if r[1] > 0]
    any_redo = sum(1 for r in with_reads if r[0] > 0)
    print(f'\n## Claude redo-after-helper\n\n- Helpers that read files and returned to a locatable parent call: {len(with_reads)}; '
          f'parent re-read at least one of the same files within {30} calls in {any_redo} ({any_redo / len(with_reads):.0%}).')

(ROOT / 'aggregates.json').write_text(json.dumps(dict(
    families=rows, by_runtime={k: dict(v) for k, v in agg.items()},
    helpers_by_role=[dict(runtime=k[0], kind=k[1], role=k[2], sessions=v[0], processed=v[1], uncached=v[2],
                          cached=v[3], output=v[4]) for k, v in role_tok.items()],
    codex_spawn_start_context={k: dict(n=len(v), median=statistics.median(v)) for k, v in fork_ctx.items()},
    claude_redo=dict(helpers=len(redo), with_reads=sum(1 for r in redo if r[1] > 0),
                     reread_any=sum(1 for r in redo if r[1] > 0 and r[0] > 0))), indent=1, default=list) + '\n')
