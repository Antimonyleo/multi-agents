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


PROSE_TASK = ('Read every .txt file recursively under notes/. Each is the revision log of one '
              'component. From each file select the greatest revision number that was approved '
              'and never withdrawn. Return one entry per file: path relative to the workspace, '
              'component from the file header, that revision and its label. Sort entries by '
              'path. Return only JSON with a single entries array. Do not omit any file.')
WORDS = ('the review covered scheduling, vendor handoffs, shelf labels, packing lists and storage '
         'conditions while the team compared earlier notes against current practice and recorded '
         'minor wording changes without altering any decision').split()


def build_prose_fixture(root, count=40):
    """Synthetic prose logs; approval, withdrawal and drafts sit in different sentences."""
    import random
    root.mkdir(parents=True, exist_ok=False)
    truth = []
    for i in range(count):
        rng = random.Random(i)
        path = root / f'notes/team_{i % 5:02d}/component_{i:03d}.txt'
        path.parent.mkdir(parents=True, exist_ok=True)
        r = 3 + i % 7
        label = f'label-{(i * 7919) % 100003:05d}'

        def approved(n, lab):
            if i % 2:
                return f'Board approved revision {n} (label {lab}).'
            return f'Rev {n} was approved by the review board and tagged {lab}.'
        body = [approved(r, label), approved(r - 1, 'label-older'),
                f'Rev {r + 1} was drafted but never approved.',
                approved(r + 2, 'label-withdrawn'),
                f'Revision {r + 3}: label label-pending, approval pending.']
        rng.shuffle(body)
        parts = []
        for sentence in body:
            filler = ' '.join(rng.choice(WORDS) for _ in range(rng.randint(25, 40)))
            parts.append(f'{filler.capitalize()}. {sentence}')
        addenda = f'Addendum: revision {r + 2} was withdrawn after a failed audit.'
        text = f'Component: component-{i:03d}\n\n' + '\n\n'.join(parts) + '\n\n' + addenda + '\n'
        path.write_text(text)
        truth.append({'path': str(path.relative_to(root)), 'component': f'component-{i:03d}',
                      'revision': r, 'label': label})
    return {'entries': sorted(truth, key=lambda x: x['path'])}


def prose_reference(root):
    """Independent raw-text algorithm; no generator formulas or cached truth."""
    import re
    rows = []
    for p in sorted((root / 'notes').rglob('*.txt')):
        text = p.read_text()
        component = re.search(r'^Component: (\S+)', text, re.M).group(1)
        found = {}
        for n, lab in re.findall(r'[Rr]ev(?:ision)? (\d+) was approved by the review board and tagged (\S+?)\.', text):
            found[int(n)] = lab
        for n, lab in re.findall(r'Board approved revision (\d+) \(label (\S+?)\)\.', text):
            found[int(n)] = lab
        for n in re.findall(r'revision (\d+) was withdrawn', text):
            found.pop(int(n), None)
        top = max(found)
        rows.append(dict(path=str(p.relative_to(root)), component=component, revision=top, label=found[top]))
    return {'entries': rows}


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
    responses = {}
    missing_response_id = False
    seen_tools = set()
    for e in stream:
        if provider == 'codex':
            if e.get('type') == 'turn.completed':
                usage = e.get('usage')
            item = e.get('item', {})
            if e.get('type') == 'item.completed' and item.get('id') not in seen_tools:
                if item.get('id'):
                    seen_tools.add(item['id'])
                tools[item.get('type', 'unknown')] += 1
                if item.get('type') == 'collab_tool_call' and item.get('tool') == 'spawn_agent':
                    delegates.append(item)
        else:
            if e.get('type') == 'result':
                result = e
                usage = e.get('usage')
            m = e.get('message', {})
            if e.get('type') == 'assistant' and not e.get('parent_tool_use_id'):
                if not m.get('id'):
                    missing_response_id = True
                else:
                    responses.setdefault(m['id'], None)
                    if isinstance(m.get('usage'), dict):
                        responses[m['id']] = m['usage']
            if m.get('model'):
                observed.add(m['model'])
            for c in m.get('content', []) or []:
                if isinstance(c, dict) and c.get('type') == 'tool_use':
                    if c.get('id') in seen_tools:
                        continue
                    if c.get('id'):
                        seen_tools.add(c['id'])
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
    context_counts = []
    for value in responses.values():
        keys = ('input_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens')
        context_counts.append(sum(value[k] for k in keys) if isinstance(value, dict) and all(type(value.get(k)) is int and value[k] >= 0 for k in keys) else None)
    complete = bool(context_counts) and not missing_response_id and None not in context_counts
    return {'assistant_response_count': len(responses) if responses and not missing_response_id else None,
            'response_telemetry_complete': complete,
            'first_input_context_tokens': context_counts[0] if context_counts and not missing_response_id else None,
            'input_tokens_processed_from_messages': sum(context_counts) if complete else None,
            'response_telemetry_note': 'Latest available usage per stable assistant message ID; missing identities or usage leave totals unknown; child stream messages excluded; not a server request count.',
            'provider_usage': usage, 'provider_result_model_usage': (result or {}).get('modelUsage'),
            'provider_reported_cost_usd': (result or {}).get('total_cost_usd'),
            'provider_error': (result or {}).get('is_error') if provider == 'claude' else None,
            'observed_models': sorted(observed), 'tools': dict(tools), 'delegate_calls': delegates,
            'native_children': children, 'thread_usage': thread_usage,
            'whole_family_accounting': 'unverified' if delegates or children else 'parent_only_no_delegate_observed',
            'net_cost_claim_supported': False,
            'accounting_note': 'Do not sum parent result totals and child transcripts; inclusion semantics unverified.'}


def toolset(arm, comparison):
    available = 'Read,Glob,Grep,Bash'
    if comparison == 'routing' or arm == 'workflow':
        available += ',Agent,Skill'
    return available


def native_capability_files(provider):
    """Re-enumerate user agent files and skill entrypoints, including additions.

    This is a bounded local inventory, not the effective runtime/plugin catalog.
    """
    home = Path.home()
    runtime = home / ('.codex' if provider == 'codex' else '.claude')
    paths = {p for p in (runtime / 'agents').rglob('*') if p.is_file()}
    for root in (home / '.agents/skills', runtime / 'skills'):
        if root.is_dir():
            for entry in root.iterdir():
                if entry.is_dir():
                    paths.update(p for p in entry.rglob('SKILL.md') if p.is_file())
    return {str(p): sha(p) for p in sorted(paths)}


def build_command(out, manifest):
    """Bind launch arguments to the declared controls and checked workspace."""
    workspace = out / 'workspace'
    if manifest['provider'] == 'codex':
        command = ['codex', '--no-daemon', 'exec', '--skip-git-repo-check', '--model', manifest['model_requested'],
                   '--sandbox', 'read-only', '--config', 'approval_policy="never"',
                   '--config', 'model_reasoning_effort=' + json.dumps(manifest['effort_requested']), '--config', 'web_search="disabled"',
                   '--config', 'features.memories=false', '--config', 'mcp_servers.openaiDeveloperDocs.enabled=false',
                   '--config', 'agents.max_threads=2', '--config', 'agents.max_depth=1',
                   '--json', '--color', 'never', '--cd', str(workspace),
                   '--output-schema', str(out / 'schema.json'), '--output-last-message', str(out / 'answer.json'), '-']
    else:
        available = toolset(manifest['arm'], manifest['comparison'])
        command = ['claude', '-p', '--model', manifest['model_requested'], '--effort', manifest['effort_requested'], '--session-id', manifest['session_id_requested'],
                   '--setting-sources', 'user', '--settings', '{"disableAllHooks":true}',
                   '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}',
                   '--permission-mode', 'dontAsk', '--permission-prompts', 'none',
                   '--tools', available, '--allowedTools', available,
                   '--output-format', 'stream-json', '--verbose', '--max-budget-usd', str(manifest['envelope']['claude_cli_budget_usd']),
                   '--json-schema', json.dumps(json.loads((out / 'schema.json').read_text())), '--append-system-prompt', SCOPE]
    return command


def frozen_errors(out, manifest):
    """Read-only identity checks, also used before any model process starts."""
    errors = []
    files = {'prompt.txt': 'prompt_sha256', 'truth.json': 'truth_sha256',
             'schema.json': 'schema_sha256'}
    for name, key in files.items():
        if not (out / name).is_file() or sha(out / name) != manifest.get(key):
            errors.append(f'{out.name}: frozen {name} differs or identity missing')
    if fingerprint(out / 'workspace') != manifest.get('before'):
        errors.append(f'{out.name}: frozen workspace differs')
    if manifest.get('adapter_sha256') != sha(Path(__file__)):
        errors.append(f'{out.name}: adapter version differs; prepare a new pair')
    if manifest.get('legacy_harness_sha256') != sha(LEGACY):
        errors.append(f'{out.name}: runner version differs')
    provider = manifest.get('provider')
    if provider not in ('codex', 'claude'):
        errors.append(f'{out.name}: unknown provider')
        return errors
    config = Path.home() / ('.codex/config.toml' if provider == 'codex' else '.claude/settings.json')
    if not config.is_file() or sha(config) != manifest.get('native_config_sha256'):
        errors.append(f'{out.name}: native config differs')
    if native_capability_files(provider) != manifest.get('native_capability_files'):
        errors.append(f'{out.name}: local native capability inventory differs or missing')
    if manifest.get('command') != build_command(out, manifest):
        errors.append(f'{out.name}: launch command differs from declared controls')
    return errors


def comparable_command(manifest, out):
    command = manifest['command'][:]
    for i, arg in enumerate(command):
        if i and command[i - 1] == '--session-id':
            command[i] = '<SESSION>'
        elif (manifest['comparison'] == 'deployment' and i
              and command[i - 1] in ('--tools', '--allowedTools')):
            command[i] = '<DECLARED_CAPABILITIES>'
        else:
            command[i] = arg.replace(str(out), '<RUN>')
    return command


def audit_pair(baseline, workflow):
    """Check comparability, not scientific acceptance, spending authority or savings."""
    baseline, workflow = Path(baseline).resolve(), Path(workflow).resolve()
    result = {'controls_match': False, 'errors': [], 'declared_capability_differences': [],
              'savings_claim_supported': False,
              'limitations': ['not evidence of implementation or review benefit',
                              'scriptable extraction cannot establish helper break-even by file count',
                              'runtime context/cache may vary despite matched declared controls',
                              'local inventory excludes plugin contents, builtins and remote catalogs; effective capability validation is required before causal claims',
                              'session usage excludes unmeasured setup/coordinator/review cost']}
    try:
        a, b = [json.loads((p / 'manifest.json').read_text()) for p in (baseline, workflow)]
        if a.get('arm') != 'baseline' or b.get('arm') != 'workflow' or baseline == workflow:
            raise ValueError('expected distinct baseline and workflow preparations')
        mode = a.get('comparison')
        if mode not in ('routing', 'deployment') or b.get('comparison') != mode:
            raise ValueError('missing or unequal comparison type; legacy trials remain historical')
        result['question'] = ('workflow use with matched capabilities' if mode == 'routing'
                              else 'capability deployment overhead')
        keys = ('provider', 'task', 'model_requested', 'effort_requested', 'timeout_s',
                'base_prompt_sha256', 'truth_sha256', 'schema_sha256', 'adapter_sha256',
                'legacy_harness_sha256', 'native_config_sha256', 'native_capability_files', 'envelope')
        for key in keys:
            if key not in a or key not in b or a[key] != b[key]:
                result['errors'].append(f'control differs or missing: {key}')
        for path, manifest in ((baseline, a), (workflow, b)):
            result['errors'].extend(frozen_errors(path, manifest))
            if manifest['provider'] == 'claude':
                for flag in ('--tools', '--allowedTools'):
                    actual = manifest['command'][manifest['command'].index(flag) + 1]
                    expected = toolset(manifest['arm'], mode)
                    if actual != expected:
                        result['errors'].append(f'{manifest["arm"]}: unexpected {flag} set')
        if comparable_command(a, baseline) != comparable_command(b, workflow):
            result['errors'].append('effective launch command controls differ')
        def payload(manifest):
            return {k: v for k, v in manifest['before'].items()
                    if not k.startswith(('.agents/skills/', '.claude/skills/'))}
        if payload(a) != payload(b):
            result['errors'].append('task workspace/guidance differs')
        if mode == 'routing' and a['before'] != b['before']:
            result['errors'].append('skill/catalog availability differs in matched routing comparison')
        if mode == 'deployment':
            result['declared_capability_differences'] = ['local workflow skill snapshot']
            if a['provider'] == 'claude':
                result['declared_capability_differences'].append('Agent and Skill tool availability')
        result['controls_match'] = not result['errors']
    except (OSError, ValueError, TypeError, KeyError, IndexError) as exc:
        result['errors'].append(str(exc))
    return result


def prepare(args):
    out = Path(args.output).resolve()
    out.mkdir(parents=True, exist_ok=False)
    workspace = out / 'workspace'
    comparison = getattr(args, 'comparison', 'routing')
    if comparison not in ('routing', 'deployment'):
        raise ValueError('unknown comparison')
    prose = getattr(args, 'task', 'inventory') == 'prose'
    budget = getattr(args, 'budget_usd', 2)
    truth = build_prose_fixture(workspace) if prose else build_fixture(workspace)
    if truth != (prose_reference(workspace) if prose else reference(workspace)):
        raise ValueError('independent reference disagrees')
    write(out / 'truth.json', truth)
    write(out / 'schema.json', SCHEMA)
    (workspace / 'AGENTS.md').write_text(SCOPE + '\n')
    (workspace / 'CLAUDE.md').write_text('@AGENTS.md\n')
    if comparison == 'routing' or args.arm == 'workflow':
        shutil.copytree(ROOT / 'skill/scientific-workflow', workspace / '.agents/skills/scientific-workflow')
        shutil.copytree(ROOT / 'skill/scientific-workflow', workspace / '.claude/skills/scientific-workflow')
    intervention = ('Use $scientific-workflow. Zero or one native scientific_explorer support call is '
                    'permitted only if it saves substantial owner work. No other delegate, no reviewer, '
                    'no helper delegation. Direct tools and choosing no helper are valid. '
                    if args.arm == 'workflow' else
                    'Use one main execution owner and direct tools. Do not invoke skills or delegates. ')
    prompt = SCOPE + intervention + (PROSE_TASK if prose else TASK) + '\n'
    (out / 'prompt.txt').write_text(prompt)
    sid = str(uuid.uuid4())
    manifest = {'provider': args.provider, 'arm': args.arm, 'session_id_requested': sid,
                'comparison': comparison, 'task': 'prose' if prose else 'inventory',
                'base_prompt_sha256': hashlib.sha256((SCOPE + (PROSE_TASK if prose else TASK)).encode()).hexdigest(),
                'schema_sha256': sha(out / 'schema.json'),
                'cost_scope': 'session only; setup, coordinator and external review remain unmeasured',
                'timeout_s': 300, 'model_requested': 'gpt-6.1-sol' if args.provider == 'codex' else 'opus',
                'effort_requested': 'high', 'scientific_execution': False, 'before': fingerprint(workspace),
                'prompt_sha256': sha(out / 'prompt.txt'), 'adapter_sha256': sha(Path(__file__)),
                'legacy_harness_sha256': sha(LEGACY), 'truth_sha256': sha(out / 'truth.json'),
                'native_config_sha256': sha(Path.home() / ('.codex/config.toml' if args.provider == 'codex' else '.claude/settings.json')),
                'native_capability_files': native_capability_files(args.provider),
                'envelope': {'top_level_start_cap': 4, 'optional_support_start_cap_total': 2,
                             'per_session_deadline_s': 300, 'max_support_per_workflow': 1,
                             'codex_hard_dollar_limit': 'not_available', 'claude_cli_budget_usd': budget,
                             'call_caps': 'declared; Codex max_threads and depth constrain concurrency/depth, not total starts'},
                'runtime_differences': ['synthetic scratch cwd', 'read-only task; no writes',
                                        'memory/web/MCP disabled where supported', 'Claude hooks disabled; user agents/auth retained',
                                        'Codex direct process (--no-daemon); native user config retained',
                                        'routing mode matches tool/skill availability; deployment mode measures declared capability differences',
                                        'baseline explicitly declines skill/delegates; installed global catalogs may remain visible in both arms',
                                        'permissions differ across runtimes; compare within runtime only']}
    manifest['command'] = build_command(out, manifest)
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
    parsed = {}
    for thread, name, _ in candidates:
        if Path(name).is_file():
            trace = events(Path(name))
            meta = next((e.get('payload', {}) for e in trace if e.get('type') == 'session_meta'), {})
            source = meta.get('source', {})
            parent = meta.get('parent_thread_id')
            if isinstance(source, dict):
                parent = parent or source.get('subagent', {}).get('thread_spawn', {}).get('parent_thread_id')
            parsed[thread] = (name, trace, parent)
    owned = {sid}
    for _ in range(2):
        owned.update(thread for thread, (_, _, parent) in parsed.items() if parent in owned)
    result = []
    dest = out / 'native'
    dest.mkdir(exist_ok=True)
    for thread in sorted(owned & parsed.keys()):
        name, trace, _ = parsed[thread]
        shutil.copyfile(name, dest / f'{thread}.jsonl')
        result.append(trace)
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


def run(out, peer=None):
    if peer is None:
        raise ValueError('run requires --peer for a matched preparation; this check does not authorize inference')
    out, peer = Path(out).resolve(), Path(peer).resolve()
    manifest = json.loads((out / 'manifest.json').read_text())
    baseline, workflow = (out, peer) if manifest.get('arm') == 'baseline' else (peer, out)
    pair = audit_pair(baseline, workflow)
    if not pair['controls_match']:
        raise ValueError('pair preflight failed: ' + '; '.join(pair['errors']))
    if (peer / 'trace.jsonl').exists():
        if not (peer / 'execution.json').exists():
            raise ValueError('peer has no terminal receipt; inspect its owned execution before proceeding')
        terminal = json.loads((peer / 'execution.json').read_text())
        if terminal.get('returncode') != 0 or terminal.get('timed_out'):
            raise ValueError('peer failed; preserve the affected comparison without an automatic further start')
        if not (peer / 'metrics.json').exists():
            raise ValueError('peer capture is incomplete; wait for its terminal metrics')
        checks = json.loads((peer / 'metrics.json').read_text()).get('checks', {})
        for name in ('terminal_success', 'workspace_unchanged', 'usage_present', 'support_cap'):
            if checks.get(name) is not True:
                raise ValueError(f'peer boundary/telemetry check failed: {name}')
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
    parser.add_argument('action', choices=['prepare', 'check-pair', 'run'])
    parser.add_argument('--provider', choices=['codex', 'claude'])
    parser.add_argument('--arm', choices=['baseline', 'workflow'])
    parser.add_argument('--comparison', choices=['routing', 'deployment'], default='routing')
    parser.add_argument('--peer', help='Other frozen arm; required by check-pair and run')
    parser.add_argument('--task', choices=['inventory', 'prose'], default='inventory')
    parser.add_argument('--budget-usd', type=float, default=2)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    if args.action == 'prepare':
        if not args.provider or not args.arm:
            parser.error('prepare requires provider and arm')
        print(prepare(args))
    elif args.action == 'check-pair':
        if not args.peer:
            parser.error('check-pair requires --peer')
        out = Path(args.output).resolve()
        arm = json.loads((out / 'manifest.json').read_text()).get('arm')
        result = audit_pair(out, args.peer) if arm == 'baseline' else audit_pair(args.peer, out)
        print(json.dumps(result, indent=2))
        raise SystemExit(0 if result['controls_match'] else 1)
    else:
        run(Path(args.output).resolve(), args.peer)


if __name__ == '__main__':
    main()
