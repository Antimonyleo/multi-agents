#!/usr/bin/env python3
"""Narrow native extraction pilot. No scientific execution or configuration edits."""
import argparse
import collections
import hashlib
import importlib.util
import json
import re
from pathlib import Path
import shutil
import sqlite3
import uuid

ROOT = Path(__file__).resolve().parents[1]
LEGACY = Path('/home/hao/githubrepo/sequence_design/tools/workflow_evaluation/run.py')
PERMISSION_COMMAND = 'printf WORKFLOW_PERMISSION_PROBE'
PERMISSION_RULE = 'Bash(' + PERMISSION_COMMAND + ')'
SCOPE = ('This is a synthetic read-only fixture task. Access only this '
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
                    value = json.loads(line)
                    if not isinstance(value, dict):
                        raise ValueError('event must be an object')
                    result.append(value)
                except ValueError as exc:
                    raise ValueError(f'malformed JSONL {path.name}:{n}') from exc
    return result


def valid_usage(provider, value):
    required = ('input_tokens', 'output_tokens')
    optional = ('cached_input_tokens', 'cache_write_input_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens', 'reasoning_output_tokens', 'total_tokens')
    return (isinstance(value, dict) and all(type(value.get(k)) is int and value[k] >= 0 for k in required)
            and all(type(value[k]) is int and value[k] >= 0 for k in optional if k in value))


def parent_id(meta):
    parent = meta.get('parent_thread_id')
    source = meta.get('source')
    if isinstance(source, str):
        try:
            source = json.loads(source)
        except ValueError:
            source = None
    if isinstance(source, dict):
        sub = source.get('subagent')
        spawn = sub.get('thread_spawn') if isinstance(sub, dict) else None
        if isinstance(spawn, dict):
            parent = parent or spawn.get('parent_thread_id')
    return parent if isinstance(parent, str) and parent else None


def delegation_check(arm, metrics, children=None):
    calls = metrics['delegate_calls']
    children = metrics['native_children'] if children is None else children
    errors = list(metrics.get('tool_fragment_conflicts', []))
    cap = 1 if arm == 'workflow' else 0
    if len(calls) > cap or len(children) > cap:
        errors.append('support start cap exceeded')
    ids = [c.get('tool_use_id') or c.get('id') for c in calls]
    if any(not isinstance(i, str) or not i for i in ids) or len(set(ids)) != len(ids):
        errors.append('delegate identity missing or duplicated')
    if any(c.get('role') != 'scientific_explorer' for c in calls):
        errors.append('unauthorized or unresolved requested role')
    if any(c.get('parent_tool_use_id') for c in calls):
        errors.append('nested helper attempt')
    if len(calls) != len(children):
        errors.append('tool starts and native children do not reconcile')
    child_ids = [c.get('id') for c in children]
    if any(not isinstance(i, str) or not i for i in child_ids) or len(set(child_ids)) != len(child_ids):
        errors.append('native child identity missing or duplicated')
    for child in children:
        if child.get('role') != 'scientific_explorer' or child.get('depth') != 1:
            errors.append('native role or depth unverified')
        linked = child.get('parent_tool_use_id') in ids or child.get('id') in [c.get('child_id') for c in calls]
        if not linked:
            errors.append('native child/start identity linkage unresolved')
    return {'verified': not errors, 'errors': errors, 'unique_starts': len(ids), 'native_child_count': len(children)}


def codex_usage_details(trace):
    """Preserve compaction/record telemetry without replacing provider accounting."""
    records = [e.get('payload', {}) for e in trace if e.get('type') == 'token_usage_record']
    compactions = [e.get('payload', {}).get('compaction_response_id') for e in trace
                   if e.get('type') == 'compacted']
    last = records[-1].get('thread_token_usage') if records else None
    usage = {}
    conflicts = set()
    for record in records:
        ident = record.get('response_id')
        if type(ident) is not str or not ident:
            continue
        value = record.get('usage')
        if not valid_usage('codex', value):
            conflicts.add(ident)
        if ident in usage and usage[ident] != value:
            conflicts.add(ident)
        usage[ident] = value
    complete = bool(compactions) and all(
        type(ident) is str and bool(ident) and ident not in conflicts
        and valid_usage('codex', usage.get(ident)) for ident in compactions)
    return {'usage_last_record_cumulative': last if valid_usage('codex', last) else None,
            'compaction_response_usage': {ident: usage[ident] for ident in compactions} if complete else None,
            'compaction_usage_complete': complete if compactions else None}


def normalize(provider, stream, native=None):
    """Keep provider accounting separate; unknown child semantics never mean zero."""
    native = native or []
    tools = collections.Counter()
    delegates = []
    usage = None
    observed = set()
    result = None
    provider_failed = False
    responses = {}
    missing_response_id = False
    seen_tools = set()
    tool_fragments = {}
    fragment_conflicts = []
    for e in stream:
        if provider == 'codex':
            if e.get('type') in ('error', 'turn.failed'):
                provider_failed = True
            if e.get('type') == 'turn.completed':
                usage = e.get('usage')
            item = e.get('item', {})
            if e.get('type') == 'item.completed':
                if item.get('id') in seen_tools:
                    if tool_fragments.get(item.get('id')) != item:
                        fragment_conflicts.append('conflicting repeated tool identity: ' + str(item.get('id')))
                    continue
                if item.get('id'):
                    seen_tools.add(item['id'])
                    tool_fragments[item['id']] = item
                tools[item.get('type', 'unknown')] += 1
                if item.get('type') == 'collab_tool_call' and item.get('tool') == 'spawn_agent':
                    delegates.append({**item, 'role': item.get('agent_type') or item.get('role') or item.get('arguments', {}).get('agent_type'),
                                      'child_id': next(iter(item.get('receiver_thread_ids', [])), None)})
        else:
            if e.get('type') == 'result':
                result = e
                usage = e.get('usage')
            m = e.get('message', {})
            # Native permission notifications use a plain-text system message.
            # They carry no assistant usage or tool result evidence.
            if e.get('type') == 'system' and isinstance(m, str):
                continue
            if not isinstance(m, dict):
                raise ValueError('unsupported native message shape')
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
                        if tool_fragments.get(c.get('id')) != c:
                            fragment_conflicts.append('conflicting repeated tool identity: ' + str(c.get('id')))
                        continue
                    if c.get('id'):
                        seen_tools.add(c['id'])
                        tool_fragments[c['id']] = c
                    tools[c.get('name', 'unknown')] += 1
                    if c.get('name') in ('Agent', 'Task'):
                        delegates.append({'role': c.get('input', {}).get('subagent_type'),
                                          'tool_use_id': c.get('id'), 'input': c.get('input'),
                                          'parent_tool_use_id': e.get('parent_tool_use_id')})
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
                             **codex_usage_details(trace),
                             'model_contexts': [{'model': c.get('model'), 'effort': c.get('effort')} for c in contexts]})
        parent = parent_id(meta)
        if parent:
            children.append({'id': meta.get('id'), 'parent': parent, 'role': meta.get('agent_role'),
                             'models': sorted({c.get('model') for c in contexts if c.get('model')}),
                             'depth': None})
    parents = {c['id']: c['parent'] for c in children}
    for child in children:
        depth, ancestor, seen = 1, child['parent'], {child['id']}
        while ancestor in parents and ancestor not in seen:
            seen.add(ancestor); ancestor = parents[ancestor]; depth += 1
        child['depth'] = depth if ancestor not in seen else None
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
            'provider_usage': usage, 'provider_telemetry_complete': valid_usage(provider, usage),
            'usable_provider_usage': usage if valid_usage(provider, usage) else None, 'provider_result_model_usage': (result or {}).get('modelUsage'),
            'provider_reported_cost_usd': (result or {}).get('total_cost_usd'),
            'provider_terminal_complete': type((result or {}).get('is_error')) is bool if provider == 'claude' else usage is not None,
            'provider_error': (result or {}).get('is_error') if provider == 'claude' else provider_failed,
            'tool_fragment_conflicts': fragment_conflicts,
            'observed_models': sorted(observed), 'tools': dict(tools), 'delegate_calls': delegates,
            'native_children': children, 'thread_usage': thread_usage,
            'whole_family_accounting': 'unverified' if delegates or children else 'parent_only_no_delegate_observed',
            'net_cost_claim_supported': False,
            'accounting_note': 'Do not sum parent result totals and child transcripts; inclusion semantics unverified. Native event snapshots, record totals and compaction usage are separate evidence; do not add overlapping totals.'}


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
        settings = {'disableAllHooks': True}
        if manifest.get('permission_deny_rules'):
            settings['permissions'] = {'deny': manifest['permission_deny_rules']}
        command = ['claude', '-p', '--model', manifest['model_requested'], '--effort', manifest['effort_requested'], '--session-id', manifest['session_id_requested'],
                   '--setting-sources', 'user', '--settings', json.dumps(settings, separators=(',', ':')),
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
    if manifest.get('task') == 'semantic' and manifest.get('semantic_fixture_sha256') != sha(ROOT / 'scripts/semantic_fixture.py'):
        errors.append(f'{out.name}: semantic fixture version differs')
    if manifest.get('adapter_sha256') != sha(Path(__file__)):
        errors.append(f'{out.name}: adapter version differs; prepare a new pair')
    if manifest.get('legacy_harness_sha256') != sha(LEGACY):
        errors.append(f'{out.name}: runner version differs')
    provider = manifest.get('provider')
    if provider not in ('codex', 'claude'):
        errors.append(f'{out.name}: unknown provider')
        return errors
    expected_rules = [PERMISSION_RULE] if provider == 'claude' else []
    if manifest.get('permission_deny_rules') != expected_rules:
        errors.append(f'{out.name}: declared permission rules differ')
    expected_probe = ({'command': PERMISSION_COMMAND, 'read_path': 'inventory/group_00/component_000.json'}
                      if manifest.get('purpose') == 'capture_qualification' and provider == 'claude' else None)
    if manifest.get('permission_probe') != expected_probe:
        errors.append(f'{out.name}: declared permission probe differs')
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
                'base_prompt_sha256', 'semantic_fixture_sha256', 'purpose', 'truth_sha256', 'schema_sha256', 'adapter_sha256',
                'legacy_harness_sha256', 'native_config_sha256', 'native_capability_files', 'envelope', 'permission_deny_rules', 'permission_probe')
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


def semantic_module():
    spec = importlib.util.spec_from_file_location('semantic_fixture', ROOT / 'scripts/semantic_fixture.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def prepare(args):
    out = Path(args.output).resolve()
    out.mkdir(parents=True, exist_ok=False)
    workspace = out / 'workspace'
    comparison = getattr(args, 'comparison', 'routing')
    if comparison not in ('routing', 'deployment'):
        raise ValueError('unknown comparison')
    task = getattr(args, 'task', 'inventory')
    prose = task == 'prose'
    semantic = semantic_module() if task == 'semantic' else None
    qualification = getattr(args, 'qualification', False)
    budget = getattr(args, 'budget_usd', 2)
    truth = semantic.build(workspace) if semantic else (build_prose_fixture(workspace) if prose else build_fixture(workspace, count=1 if qualification else 96))
    if (semantic and not semantic.verify(workspace, truth)) or (not semantic and truth != (prose_reference(workspace) if prose else reference(workspace))):
        raise ValueError('independent reference disagrees')
    write(out / 'truth.json', truth)
    write(out / 'schema.json', semantic.SCHEMA if semantic else SCHEMA)
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
    base_task = semantic.TASK if semantic else (PROSE_TASK if prose else TASK)
    if qualification:
        intervention = ('First use Read yourself on inventory/group_00/component_000.json. '
                        'Then attempt exactly one Bash tool call with command "' + PERMISSION_COMMAND +
                        '". This harmless command is deliberately denied by a session-only rule; '
                        'a runtime denial is the expected outcome. Do not change the command, '
                        'retry, use a wrapper or request approval. After denial, '
                        'call exactly one native scientific_explorer. Give it the mechanical task '
                        'of reading the one inventory JSON and returning its selected record. '
                        'Integrate its reply. No other role or nested helper. ')
    elif semantic and args.arm == 'workflow':
        intervention = 'Call exactly one native scientific_explorer for this bounded mechanical assignment. Do not inspect its assigned files yourself unless its return has a concrete discrepancy. ' + semantic.HELPER_ASSIGNMENT + ' No other role or nested helper. '
    prompt = SCOPE + intervention + base_task + '\n'
    (out / 'prompt.txt').write_text(prompt)
    sid = str(uuid.uuid4())
    manifest = {'provider': args.provider, 'arm': args.arm, 'session_id_requested': sid,
                'comparison': comparison, 'task': task, 'purpose': 'capture_qualification' if qualification else 'comparison',
                'permission_deny_rules': [PERMISSION_RULE] if args.provider == 'claude' else [],
                'permission_probe': {'command': PERMISSION_COMMAND,
                                     'read_path': 'inventory/group_00/component_000.json'} if qualification and args.provider == 'claude' else None,
                'semantic_fixture_sha256': sha(ROOT / 'scripts/semantic_fixture.py') if semantic else None,
                'base_prompt_sha256': hashlib.sha256((SCOPE + base_task).encode()).hexdigest(),
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
    errors, candidates, conflicts = [], {}, set()
    if not sid:
        write(out / 'native_capture.json', {'complete': False, 'errors': ['missing parent thread identity']})
        return []
    for db in (Path.home() / '.codex').glob('state_*.sqlite'):
        con = sqlite3.connect(f'file:{db}?mode=ro', uri=True)
        try:
            rows = con.execute('select id, rollout_path, source from threads').fetchall()
            for thread, name, source in rows:
                parent = parent_id({'source': source})
                # Inspect metadata only to establish ownership; do not export unrelated sessions.
                meta = {}
                if isinstance(name, str) and Path(name).is_file():
                    with Path(name).open() as handle:
                        for line in handle:
                            try:
                                event = json.loads(line)
                            except ValueError:
                                break
                            if isinstance(event, dict) and event.get('type') == 'session_meta':
                                meta = event.get('payload', {}); break
                if not isinstance(meta, dict):
                    meta = {}
                parent = parent_id(meta) or parent
                candidate = (name, parent, meta.get('id'))
                if thread in candidates and candidates[thread] != candidate:
                    conflicts.add(thread)
                candidates[thread] = candidate
        finally:
            con.close()
    owned = {sid}
    while True:
        expanded = owned | {thread for thread, (_, parent, _) in candidates.items() if parent in owned}
        if expanded == owned:
            break
        owned = expanded
    errors.extend('conflicting candidate identity: ' + str(thread) for thread in sorted(owned & conflicts))
    result = []
    dest = out / 'native'; dest.mkdir(exist_ok=True)
    for thread in sorted(owned):
        if thread not in candidates:
            errors.append('missing descendant transcript: ' + thread); continue
        name, _, ident = candidates[thread]
        if ident != thread or not isinstance(name, str) or not Path(name).is_file():
            errors.append('missing or mismatched descendant transcript: ' + thread); continue
        try:
            trace = events(Path(name))
        except ValueError as exc:
            errors.append(str(exc)); continue
        shutil.copyfile(name, dest / f'{thread}.jsonl')
        result.append(trace)
    write(out / 'native_capture.json', {'complete': not errors, 'errors': errors, 'owned_ids': sorted(owned)})
    return result


def collect_claude(out, sid):
    dest = out / 'native'; dest.mkdir(exist_ok=True)
    collected, errors, parents = [], [], []
    for project in (Path.home() / '.claude/projects').glob('*'):
        parent = project / f'{sid}.jsonl'
        if parent.is_file():
            parents.append(parent)
            shutil.copyfile(parent, dest / 'parent.jsonl')
        folder = project / sid / 'subagents'
        if folder.is_dir():
            for path in sorted(folder.glob('agent-*.jsonl')):
                meta_path = path.with_suffix('.meta.json')
                meta = json.loads(meta_path.read_text()) if meta_path.is_file() else {}
                if not isinstance(meta, dict):
                    raise ValueError('malformed child metadata')
                trace = events(path)
                ident = path.stem.removeprefix('agent-')
                if any(t['id'] == ident for t in collected):
                    errors.append('duplicate child transcript: ' + ident)
                    continue
                shutil.copyfile(path, dest / path.name)
                if meta_path.exists(): shutil.copyfile(meta_path, dest / meta_path.name)
                collected.append({'file': path.name, 'id': ident, 'role': meta.get('agentType'),
                                  'parent_tool_use_id': meta.get('parentToolUseId') or meta.get('parent_tool_use_id'),
                                  'depth': 1, 'events': trace})
    if len(parents) != 1:
        errors.append('missing or duplicated parent transcript')
    if parents:
        for event in events(parents[0]):
            for content in event.get('message', {}).get('content', []) or []:
                if isinstance(content, dict) and content.get('type') == 'tool_result':
                    text = content.get('content')
                    if not isinstance(text, str): text = json.dumps(text)
                    match = re.search(r'agentId:\s*([A-Za-z0-9_-]+)', text)
                    if match:
                        for child in collected:
                            if child['id'] == match.group(1):
                                child['parent_tool_use_id'] = content.get('tool_use_id')
    for child in collected:
        # A nested request is invalid even if the child CLI never started it.
        if normalize('claude', child['events'])['delegate_calls']:
            child['depth'] = 2
    write(out / 'native_capture.json', {'complete': not errors, 'errors': errors})
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
    if any((peer / name).exists() for name in ('trace.jsonl', 'execution.json', 'metrics.json')):
        try:
            terminal = json.loads((peer / 'execution.json').read_text())
            checks = json.loads((peer / 'metrics.json').read_text()).get('checks', {})
        except (OSError, ValueError, AttributeError) as exc:
            raise ValueError('peer capture is incomplete or malformed; preserve its receipt') from exc
        if not isinstance(terminal, dict) or type(terminal.get('returncode')) is not int or terminal['returncode'] != 0 or terminal.get('timed_out') is not False:
            raise ValueError('peer failed; preserve the affected comparison without an automatic further start')
        for name in ('terminal_success', 'workspace_unchanged', 'usage_present', 'support_cap',
                     'cleanup_verified', 'capture_complete', 'exact_output'):
            if not isinstance(checks, dict) or checks.get(name) is not True:
                raise ValueError(f'peer boundary/telemetry check failed: {name}')
        if not isinstance(terminal.get('cleanup'), dict) or terminal['cleanup'].get('verified') is not True:
            raise ValueError('peer cleanup unverified')
    if any((out / name).exists() for name in ('execution.json', 'trace.jsonl', 'metrics.json')):
        raise ValueError('refusing unchanged retry; preserve previous receipt')
    execute(out, manifest)


def run_qualification(out):
    out = Path(out).resolve()
    manifest = json.loads((out / 'manifest.json').read_text())
    if manifest.get('purpose') != 'capture_qualification' or manifest.get('arm') != 'workflow':
        raise ValueError('not a frozen capture qualification')
    errors = frozen_errors(out, manifest)
    if errors: raise ValueError('qualification preflight failed: ' + '; '.join(errors))
    if any((out / name).exists() for name in ('execution.json', 'trace.jsonl', 'metrics.json')):
        raise ValueError('refusing qualification retry')
    execute(out, manifest)


def execute(out, manifest):
    spec = importlib.util.spec_from_file_location('legacy_workflow_harness', LEGACY)
    legacy = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(legacy)
    # Reuse existing finite timeout/process-group runner, not another orchestrator.
    failure = None
    try:
        legacy.run(out, manifest)
    except Exception as exc:
        failure = f'runner failed: {type(exc).__name__}: {exc}'
    capture(out, manifest, failure)


def permission_probe(stream, workspace, declaration):
    """Correlate exact tool attempts with native results, never model assertions.

    This proves one scoped parent rule only. Missing/unsupported evidence is
    unknown; a successfully executed forbidden command is an observed failure.
    """
    result = {'allowed_read': False, 'denied_attempts': 0,
              'denied_enforcement': False, 'unexpected_success': False,
              'status': 'unverified', 'scope': 'one exact parent Bash rule'}
    if (not isinstance(declaration, dict) or type(declaration.get('command')) is not str
            or type(declaration.get('read_path')) is not str):
        return result
    calls, replies, decisions = {}, {}, {}
    conflicts = set()
    for event in stream:
        if not isinstance(event, dict):
            return result
        if event.get('parent_tool_use_id'):
            continue
        message = event.get('message', {})
        if event.get('type') == 'system' and isinstance(message, str):
            continue
        if not isinstance(message, dict) or not isinstance(message.get('content', []), list):
            return result
        for block in message.get('content', []):
            if not isinstance(block, dict):
                continue
            ident = block.get('id') if block.get('type') == 'tool_use' else block.get('tool_use_id')
            if not isinstance(ident, str) or not ident:
                continue
            table = (calls if block.get('type') == 'tool_use' and event.get('type') == 'assistant'
                     else replies if block.get('type') == 'tool_result' and event.get('type') == 'user' else None)
            if table is not None:
                if ident in table and table[ident] != block:
                    conflicts.add(ident)
                table[ident] = block
        metadata = event.get('tool_result_meta', [])
        if not isinstance(metadata, list):
            return result
        for meta in metadata:
            if event.get('type') != 'user':
                return result
            if isinstance(meta, dict) and isinstance(meta.get('id'), str):
                decision = meta.get('permission_decision', {})
                if not isinstance(decision, dict):
                    return result
                if meta['id'] in decisions and decisions[meta['id']] != decision:
                    conflicts.add(meta['id'])
                decisions[meta['id']] = decision
    finals = [e for e in stream if e.get('type') == 'result']
    denials = finals[-1].get('permission_denials', []) if finals else []
    if not isinstance(denials, list):
        return result
    expected_read = (workspace / declaration['read_path']).resolve()
    denied_ids = []
    for ident, call in calls.items():
        if ident in conflicts:
            continue
        reply = replies.get(ident, {})
        inputs = call.get('input', {})
        if not isinstance(inputs, dict):
            return result
        if call.get('name') == 'Read' and isinstance(inputs.get('file_path'), str):
            path = Path(inputs['file_path'])
            path = path if path.is_absolute() else workspace / path
            content = reply.get('content')
            usable_content = ((isinstance(content, str) and bool(content.strip()))
                              or (isinstance(content, list) and any(isinstance(b, dict)
                                  and b.get('type') == 'text' and isinstance(b.get('text'), str)
                                  and bool(b['text'].strip()) for b in content)))
            if (path.resolve() == expected_read and usable_content and reply.get('is_error', False) is False
                    and decisions.get(ident, {}).get('decision') not in ('deny', 'reject')):
                result['allowed_read'] = True
        if call.get('name') != 'Bash' or inputs.get('command') != declaration['command']:
            continue
        denied_ids.append(ident)
        if reply and reply.get('is_error', False) is False:
            result['unexpected_success'] = True
        native_denial = False
        for denial in denials:
            if not isinstance(denial, dict):
                return result
            denial_input = denial.get('tool_input', denial.get('input', {}))
            if not isinstance(denial_input, dict):
                return result
            if (denial.get('tool_name') == 'Bash' and denial.get('tool_use_id') == ident
                    and denial_input.get('command') == declaration['command']):
                native_denial = True
        decision = decisions.get(ident, {})
        rule_denial = (decision.get('decision') in ('deny', 'reject')
                       and decision.get('source') == 'config'
                       and decision.get('reason_type') == 'rule')
        if reply.get('is_error') is True and (native_denial or rule_denial) and decision.get('decision') != 'accept':
            result['denied_enforcement'] = True
    result['denied_attempts'] = len(denied_ids)
    if result['unexpected_success']:
        result['denied_enforcement'] = False
        result['status'] = 'failed'
    elif result['allowed_read'] and len(denied_ids) == 1 and result['denied_enforcement'] and not conflicts:
        result['status'] = 'verified'
    return result


def capture(out, manifest, failure=None):
    """Always leave a terminal incomplete record when native capture cannot be parsed."""
    errors = [failure] if failure else []
    execution, stream, traces, children = {}, [], [], []
    try:
        execution = json.loads((out / 'execution.json').read_text())
        if not isinstance(execution, dict): raise ValueError('receipt must be an object')
    except (OSError, ValueError) as exc:
        errors.append('missing or malformed execution receipt: ' + str(exc)); execution = {}
    metrics = normalize(manifest['provider'], [])
    try:
        if not (out / 'trace.jsonl').is_file(): raise ValueError('missing trace')
        stream = events(out / 'trace.jsonl')
        if not stream: raise ValueError('empty trace')
        if manifest['provider'] == 'codex':
            traces = collect_codex(out, stream)
        else:
            children = collect_claude(out, manifest['session_id_requested'])
        report = json.loads((out / 'native_capture.json').read_text())
        if report.get('complete') is not True: errors.extend(report.get('errors') or ['native capture incomplete'])
        metrics = normalize(manifest['provider'], stream, traces)
    except (OSError, ValueError, TypeError, AttributeError, KeyError, IndexError, sqlite3.Error) as exc:
        errors.append('native capture failed: ' + str(exc))
    if children:
        metrics['observed_models'] = sorted(set(metrics['observed_models']) | {e.get('message', {}).get('model') for t in children for e in t['events'] if e.get('message', {}).get('model')})
        metrics['claude_child_evidence'] = [{
            'file': t['file'], 'id': t['id'], 'role': t['role'], 'depth': t['depth'],
            'parent_tool_use_id': t['parent_tool_use_id'],
            'models': sorted({e.get('message', {}).get('model') for e in t['events'] if e.get('message', {}).get('model')}),
            'usage_raw': [e['message']['usage'] for e in t['events'] if e.get('message', {}).get('usage')],
        } for t in children]
        metrics['whole_family_accounting'] = 'unverified'
    boundary = delegation_check(manifest['arm'], metrics, children if manifest['provider'] == 'claude' else None)
    if manifest.get('purpose') == 'capture_qualification' and boundary['unique_starts'] != 1:
        boundary['verified'] = False
        boundary['errors'].append('qualification requires exactly one allowed helper')
    answer = None
    try:
        if manifest['provider'] == 'claude':
            final = next((e for e in reversed(stream) if e.get('type') == 'result'), {})
            answer = final.get('structured_output')
            if answer is None:
                try: answer = json.loads(final.get('result', ''))
                except ValueError: pass
            if answer is not None: write(out / 'answer.json', answer)
        elif (out / 'answer.json').exists():
            answer = json.loads((out / 'answer.json').read_text())
    except (OSError, ValueError, TypeError) as exc:
        errors.append('answer parse failure: ' + str(exc))
    expected = json.loads((out / 'truth.json').read_text())
    cleanup = execution.get('cleanup', {})
    checks = {'exact_output': semantic_module().score(answer, expected, out / 'workspace') if manifest.get('task') == 'semantic' else score(answer, expected),
              'workspace_unchanged': fingerprint(out / 'workspace') == manifest['before'],
              'terminal_success': type(execution.get('returncode')) is int and execution['returncode'] == 0 and execution.get('timed_out') is False and metrics['provider_terminal_complete'] and metrics['provider_error'] is False,
              'usage_present': metrics['provider_telemetry_complete'],
              'support_cap': boundary['verified'],
              'cleanup_verified': isinstance(cleanup, dict) and cleanup.get('verified') is True and cleanup.get('status') in ('absent', 'terminated'),
              'capture_complete': not errors}
    if manifest.get('purpose') == 'capture_qualification':
        permissions = permission_probe(stream, out / 'workspace', manifest.get('permission_probe')) if manifest['provider'] == 'claude' else {'status': 'unverified'}
        metrics['qualification_gate'] = {
            'native_identity_observed': bool(metrics['observed_models']) and bool(children) and all(c.get('models') for c in metrics.get('claude_child_evidence', [])),
            'family_accounting': metrics['whole_family_accounting'],
            'effective_permissions': permissions,
            'accepted': False,
            'note': 'Capture checks do not establish inclusive accounting or effective permissions; independent native qualification evidence is required before comparison.'}
    write(out / 'metrics.json', {**metrics, 'checks': checks, 'quality_pass': all(checks.values()),
                                'execution_state': 'complete' if all(checks.values()) else 'incomplete',
                                'capture_errors': errors, 'delegation_boundary': boundary,
                                'execution': execution, 'cleanup': cleanup, 'scientific_execution': False})
    print(json.dumps({'output': str(out), 'checks': checks, 'wall_s': execution.get('wall_s'),
                      'delegates': len(metrics['delegate_calls']), 'observed_models': metrics['observed_models'],
                      'cost_usd_reported': metrics['provider_reported_cost_usd']}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['prepare', 'check-pair', 'run', 'prepare-qualification', 'run-qualification'])
    parser.add_argument('--provider', choices=['codex', 'claude'])
    parser.add_argument('--arm', choices=['baseline', 'workflow'])
    parser.add_argument('--comparison', choices=['routing', 'deployment'], default='routing')
    parser.add_argument('--peer', help='Other frozen arm; required by check-pair and run')
    parser.add_argument('--task', choices=['inventory', 'prose', 'semantic'], default='inventory')
    parser.add_argument('--budget-usd', type=float)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    if args.budget_usd is None:
        args.budget_usd = 0.4 if args.action == 'prepare-qualification' else 2
    if args.action == 'prepare-qualification':
        args.provider = args.provider or 'claude'
        args.arm = 'workflow'; args.qualification = True; args.task = 'inventory'
        print(prepare(args))
    elif args.action == 'run-qualification':
        run_qualification(Path(args.output).resolve())
    elif args.action == 'prepare':
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
