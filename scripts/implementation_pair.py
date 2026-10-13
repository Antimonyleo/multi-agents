#!/usr/bin/env python3
"""Prepare a fresh pair; launch only from separately recorded bounded authority."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import secrets
import shutil
import subprocess
import uuid

ROOT = Path(__file__).resolve().parents[1]
ARMS = ('owner', 'support')
BUDGET = 1.5
CONTINUATION_CHECKS = ('usage_present', 'family_inclusion', 'native_role_identity',
                       'helper_limits', 'permission_boundary', 'review_completed',
                       'final_version_review_binding', 'public_check_observed',
                       'immutable_inputs_preserved', 'retrieval_replacement_assessed')


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


native = module('native_calibration')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def read(path):
    return json.loads(Path(path).read_text())


def tree(path):
    path = Path(path)
    return {str(p.relative_to(path)): sha(p) for p in sorted(path.rglob('*')) if p.is_file()}


def environment():
    return {
        'runtime_version': subprocess.check_output(['claude', '--version'], text=True).strip(),
        'native_config_sha256': sha(Path.home() / '.claude/settings.json'),
        'native_capability_files': native.native_capability_files('claude'),
    }


def prepare(output, protocol, order=None):
    output, protocol = Path(output).resolve(), Path(protocol).resolve()
    if order is not None and sorted(order) != sorted(ARMS):
        raise ValueError('invalid arm order')
    output.mkdir(parents=True, exist_ok=False)
    fixture = module('implementation_fixture')
    controls = environment()
    if order is None:
        order = list(ARMS)
        secrets.SystemRandom().shuffle(order)
    else:
        order = list(order)
    manifests = {}
    for arm in ARMS:
        out = output / arm
        out.mkdir()
        workspace = out / 'workspace'
        built = fixture.build(workspace)
        scope = ('Synthetic implementation evaluation only. Work in this workspace; '
                 'no network, memory, scientific work, background jobs or unrelated paths. '
                 'Do not read evaluator files outside the workspace. Edit only '
                 + ', '.join(built['writable_paths']) + ' and receipts/. '
                 'Use scientific-workflow. No nested delegation.')
        (workspace / 'AGENTS.md').write_text(scope + '\n')
        (workspace / 'CLAUDE.md').write_text('@AGENTS.md\n')
        for folder in ('.agents', '.claude'):
            shutil.copytree(ROOT / 'skill/scientific-workflow', workspace / folder / 'skills/scientific-workflow')
        intervention = (
            'Perform retrieval yourself. Call no helper except the required scientific_reviewer.'
            if arm == 'owner' else
            'You may call scientific_explorer once for this mechanical lookup only: '
            + built['retrieval_task'] + ' Delegate only if it replaces useful owner retrieval; '
            'otherwise do it yourself. No helper except this optional explorer and the required reviewer.')
        prompt = (scope + '\n' + built['prompt'] + '\n' + intervention + '\n'
                  'After your final edit, run the named public command: ' + ' '.join(built['public_command']) + '. '
                  'Save full stdout/stderr as receipts/public.log and the verified process exit as '
                  'receipts/public-exit.json. Save SHA-256 values for every editable source and that log '
                  'in receipts/review-input.json. Call exactly one scientific_reviewer, after those checks, '
                  'to inspect original contracts, final sources, full check log/exit and hash manifest. '
                  'Its response must list findings and disposition. Do not edit implementation or rerun '
                  'checks after review. If review finds a needed repair, report failure and stop; no second '
                  'review. Finish with a plain-text account of changes, checks, findings and limits.\n')
        (out / 'prompt.txt').write_text(prompt)
        # Native build_command expects a schema; final text is deliberately unscored.
        write(out / 'schema.json', {'type': 'object', 'properties': {'summary': {'type': 'string'}},
                                    'required': ['summary'], 'additionalProperties': False})
        manifest = {
            'provider': 'claude', 'arm': 'workflow', 'comparison': 'routing',
            'purpose': 'fresh_implementation_pair', 'treatment': arm,
            'model_requested': 'opus', 'effort_requested': 'high',
            'session_id_requested': str(uuid.uuid4()), 'timeout_s': 300, 'cleanup_grace_s': 5,
            'envelope': {'claude_cli_budget_usd': BUDGET},
            'writable_paths': built['writable_paths'], 'public_command': built['public_command'],
            'before': tree(workspace), **controls,
        }
        command = native.build_command(out, manifest)
        for flag in ('--tools', '--allowedTools'):
            command[command.index(flag) + 1] = 'Read,Glob,Grep,Bash,Skill,Agent,Edit,Write'
        command[command.index('--append-system-prompt') + 1] = scope
        # Plain output avoids hidden literal/schema acceptance and extra formatting turns.
        i = command.index('--json-schema')
        del command[i:i + 2]
        manifest['command'] = command
        write(out / 'manifest.json', manifest)
        manifests[arm] = manifest
    if manifests['owner']['before'] != manifests['support']['before']:
        raise ValueError('initial workspaces differ')
    source_paths = [Path(__file__), ROOT / 'scripts/implementation_fixture.py',
                    ROOT / 'scripts/native_calibration.py', native.LEGACY, protocol]
    seal = {
        'purpose': 'fresh_implementation_pair', 'order': order, 'controls': controls,
        'inputs': tree(output),
        'sources': {str(p): sha(p) for p in source_paths},
        'limits': {'parents': 2, 'children': 3, 'per_family_reported_usd': BUDGET,
                   'nominal_total_usd': 3.0, 'timeout_s': 300, 'retry': False},
    }
    write(output / 'seal.json', seal)
    write(output / 'allocation.json', {'approved': False, 'authority': None,
                                       'seal_sha256': sha(output / 'seal.json'), 'limits': seal['limits']})
    return seal


def check(output, arm=None):
    """Read-only preflight. A changed completed peer is checked by terminal review."""
    output = Path(output).resolve()
    seal = read(output / 'seal.json')
    errors = []
    for name, digest in seal['sources'].items():
        if not Path(name).is_file() or sha(name) != digest:
            errors.append('source differs: ' + name)
    for name, digest in seal['inputs'].items():
        # During arm two, skip only the already executed peer workspace.
        if arm and not name.startswith(arm + '/') and '/workspace/' in name:
            continue
        path = output / name
        if not path.is_file() or sha(path) != digest:
            errors.append('input differs: ' + name)
    for target in (ARMS if arm is None else (arm,)):
        manifest = read(output / target / 'manifest.json')
        if tree(output / target / 'workspace') != manifest['before']:
            errors.append('initial workspace differs: ' + target)
    if environment() != seal['controls']:
        errors.append('runtime/config/capability inventory differs')
    return {'prepared_inputs_valid': not errors, 'errors': errors,
            'native_start_authorized': False}


def launch(output, arm):
    """The record documents human authority, not a security/authentication boundary."""
    output = Path(output).resolve()
    if arm not in ARMS:
        raise ValueError('unknown arm')
    seal = read(output / 'seal.json')
    allocation = read(output / 'allocation.json')
    digest = sha(output / 'seal.json')
    if (allocation.get('approved') is not True or not allocation.get('authority')
            or allocation.get('seal_sha256') != digest or allocation.get('limits') != seal['limits']):
        raise ValueError('new exact allocation is not approved')
    readiness = read(output / 'readiness.json')
    if (readiness.get('accepted') is not True or not readiness.get('reviewer')
            or readiness.get('seal_sha256') != digest):
        raise ValueError('independent readiness review is missing or stale')
    if seal['order'].index(arm) == 1:
        peer = output / seal['order'][0]
        review = read(peer / 'continuation.json')
        evidence = peer / 'terminal.json'
        if (review.get('measurement_valid') is not True or not review.get('reviewer')
                or review.get('terminal_sha256') != sha(evidence)
                or not all(review.get('checks', {}).get(k) is True for k in CONTINUATION_CHECKS)
                or not all(read(evidence).get('terminal_checks', {}).get(k) is True
                           for k in ('execution_success', 'cleanup_verified', 'capture_complete'))):
            raise ValueError('peer continuation is not independently accepted')
        for name, expected in read(evidence)['artifacts'].items():
            if not (peer / name).is_file() or sha(peer / name) != expected:
                raise ValueError('peer evidence changed')
    elif any((output / x / 'started.json').exists() for x in ARMS):
        raise ValueError('pair has already started')
    result = check(output, arm if seal['order'].index(arm) == 1 else None)
    if not result['prepared_inputs_valid']:
        raise ValueError('; '.join(result['errors']))
    out = output / arm
    if any((out / name).exists() for name in ('started.json', 'trace.jsonl', 'execution.json', 'terminal.json')):
        raise ValueError('refusing repeated start')
    # Exclusive durable marker precedes process creation, including launch failures.
    with (out / 'started.json').open('x') as stream:
        json.dump({'seal_sha256': digest, 'allocation_sha256': sha(output / 'allocation.json')}, stream)
    manifest = read(out / 'manifest.json')
    errors = []
    try:
        spec = importlib.util.spec_from_file_location('owned_runner', native.LEGACY)
        runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runner)
        runner.run(out, manifest)
    except Exception as exc:
        errors.append('launch: ' + repr(exc))
    try:
        children = native.collect_claude(out, manifest['session_id_requested'])
        write(out / 'children.json', children)
        write(out / 'usage.json', native.normalize('claude', native.events(out / 'trace.jsonl')))
    except Exception as exc:
        errors.append('capture: ' + repr(exc))
    records = {}
    for name in ('execution.json', 'native_capture.json'):
        try:
            records[name] = read(out / name)
            if not isinstance(records[name], dict):
                raise ValueError('expected object')
        except (OSError, ValueError) as exc:
            records[name] = {}
            errors.append(name + ': ' + repr(exc))
    execution, capture = records['execution.json'], records['native_capture.json']
    cleanup = execution.get('cleanup')
    cleanup_verified = isinstance(cleanup, dict) and cleanup.get('verified') is True
    # Final source may be arbitrary generated code: oracle is a bounded local check,
    # not an isolation guarantee. No oracle is run if owned cleanup is unverified.
    if cleanup_verified:
        try:
            write(out / 'oracle.json', module('implementation_fixture').validate(
                out / 'workspace', evidence_path=out / 'oracle-probes.json'))
        except Exception as exc:
            errors.append('oracle: ' + repr(exc))
    artifacts = tree(out)
    write(out / 'terminal.json', {
        'errors': errors, 'artifacts': artifacts,
        'terminal_checks': {
            'execution_success': type(execution.get('returncode')) is int and execution['returncode'] == 0 and execution.get('timed_out') is False,
            'cleanup_verified': cleanup_verified,
            'capture_complete': capture.get('complete') is True and not errors,
        },
        'measurement_valid': None, 'task_accepted': None,
        'next': 'Independent raw-evidence assessment required by PROTOCOL.md; no automatic second start.',
    })


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', 'check', 'launch'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--protocol', type=Path)
    parser.add_argument('--arm', choices=ARMS)
    args = parser.parse_args()
    if args.action == 'prepare':
        if not args.protocol:
            parser.error('prepare requires --protocol')
        result = prepare(args.output, args.protocol)
    elif args.action == 'check':
        result = check(args.output)
    else:
        if not args.arm:
            parser.error('launch requires --arm')
        result = launch(args.output, args.arm)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
