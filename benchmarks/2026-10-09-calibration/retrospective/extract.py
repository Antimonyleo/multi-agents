"""One-off, read-only extraction for the frozen sample; no runtime/model calls."""
import collections
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
SAMPLE = json.loads((ROOT / 'sample.json').read_text())
ADAPTER = ROOT.parents[2] / 'scripts/native_calibration.py'
spec = importlib.util.spec_from_file_location('adapter', ADAPTER)
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)


def extract(source):
    data = Path(source['path']).read_bytes()
    assert len(data) == source['bytes'], 'source size changed'
    assert hashlib.sha256(data).hexdigest() == source['sha256'], 'source hash changed'
    records = [(n, json.loads(line)) for n, line in enumerate(data.splitlines(), 1)]
    runtime = source['runtime']
    types, tools, calls, responses = collections.Counter(), collections.Counter(), {}, {}
    stamps, completed, starts, compact, errors, usage_lines = [], [], [], [], [], []
    user_lines, final_lines, models, commands = [], [], set(), collections.defaultdict(list)
    for n, r in records:
        types[r.get('type')] += 1
        if r.get('timestamp'):
            stamps.append(datetime.datetime.fromisoformat(r['timestamp'].replace('Z', '+00:00')))
        if runtime == 'codex':
            p = r.get('payload', {})
            if r['type'] == 'turn_context' and p.get('model'):
                models.add(p['model'])
            if r['type'] == 'token_usage_record':
                assert p.get('response_id'), 'missing response ID'
                responses[p['response_id']] = (n, p['usage'])
                usage_lines.append(n)
            if r['type'] == 'event_msg':
                if p.get('type') == 'task_started':
                    starts.append({'line': n, 'turn_id': p.get('turn_id'), 'trigger': p.get('turn_attribution', {}).get('turn_trigger')})
                if p.get('type') == 'task_complete':
                    completed.append({'line': n, 'turn_id': p.get('turn_id'), 'duration_ms': p.get('duration_ms')})
            if r['type'] == 'compacted':
                compact.append(n)
            if r['type'] == 'response_item':
                if p.get('type') in ('function_call', 'custom_tool_call'):
                    calls[p['call_id']] = (n, p['name'], p.get('arguments', p.get('input', '')))
                if p.get('role') == 'user':
                    user_lines.append(n)
                if p.get('role') == 'assistant' and p.get('channel') == 'final':
                    final_lines.append(n)
        else:
            m = r.get('message', {})
            if r['type'] == 'assistant':
                assert m.get('id'), 'missing response ID'
                responses[m['id']] = (n, m.get('usage'))
                models.add(m.get('model'))
                for c in m.get('content', []):
                    if isinstance(c, dict) and c.get('type') == 'tool_use':
                        calls[c['id']] = (n, c['name'], c.get('input', {}))
            if r['type'] == 'user':
                for c in m.get('content', []) if isinstance(m.get('content'), list) else []:
                    if c.get('type') == 'tool_result' and c.get('is_error'):
                        errors.append(n)
                if isinstance(m.get('content'), str):
                    user_lines.append(n)
            if r['type'] == 'system' and r.get('subtype') == 'compact_boundary':
                compact.append(n)

    for n, name, args in calls.values():
        tools[name] += 1
        # Exact repetition candidates only. JS wrappers stay distinct from Bash commands.
        key = json.dumps([name, args], sort_keys=True)
        commands[key].append(n)
    totals = collections.Counter()
    missing_usage = []
    for rid, (n, usage) in responses.items():
        if not isinstance(usage, dict):
            missing_usage.append(n)
            continue
        keys = ('input_tokens', 'cached_input_tokens', 'cache_write_input_tokens', 'output_tokens', 'reasoning_output_tokens') if runtime == 'codex' else ('input_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens', 'output_tokens')
        for k in keys:
            assert type(usage.get(k)) is int and usage[k] >= 0, (n, k)
            totals[k] += usage[k]
    result = {'runtime': runtime, 'path': source['path'], 'sha256': source['sha256'],
              'lines': len(records), 'record_types': dict(types), 'models': sorted(m for m in models if m),
              'span_seconds': (max(stamps) - min(stamps)).total_seconds() if stamps else None,
              'response_ids': len(responses), 'usage_missing_lines': missing_usage,
              'parent_or_child_usage_totals': dict(totals) if responses and not missing_usage else None,
              'tools': dict(tools), 'tool_calls': len(calls),
              'compaction_lines': compact, 'explicit_tool_error_lines': errors,
              'task_starts': starts, 'task_completions': completed,
              'user_message_lines': user_lines, 'final_message_lines': final_lines,
              'exact_repeated_tool_calls': [{'sha256': hashlib.sha256(k.encode()).hexdigest(), 'lines': v}
                                            for k, v in commands.items() if len(v) > 1]}
    if runtime == 'codex':
        counts = [(n, r['payload']['info']['total_token_usage']) for n, r in records
                  if r['type'] == 'event_msg' and r['payload'].get('type') == 'token_count'
                  and r['payload'].get('info')]
        result['last_cumulative_usage'] = {'line': counts[-1][0], 'usage': counts[-1][1]} if counts else None
        event_comparable = (bool(responses) and not missing_usage and bool(counts)
                            and adapter.valid_usage('codex', counts[-1][1])
                            and set(totals) <= set(counts[-1][1]))
        result['response_usage_reconciles_with_cumulative'] = all(
            totals[k] == counts[-1][1][k] for k in totals) if event_comparable else None
        details = adapter.codex_usage_details([r for _, r in records])
        result['record_and_compaction_evidence'] = details
        compaction_totals = collections.Counter()
        for usage in (details['compaction_response_usage'] or {}).values():
            compaction_totals.update(usage)
        result['compaction_usage_totals'] = dict(compaction_totals) if details['compaction_usage_complete'] else None
        last = details['usage_last_record_cumulative']
        record_comparable = (bool(responses) and not missing_usage and last is not None
                             and set(totals) <= set(last))
        result['response_sum_matches_record_total'] = all(
            totals[k] == last[k] for k in totals) if record_comparable else None
        result['event_snapshot_plus_compactions_matches_record_total'] = all(
            counts[-1][1][k] + compaction_totals[k] == totals[k] for k in totals
        ) if event_comparable and record_comparable and details['compaction_usage_complete'] else None
        result['nested_shell_wait_calls'] = sum(
            len(re.findall(r'tools\.write_stdin\s*\(', str(args))) for _, name, args in calls.values() if name == 'exec')
    result['complete_cost_usd'] = None
    return result


if __name__ == '__main__':
    parents = [extract(s) for s in SAMPLE['parents']]
    children = [extract(s) for s in SAMPLE['children']]
    output = {'scope': SAMPLE['scope'], 'adapter_sha256': hashlib.sha256(ADAPTER.read_bytes()).hexdigest(),
              'extractor_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'parents': parents, 'children': children,
              'limits': ['No aggregate parent/child cost; inclusion semantics unverified.',
                         'Task duration includes tools and waits, not pure reasoning time.',
                         'Exact repeated calls are candidates, not proven redundant work.',
                         'Usage deduplicated by response ID; child totals stay separate and inherited history is not reconciled.']}
    (ROOT / 'summary.json').write_text(json.dumps(output, indent=2) + '\n')
    for p in parents:
        print(json.dumps({k: p[k] for k in ['runtime', 'span_seconds', 'response_ids', 'tool_calls',
                                         'tools', 'parent_or_child_usage_totals', 'compaction_lines',
                                         'explicit_tool_error_lines']}))
