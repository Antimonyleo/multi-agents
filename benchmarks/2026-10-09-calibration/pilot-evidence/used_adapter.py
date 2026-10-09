#!/usr/bin/env python3
"""Narrow native extraction pilot. No scientific execution or configuration edits."""
import argparse
import collections
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sqlite3
import uuid

ROOT = Path(__file__).resolve().parents[1]
LEGACY = Path('/home/hao/githubrepo/sequence_design/tools/workflow_evaluation/run.py')
SCOPE = ('This is a synthetic read-only inventory extraction task. Access only this '
         'workspace and, in the workflow arm, the scientific-workflow skill and native '
         'role definitions. No other projects, credentials, memory, web, scientific '
         'execution, unrelated processes or configuration changes. No background jobs. '
         'Do not write files. Direct Python/shell scripts are allowed. ')
TASK = ('Inspect every JSON file recursively under inventory/. From each file select '
        'the record with the greatest integer revision among records where enabled '
        'is true and outcome is exactly ready. Ignore higher ineligible revisions. '
        'Return one entry per file: path relative to the workspace, component from '
        'the document, revision and label from the selected record. Sort entries by '
        'path. Return only JSON with a single entries array. Do not omit any file.')
SCHEMA = {'type': 'object', 'properties': {'entries': {'type': 'array', 'items': {
    'type': 'object', 'properties': {'path': {'type': 'string'}, 'component': {'type': 'string'},
    'revision': {'type': 'integer'}, 'label': {'type': 'string'}},
    'required': ['path', 'component', 'revision', 'label'], 'additionalProperties': False}}},
    'required': ['entries'], 'additionalProperties': False}


def write(path, obj):
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fingerprint(root):
    return {str(p.relative_to(root)): sha(p) for p in sorted(root.rglob('*')) if p.is_file()}


def build_fixture(root, count=96):
    root.mkdir(parents=True, exist_ok=False)
    truth = []
    for i in range(count):
        path = root / f'inventory/group_{i % 8:02d}/component_{i:03d}.json'
        path.parent.mkdir(parents=True, exist_ok=True)
        revision = 3 + i % 7
        label = f'label-{(i * 7919) % 100003:05d}'
        records = [
            {'revision': revision + 2, 'enabled': True, 'outcome': 'pending', 'label': 'ineligible-pending'},
            {'revision': revision - 1, 'enabled': True, 'outcome': 'ready', 'label': 'older'},
            {'revision': revision + 3, 'enabled': False, 'outcome': 'ready', 'label': 'disabled'},
            {'revision': revision, 'enabled': True, 'outcome': 'ready', 'label': label},
            {'revision': revision + 1, 'enabled': True, 'outcome': 'READY', 'label': 'wrong-case'},
        ]
        if i % 2:
            records.reverse()
        write(path, {'component': f'component-{i:03d}', 'records': records,
                     'notes': 'synthetic inventory; no scientific data'})
        truth.append({'path': str(path.relative_to(root)), 'component': f'component-{i:03d}',
                      'revision': revision, 'label': label})
    return {'entries': sorted(truth, key=lambda x: x['path'])}


def reference(root):
    """Independent raw-input algorithm; no generator formulas or cached truth."""
    rows = []
    for p in sorted((root / 'inventory').rglob('*.json')):
        doc = json.loads(p.read_text())
        eligible = [r for r in doc['records'] if r['enabled'] is True and r['outcome'] == 'ready']
        selected = sorted(eligible, key=lambda r: r['revision'])[-1]
        rows.append(dict(path=str(p.relative_to(root)), component=doc['component'],
                         revision=selected['revision'], label=selected['label']))
    return {'entries': rows}


def score(answer, expected):
    # Python bool equals integer; require strict JSON field types first.
    if not isinstance(answer, dict) or set(answer) != {'entries'} or not isinstance(answer['entries'], list):
        return False
    for row in answer['entries']:
        if not isinstance(row, dict) or set(row) != {'path', 'component', 'revision', 'label'}:
            return False
        if type(row['revision']) is not int or any(type(row[k]) is not str for k in ('path', 'component', 'label')):
            return False
    return answer == expected


def events(path):
    result = []
    if path.exists():
        for n, line in enumerate(path.read_text().splitlines(), 1):
            if line.strip():
                try:
                    result.append(json.loads(line))
                except ValueError as exc:
                    raise ValueError(f'malformed JSONL {path.name}:{n}') from exc
    return result


def normalize(provider, stream, native=None):
    """Keep provider accounting separate; unknown child semantics never mean zero."""
    native = native or []
    tools = collections.Counter()
    delegates = []
    usage = None
    observed = set()
    result = None
    for e in stream:
        if provider == 'codex':
            if e.get('type') == 'turn.completed':
                usage = e.get('usage')
            item = e.get('item', {})
            if e.get('type') == 'item.completed':
                tools[item.get('type', 'unknown')] += 1
                if item.get('type') == 'collab_tool_call' and item.get('tool') == 'spawn_agent':
                    delegates.append(item)
        else:
            if e.get('type') == 'result':
                result = e
                usage = e.get('usage')
            m = e.get('message', {})
            if m.get('model'):
                observed.add(m['model'])
            for c in m.get('content', []) or []:
                if isinstance(c, dict) and c.get('type') == 'tool_use':
                    tools[c.get('name', 'unknown')] += 1
                    if c.get('name') in ('Agent', 'Task'):
                        delegates.append({'role': c.get('input', {}).get('subagent_type'),
                                          'tool_use_id': c.get('id'), 'input': c.get('input')})
    children = []
    thread_usage = []
    for trace in native:
        meta = next((e.get('payload', {}) for e in trace if e.get('type') == 'session_meta'), {})
        contexts = [e['payload'] for e in trace if e.get('type') == 'turn_context']
        for ctx in contexts:
            if ctx.get('model'):
                observed.add(ctx['model'])
        counts = [e.get('payload', {}).get('info', {}).get('total_token_usage') for e in trace
                  if e.get('type') == 'event_msg' and e.get('payload', {}).get('type') == 'token_count']
        counts = [u for u in counts if u is not None]
        thread_usage.append({'id': meta.get('id'), 'usage_last_cumulative': counts[-1] if counts else None,
                             'model_contexts': [{'model': c.get('model'), 'effort': c.get('effort')} for c in contexts]})
        parent = meta.get('parent_thread_id')
        source = meta.get('source', {})
        if isinstance(source, dict):
            spawn = source.get('subagent', {}).get('thread_spawn', {})
            parent = parent or spawn.get('parent_thread_id')
        if parent:
            children.append({'id': meta.get('id'), 'parent': parent, 'role': meta.get('agent_role'),
                             'models': sorted({c.get('model') for c in contexts if c.get('model')})})
    return {'provider_usage': usage, 'provider_result_model_usage': (result or {}).get('modelUsage'),
            'provider_reported_cost_usd': (result or {}).get('total_cost_usd'),
            'provider_error': (result or {}).get('is_error') if provider == 'claude' else None,
            'observed_models': sorted(observed), 'tools': dict(tools), 'delegate_calls': delegates,
            'native_children': children, 'thread_usage': thread_usage,
            'whole_family_accounting': 'unverified' if delegates or children else 'parent_only_no_delegate_observed',
            'net_cost_claim_supported': False,
            'accounting_note': 'Do not sum parent result totals and child transcripts; inclusion semantics unverified.'}


def prepare(args):
    out = Path(args.output).resolve()
    out.mkdir(parents=True, exist_ok=False)
    workspace = out / 'workspace'
    truth = build_fixture(workspace)
    if truth != reference(workspace):
        raise ValueError('independent reference disagrees')
    write(out / 'truth.json', truth)
    write(out / 'schema.json', SCHEMA)
    (workspace / 'AGENTS.md').write_text(SCOPE + '\n')
    (workspace / 'CLAUDE.md').write_text('@AGENTS.md\n')
    if args.arm == 'workflow':
        shutil.copytree(ROOT / 'skill/scientific-workflow', workspace / '.agents/skills/scientific-workflow')
        shutil.copytree(ROOT / 'skill/scientific-workflow', workspace / '.claude/skills/scientific-workflow')
    intervention = ('Use $scientific-workflow. Zero or one native scientific_explorer support call is '
                    'permitted only if it saves substantial owner work. No other delegate, no reviewer, '
                    'no helper delegation. Direct tools and choosing no helper are valid. '
                    if args.arm == 'workflow' else
                    'Use one main execution owner and direct tools. Do not invoke skills or delegates. ')
    prompt = SCOPE + intervention + TASK + '\n'
    (out / 'prompt.txt').write_text(prompt)
    sid = str(uuid.uuid4())
    if args.provider == 'codex':
        command = ['codex', '--no-daemon', 'exec', '--skip-git-repo-check', '--model', 'gpt-6.1-sol',
                   '--sandbox', 'read-only', '--config', 'approval_policy="never"',
                   '--config', 'model_reasoning_effort="high"', '--config', 'web_search="disabled"',
                   '--config', 'features.memories=false', '--config', 'mcp_servers.openaiDeveloperDocs.enabled=false',
                   '--config', 'agents.max_threads=2', '--config', 'agents.max_depth=1',
                   '--json', '--color', 'never', '--cd', str(workspace),
                   '--output-schema', str(out / 'schema.json'), '--output-last-message', str(out / 'answer.json'), '-']
    else:
        available = 'Read,Glob,Grep,Bash' + (',Agent,Skill' if args.arm == 'workflow' else '')
        command = ['claude', '-p', '--model', 'opus', '--effort', 'high', '--session-id', sid,
                   '--setting-sources', 'user', '--settings', '{"disableAllHooks":true}',
                   '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}',
                   '--permission-mode', 'dontAsk', '--permission-prompts', 'none',
                   '--tools', available, '--allowedTools', available,
                   '--output-format', 'stream-json', '--verbose', '--max-budget-usd', '2',
                   '--json-schema', json.dumps(SCHEMA), '--append-system-prompt', SCOPE]
    manifest = {'provider': args.provider, 'arm': args.arm, 'session_id_requested': sid,
                'command': command, 'timeout_s': 300, 'model_requested': 'gpt-6.1-sol' if args.provider == 'codex' else 'opus',
                'effort_requested': 'high', 'scientific_execution': False, 'before': fingerprint(workspace),
                'prompt_sha256': sha(out / 'prompt.txt'), 'adapter_sha256': sha(Path(__file__)),
                'legacy_harness_sha256': sha(LEGACY), 'truth_sha256': sha(out / 'truth.json'),
                'native_config_sha256': sha(Path.home() / ('.codex/config.toml' if args.provider == 'codex' else '.claude/settings.json')),
                'native_agent_hashes': {str(p): sha(p) for p in sorted((Path.home() / ('.codex/agents' if args.provider == 'codex' else '.claude/agents')).glob('scientific_*'))},
                'envelope': {'top_level_start_cap': 4, 'optional_support_start_cap_total': 2,
                             'per_session_deadline_s': 300, 'max_support_per_workflow': 1,
                             'codex_hard_dollar_limit': 'not_available', 'claude_cli_budget_usd': 2,
                             'call_caps': 'declared; Codex max_threads and depth constrain concurrency/depth, not total starts'},
                'runtime_differences': ['synthetic scratch cwd', 'read-only task; no writes',
                                        'memory/web/MCP disabled where supported', 'Claude hooks disabled; user agents/auth retained',
                                        'Codex direct process (--no-daemon); native user config retained',
                                        'workflow skill snapshotted locally; baseline explicitly declines skill/delegates',
                                        'permissions differ across runtimes; compare within runtime only']}
    write(out / 'manifest.json', manifest)
    return out


def collect_codex(out, stream):
    sid = next((e.get('thread_id') for e in stream if e.get('type') == 'thread.started'), None)
    if not sid:
        return []
    candidates = []
    for db in (Path.home() / '.codex').glob('state_*.sqlite'):
        con = sqlite3.connect(f'file:{db}?mode=ro', uri=True)
        try:
            rows = con.execute('select id, rollout_path, source from threads where cwd=?',
                               (str(out / 'workspace'),)).fetchall()
            candidates.extend(rows)
        finally:
            con.close()
    owned = {sid}
    for _ in range(2):
        for thread, _, source in candidates:
            try:
                source = json.loads(source)
            except (ValueError, TypeError):
                continue
            if isinstance(source, dict) and source.get('subagent', {}).get('thread_spawn', {}).get('parent_thread_id') in owned:
                owned.add(thread)
    result = []
    dest = out / 'native'
    dest.mkdir(exist_ok=True)
    for thread, name, _ in candidates:
        if thread in owned and Path(name).is_file():
            copy = dest / f'{thread}.jsonl'
            shutil.copyfile(name, copy)
            result.append(events(copy))
    return result


def collect_claude(out, sid):
    # Exact requested session identity only; never inspect unrelated conversations.
    dest = out / 'native'
    dest.mkdir(exist_ok=True)
    collected = []
    for project in (Path.home() / '.claude/projects').glob('*'):
        parent = project / f'{sid}.jsonl'
        if parent.is_file():
            shutil.copyfile(parent, dest / 'parent.jsonl')
        folder = project / sid / 'subagents'
        if folder.is_dir():
            for p in folder.glob('agent-*'):
                if p.suffix in ('.jsonl', '.json'):
                    shutil.copyfile(p, dest / p.name)
                    if p.suffix == '.jsonl':
                        collected.append({'file': p.name, 'events': events(p)})
    return collected


def run(out):
    manifest = json.loads((out / 'manifest.json').read_text())
    config = Path.home() / ('.codex/config.toml' if manifest['provider'] == 'codex' else '.claude/settings.json')
    if (sha(config) != manifest['native_config_sha256']
            or sha(out / 'prompt.txt') != manifest['prompt_sha256']
            or sha(out / 'truth.json') != manifest['truth_sha256']
            or sha(Path(__file__)) != manifest['adapter_sha256']
            or sha(LEGACY) != manifest['legacy_harness_sha256']
            or fingerprint(out / 'workspace') != manifest['before']
            or any(sha(Path(p)) != digest for p, digest in manifest['native_agent_hashes'].items())):
        raise ValueError('frozen runtime, adapter, agent, prompt or fixture changed')
    if (out / 'execution.json').exists() or (out / 'trace.jsonl').exists():
        raise ValueError('refusing unchanged retry; preserve previous receipt')
    spec = importlib.util.spec_from_file_location('legacy_workflow_harness', LEGACY)
    legacy = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(legacy)
    # Reuse existing finite timeout/process-group runner, not another orchestrator.
    legacy.run(out, manifest)
    execution = json.loads((out / 'execution.json').read_text())
    stream = events(out / 'trace.jsonl')
    native = collect_codex(out, stream) if manifest['provider'] == 'codex' else []
    child_traces = collect_claude(out, manifest['session_id_requested']) if manifest['provider'] == 'claude' else []
    metrics = normalize(manifest['provider'], stream, native)
    if child_traces:
        metrics['claude_child_evidence'] = [{
            'file': t['file'], 'models': sorted({e.get('message', {}).get('model') for e in t['events'] if e.get('message', {}).get('model')}),
            'usage_raw': [e['message']['usage'] for e in t['events'] if e.get('message', {}).get('usage')],
        } for t in child_traces]
        metrics['whole_family_accounting'] = 'unverified'
    answer = None
    if manifest['provider'] == 'claude':
        final = next((e for e in reversed(stream) if e.get('type') == 'result'), {})
        answer = final.get('structured_output')
        if answer is None:
            try:
                answer = json.loads(final.get('result', ''))
            except ValueError:
                pass
        if answer is not None:
            write(out / 'answer.json', answer)
    elif (out / 'answer.json').exists():
        try:
            answer = json.loads((out / 'answer.json').read_text())
        except ValueError:
            pass
    expected = json.loads((out / 'truth.json').read_text())
    changed = fingerprint(out / 'workspace') != manifest['before']
    checks = {'exact_output': score(answer, expected), 'workspace_unchanged': not changed,
              'terminal_success': execution['returncode'] == 0 and not execution['timed_out'] and metrics['provider_error'] is not True,
              'usage_present': isinstance(metrics['provider_usage'], dict),
              'support_cap': max(len(metrics['delegate_calls']), len(metrics['native_children']), len(child_traces)) <= (1 if manifest['arm'] == 'workflow' else 0)}
    write(out / 'metrics.json', {**metrics, 'checks': checks, 'quality_pass': all(checks.values()),
                                'execution': execution, 'cleanup': 'runner exited; external child termination unverified if any',
                                'scientific_execution': False})
    print(json.dumps({'output': str(out), 'checks': checks, 'wall_s': execution['wall_s'],
                      'delegates': len(metrics['delegate_calls']), 'observed_models': metrics['observed_models'],
                      'cost_usd_reported': metrics['provider_reported_cost_usd']}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['prepare', 'run'])
    parser.add_argument('--provider', choices=['codex', 'claude'])
    parser.add_argument('--arm', choices=['baseline', 'workflow'])
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    if args.action == 'prepare':
        if not args.provider or not args.arm:
            parser.error('prepare requires provider and arm')
        print(prepare(args))
    else:
        run(Path(args.output).resolve())


if __name__ == '__main__':
    main()
