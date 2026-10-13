#!/usr/bin/env python3
"""Native behavioral fixture execution using the existing owned-group runner."""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import uuid

ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


native = module('native_calibration')
evidence = module('behavioral_evidence')


def command(out, manifest):
    args = native.build_command(out, manifest)
    scope = manifest['scope']
    if manifest['provider'] == 'claude':
        available = 'Read,Glob,Grep,Bash,Skill'
        if manifest['allowed_roles']:
            available += ',Agent'
        if manifest['writable']:
            available += ',Edit,Write'
        for flag in ('--tools', '--allowedTools'):
            args[args.index(flag) + 1] = available
        args[args.index('--append-system-prompt') + 1] = scope
    else:
        args[args.index('--sandbox') + 1] = 'workspace-write' if manifest['writable'] else 'read-only'
    return args


def prepare(out, case, provider='claude', budget=0.6, previous=None, stage=1):
    fixture = module('behavioral_fixture')
    out = Path(out).resolve()
    out.mkdir(parents=True, exist_ok=False)
    workspace = out / 'workspace'
    if previous:
        previous = Path(previous).resolve()
        prior_manifest = json.loads((previous / 'manifest.json').read_text())
        if (prior_manifest.get('case') != case or prior_manifest.get('provider') != provider
                or type(stage) is not int or prior_manifest.get('stage') != stage - 1):
            raise ValueError('stage predecessor differs')
        if not (previous / 'metrics.json').is_file():
            raise ValueError('stage predecessor has no terminal result')
        prior_metrics = json.loads((previous / 'metrics.json').read_text())
        checks = prior_metrics.get('checks')
        if (prior_metrics.get('accepted') is not True or not isinstance(checks, dict)
                or not checks or any(value is not True for value in checks.values())):
            raise ValueError('stage predecessor was not accepted')
        shutil.copytree(previous / 'workspace', workspace)
        prior_answer = json.loads((previous / 'answer.json').read_text()) if (previous / 'answer.json').is_file() else None
        obs = json.loads((previous / 'observations.json').read_text())
        built = fixture.advance(workspace, case, stage, prior_answer, obs)
    else:
        if type(stage) is not int or stage != 1:
            raise ValueError('first preparation must be stage 1')
        built = fixture.build(workspace, case)
    scope = ('Synthetic workflow evaluation only. Access this workspace, its local skill '
             'and native role definitions. Preserve unrelated projects, processes and '
             'global configuration. No memory, network, scientific execution or background jobs. '
             + ('Only the named fixture source modules may be edited. ' if built['writable']
                else 'This fixture is read-only; do not write files. '))
    native.write(out / 'schema.json', built['schema'])
    (workspace / 'AGENTS.md').write_text(scope + '\n')
    (workspace / 'CLAUDE.md').write_text('@AGENTS.md\n')
    for folder in ('.agents', '.claude'):
        target = workspace / folder / 'skills/scientific-workflow'
        if not target.exists():
            shutil.copytree(ROOT / 'skill/scientific-workflow', target)
    built['truth']['initial'] = native.fingerprint(workspace)
    native.write(out / 'truth.json', built['truth'])
    prompt = scope + 'Use scientific-workflow for this fixture. ' + built['prompt']
    (out / 'prompt.txt').write_text(prompt.rstrip() + '\n')
    manifest = {
        'provider': provider, 'arm': 'workflow', 'comparison': 'routing',
        'case': case, 'stage': stage, 'previous': str(previous) if previous else None,
        'purpose': 'behavioral', 'scope': scope,
        'writable': built['writable'], 'allowed_roles': built['allowed_roles'],
        'max_helpers': built['max_helpers'], 'timeout_s': 300,
        'session_id_requested': str(uuid.uuid4()),
        'model_requested': 'opus' if provider == 'claude' else 'gpt-6.1-sol',
        'effort_requested': 'high',
        'envelope': {'claude_cli_budget_usd': budget},
        'permission_deny_rules': [native.PERMISSION_RULE] if provider == 'claude' else [],
        'native_config_sha256': native.sha(Path.home() / ('.claude/settings.json' if provider == 'claude' else '.codex/config.toml')),
        'native_capability_files': native.native_capability_files(provider),
        'before': native.fingerprint(workspace),
        'input_hashes': {name: native.sha(out / name) for name in ('prompt.txt', 'schema.json', 'truth.json')},
        'source_hashes': {str(path): native.sha(path) for path in (
            ROOT / 'scripts/native_calibration.py', ROOT / 'scripts/behavioral_fixture.py',
            ROOT / 'scripts/behavioral_evidence.py',
            Path(__file__), native.LEGACY)},
        'runtime_version': subprocess.check_output([provider, '--version'], text=True).strip(),
        'scientific_execution': False,
        'cost_scope': 'this native family only; coordinator/external review and billing unknown',
    }
    manifest['command'] = command(out, manifest)
    native.write(out / 'manifest.json', manifest)
    return manifest


def frozen_errors(out, manifest):
    errors = []
    for name, digest in manifest['input_hashes'].items():
        if not (out / name).is_file() or native.sha(out / name) != digest:
            errors.append('input differs: ' + name)
    for name, digest in manifest['source_hashes'].items():
        if not Path(name).is_file() or native.sha(Path(name)) != digest:
            errors.append('source differs: ' + name)
    if native.fingerprint(out / 'workspace') != manifest['before']:
        errors.append('workspace differs')
    provider = manifest['provider']
    config = Path.home() / ('.claude/settings.json' if provider == 'claude' else '.codex/config.toml')
    if native.sha(config) != manifest['native_config_sha256']:
        errors.append('native config differs')
    if native.native_capability_files(provider) != manifest['native_capability_files']:
        errors.append('capability inventory differs')
    if manifest['command'] != command(out, manifest):
        errors.append('launch controls differ')
    if subprocess.check_output([provider, '--version'], text=True).strip() != manifest['runtime_version']:
        errors.append('runtime version differs')
    return errors


def observations(stream, children, manifest, after, owned_traces=None):
    calls, replies, conflicts = {}, {}, []
    child_links = {c.get('parent_tool_use_id'): c['id'] for c in children if c.get('parent_tool_use_id')}
    reply_actors = {}
    sources = [(stream, 'main')] + [(c.get('events', []), c['id']) for c in children]
    for trace, default_actor in sources:
        for event in trace:
            actor = event.get('agent_id') or child_links.get(event.get('parent_tool_use_id')) or default_actor
            message = event.get('message', {})
            if event.get('type') == 'system' and isinstance(message, str):
                continue
            if not isinstance(message, dict):
                conflicts.append('unsupported message shape')
                continue
            content = message.get('content', [])
            origin = event.get('type') or message.get('role')
            if isinstance(content, str) and origin in ('user', 'assistant'):
                # Native transcript assignment/text messages carry no tool data.
                continue
            if not isinstance(content, list):
                conflicts.append('unsupported content shape')
                continue
            for block in content:
                if not isinstance(block, dict):
                    continue
                if block.get('type') == 'tool_use':
                    ident = block.get('id')
                    if origin != 'assistant' or not isinstance(ident, str) or not ident:
                        conflicts.append('unsupported tool-use origin/identity')
                        continue
                    value = {'id': ident, 'name': block.get('name'), 'input': block.get('input', {}), 'actor': actor}
                    if ident in calls and calls[ident] != value:
                        conflicts.append(ident)
                    calls[ident] = value
                elif block.get('type') == 'tool_result':
                    ident = block.get('tool_use_id')
                    if origin != 'user' or not isinstance(ident, str) or not ident:
                        conflicts.append('unsupported tool-result origin/identity')
                        continue
                    reply = dict(block)
                    if isinstance(event.get('tool_use_result'), dict):
                        reply['native'] = event['tool_use_result']
                    if ident in replies:
                        prior = replies[ident]
                        if ({k:v for k,v in prior.items() if k!='native'} != {k:v for k,v in reply.items() if k!='native'}
                                or reply_actors[ident] != actor
                                or 'native' in prior and 'native' in reply and prior['native'] != reply['native']):
                            conflicts.append('conflicting tool result: ' + ident)
                        if 'native' in prior and 'native' not in reply:
                            reply['native'] = prior['native']
                    replies[ident] = reply
                    reply_actors[ident] = actor
            item = event.get('item', {})
            if event.get('type') == 'item.completed' and item.get('type') == 'command_execution':
                ident = item.get('id')
                calls[ident] = {'id': ident, 'name': 'Bash', 'input': {'command': item.get('command')}, 'actor': 'main'}
                replies[ident] = {'tool_use_id': ident, 'is_error': item.get('exit_code') != 0,
                                  'exit_code': item.get('exit_code'), 'content': item.get('aggregated_output', '')}
    tools = list(calls.values())
    for tool in tools:
        tool['result'] = replies.get(tool['id'])
        if tool['id'] in reply_actors and reply_actors[tool['id']] != tool['actor']:
            conflicts.append('cross-actor tool result: ' + tool['id'])
    unknowns = []
    if owned_traces is not None:
        frontend_tools = tools
        tools = []
        for trace in owned_traces:
            parsed, issues = evidence.native_tools(trace['events'], trace.get('actor', 'main'))
            tools.extend(parsed); unknowns.extend(issues)
    else:
        frontend_tools = []
    return {'tools': tools, 'helpers': [{k:v for k,v in c.items() if k!='events'} for c in children],
            'before': manifest['before'], 'after': after, 'tool_conflicts': conflicts,
            'evidence_unknowns': unknowns, 'frontend_tools': frontend_tools,
            'owner_ids': sorted({t['actor'] for t in tools if t['name'] in ('Edit','Write','Bash','exec_command')})}


def boundary(metrics, children, manifest):
    starts = metrics['delegate_calls']
    ids = [c.get('tool_use_id') or c.get('id') for c in starts]
    errors = list(metrics.get('tool_fragment_conflicts', []))
    if len(starts) > manifest['max_helpers'] or len(children) != len(starts):
        errors.append('helper cap or captured start count differs')
    if any(not isinstance(i, str) or not i for i in ids) or len(ids) != len(set(ids)):
        errors.append('helper identity missing/conflicting')
    child_ids = [child.get('id') for child in children]
    if any(not isinstance(i, str) or not i for i in child_ids) or len(child_ids) != len(set(child_ids)):
        errors.append('native child identity missing/conflicting')
    if any(c.get('role') not in manifest['allowed_roles'] or c.get('parent_tool_use_id') for c in starts):
        errors.append('unexpected or nested role')
    for child in children:
        if (child.get('role') not in manifest['allowed_roles'] or child.get('depth') != 1
                or not child.get('id') or not child.get('models')):
            errors.append('native child role/depth/model missing')
        if child.get('parent_tool_use_id') not in ids and child.get('id') not in [c.get('child_id') for c in starts]:
            errors.append('child linkage missing')
    return {'verified': not errors, 'errors': errors}


def run(out):
    out = Path(out).resolve()
    manifest = json.loads((out / 'manifest.json').read_text())
    if manifest.get('purpose') != 'behavioral':
        raise ValueError('not a behavioral fixture')
    if any((out / name).exists() for name in ('trace.jsonl','execution.json','metrics.json')):
        raise ValueError('refusing repeated behavioral start')
    errors = frozen_errors(out, manifest)
    if errors:
        raise ValueError('; '.join(errors))
    spec = importlib.util.spec_from_file_location('legacy', native.LEGACY)
    legacy = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(legacy)
    launch_failure = None
    try:
        legacy.run(out, manifest)
    except Exception as exc:
        launch_failure = f'{type(exc).__name__}: {exc}'
    capture(out, launch_failure)


def capture(out, launch_failure=None):
    """Assess saved terminal evidence without starting or retrying a model."""
    out = Path(out).resolve()
    manifest = json.loads((out / 'manifest.json').read_text())
    if not (out / 'execution.json').is_file() and not launch_failure:
        raise ValueError('capture requires terminal execution evidence')
    stream, children, traces = [], [], []
    capture_errors = [launch_failure] if launch_failure else []
    try:
        stream = native.events(out / 'trace.jsonl')
        if not stream:
            raise ValueError('empty trace')
        if manifest['provider'] == 'claude':
            children = native.collect_claude(out, manifest['session_id_requested'])
        else:
            traces = native.collect_codex(out, stream)
        report = json.loads((out / 'native_capture.json').read_text())
        if report.get('complete') is not True:
            capture_errors.extend(report.get('errors') or ['incomplete capture'])
    except Exception as exc:
        capture_errors.append(f'{type(exc).__name__}: {exc}')
    try:
        metrics = native.normalize(manifest['provider'], stream, traces)
    except (ValueError, TypeError, AttributeError, KeyError) as exc:
        capture_errors.append(f'normalization failed: {type(exc).__name__}: {exc}')
        metrics = native.normalize(manifest['provider'], [])
    if manifest['provider'] == 'codex':
        children = metrics['native_children']
    for child in children:
        if 'events' in child:
            child['models'] = sorted({e['message']['model'] for e in child['events']
                                      if isinstance(e.get('message'), dict) and e['message'].get('model')})
    obs = observations(stream, children, manifest, native.fingerprint(out / 'workspace'))
    execution = json.loads((out / 'execution.json').read_text()) if (out / 'execution.json').is_file() else {}
    obs['execution'] = execution
    answer = None
    if (out / 'answer.json').exists():
        try:
            answer = json.loads((out / 'answer.json').read_text())
        except ValueError as exc:
            capture_errors.append(f'answer failed: {exc}')
    elif manifest['provider'] == 'claude':
        finals = [e for e in stream if e.get('type')=='result']
        answer = finals[-1].get('structured_output') if finals else None
    fixture = module('behavioral_fixture')
    try:
        checks = fixture.score(manifest['case'], answer, json.loads((out / 'truth.json').read_text()), out / 'workspace', obs)
    except Exception as exc:
        capture_errors.append(f'score failed: {type(exc).__name__}: {exc}')
        checks = {'fixture_score': False}
    helper_boundary = boundary(metrics, children, manifest)
    cleanup = execution.get('cleanup', {})
    checks.update({
        'terminal_success': type(execution.get('returncode')) is int and execution['returncode'] == 0 and execution.get('timed_out') is False and metrics['provider_terminal_complete'] and metrics['provider_error'] is False,
        'capture_complete': not capture_errors and not obs['tool_conflicts'],
        'usage_present': metrics['provider_telemetry_complete'],
        'helper_boundary': helper_boundary['verified'],
        'owned_cleanup': cleanup.get('verified') is True and cleanup.get('status') in ('absent','terminated'),
    })
    native.write(out / 'observations.json', obs)
    native.write(out / 'metrics.json', {**metrics, 'checks': checks, 'accepted': all(checks.values()), 'capture_errors': capture_errors,
                                       'boundary': helper_boundary, 'execution': execution, 'scientific_execution': False})
    print(json.dumps({'case':manifest['case'], 'checks':checks, 'wall_s':execution.get('wall_s'),
                      'reported_cost_usd':metrics['provider_reported_cost_usd']}))


def replay(saved_stage, output_dir, owned_traces=None, *, run_hidden=False):
    """Pure supplemental replay. Never collect native traces or replace old files.

    owned_traces optionally lists {actor, events} records. Default Codex replay
    loads only copied native files listed by the saved owned_ids receipt. Missing
    owned evidence stays unknown. Hidden synthetic probes are opt-in, never science.
    Returns the assessment; output_dir must be a new directory outside saved_stage.
    """
    saved, output = Path(saved_stage).resolve(), Path(output_dir).resolve()
    if output == saved or saved in output.parents:
        raise ValueError('supplemental output must be outside frozen stage')
    names = ('manifest.json', 'truth.json', 'observations.json', 'answer.json', 'native_capture.json')
    source_hashes = {name: native.sha(saved / name) for name in names if (saved / name).is_file()}
    manifest = json.loads((saved / 'manifest.json').read_text())
    truth = json.loads((saved / 'truth.json').read_text())
    obs = json.loads((saved / 'observations.json').read_text())
    answer = json.loads((saved / 'answer.json').read_text()) if (saved / 'answer.json').is_file() else None
    if manifest['provider'] == 'codex':
        loaded = []
        if owned_traces is None:
            receipt = json.loads((saved / 'native_capture.json').read_text()) if (saved / 'native_capture.json').is_file() else {}
            ids = receipt.get('owned_ids', [])
            if not isinstance(ids, list):
                ids = []
            frozen_stream = saved / 'trace.jsonl'
            parent_id = None
            if frozen_stream.is_file():
                source_hashes['trace.jsonl'] = native.sha(frozen_stream)
                starts = [e for e in native.events(frozen_stream) if e.get('type') == 'thread.started']
                thread_ids = {e.get('thread_id') for e in starts if isinstance(e.get('thread_id'), str) and e['thread_id']}
                if len(thread_ids) == 1 and len(starts) == sum(isinstance(e.get('thread_id'), str) and bool(e['thread_id']) for e in starts):
                    parent_id = next(iter(thread_ids))
            if parent_id is None:
                obs.setdefault('evidence_unknowns', []).append('missing or ambiguous frozen parent thread identity')
            elif parent_id not in ids:
                obs.setdefault('evidence_unknowns', []).append('frozen parent thread absent from owned inventory')
            if receipt.get('complete') is not True or not ids:
                obs.setdefault('evidence_unknowns', []).append('owned native capture missing or incomplete')
            if len(ids) != len(set(str(i) for i in ids)):
                obs.setdefault('evidence_unknowns', []).append('duplicate owned trace identity')
            for ident in ids:
                if not isinstance(ident, str) or '/' in ident or '\\' in ident:
                    obs.setdefault('evidence_unknowns', []).append('invalid owned trace identity'); continue
                path = saved / 'native' / (ident + '.jsonl')
                if not path.is_file():
                    obs.setdefault('evidence_unknowns', []).append('missing owned trace: ' + ident); continue
                source_hashes[path.relative_to(saved).as_posix()] = native.sha(path)
                events = native.events(path)
                metas = [e for e in events if e.get('type') == 'session_meta']
                session_ids = {e.get('payload', {}).get('id') for e in metas if isinstance(e.get('payload'), dict)
                               and isinstance(e['payload'].get('id'), str)}
                identity_valid = bool(metas) and len(session_ids) == 1 and session_ids == {ident} and all(
                    isinstance(e.get('payload'), dict) and e['payload'].get('id') == ident for e in metas)
                if not identity_valid:
                    obs.setdefault('evidence_unknowns', []).append('missing or conflicting native session identity: ' + ident)
                actor = 'main' if identity_valid and ident == parent_id else ident
                loaded.append({'actor': actor, 'events': events})
            owned_traces = loaded
        original_tools = obs.get('tools', [])
        obs['tools'] = []
        for trace in owned_traces:
            parsed, issues = evidence.native_tools(trace['events'], trace.get('actor', 'main'))
            obs['tools'].extend(parsed)
            obs.setdefault('evidence_unknowns', []).extend(issues)
        obs['frontend_tools'] = original_tools
    fixture = module('behavioral_fixture')
    report = fixture.diagnose(manifest['case'], answer, truth, saved / 'workspace', obs, run_hidden=run_hidden)
    report.update({'case': manifest['case'], 'stage': manifest.get('stage', 1),
                   'source_stage': str(saved), 'originals_unchanged': True, 'input_hashes': source_hashes,
                   'scorer_hashes': {str(p.relative_to(ROOT)): native.sha(p) for p in (
                       Path(__file__), ROOT / 'scripts/behavioral_fixture.py', ROOT / 'scripts/behavioral_evidence.py')},
                   'hidden_probes_rerun': run_hidden})
    if any(native.sha(saved / name) != digest for name, digest in source_hashes.items()):
        raise ValueError('frozen replay input changed during assessment')
    output.mkdir(parents=True, exist_ok=False)
    native.write(output / 'supplemental-assessment.json', report)
    native.write(output / 'supplemental-observations.json', obs)
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['prepare','run'])
    parser.add_argument('--output',required=True)
    parser.add_argument('--case')
    parser.add_argument('--provider',choices=['claude','codex'],default='claude')
    parser.add_argument('--budget-usd',type=float,default=0.6)
    parser.add_argument('--previous')
    parser.add_argument('--stage',type=int,default=1)
    args=parser.parse_args()
    if args.action=='prepare':
        prepare(args.output,args.case,args.provider,args.budget_usd,args.previous,args.stage)
    else:
        run(args.output)


if __name__=='__main__':
    main()
