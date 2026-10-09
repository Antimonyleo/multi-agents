#!/usr/bin/env python3
"""Check a versioned review handoff; never run jobs, approve gates or dispatch agents."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

PHASES = {'plan', 'blocking', 'readiness', 'completion'}
TERMINAL = {'passed', 'failed', 'skipped', 'errored', 'cancelled', 'interrupted', 'timed_out'}
STATUSES = TERMINAL | {'planned', 'pending', 'running'}


def check_packet(packet, base):
    errors = []
    if not isinstance(packet, dict):
        return {'packet_complete_for_phase': False, 'errors': ['packet must be an object'],
                'gate_decision': 'not_evaluated'}
    phase = packet.get('phase')
    if not isinstance(phase, str) or phase not in PHASES:
        errors.append('phase must be plan, blocking, readiness or completion')
        phase = None
    for key in ('question', 'scope', 'stop_boundary'):
        if not isinstance(packet.get(key), str) or not packet[key].strip():
            errors.append(f'{key} must be a nonempty string')
    artifacts = packet.get('artifacts')
    if not isinstance(artifacts, list) or not artifacts:
        errors.append('artifacts must be a nonempty list')
        artifacts = []
    declared, verified = set(), set()
    for index, artifact in enumerate(artifacts):
        if not isinstance(artifact, dict) or not isinstance(artifact.get('path'), str) or not artifact['path'].strip():
            errors.append(f'artifact {index}: path required')
            continue
        path = (base / artifact['path']).resolve()
        if path in declared:
            errors.append(f'duplicate artifact: {artifact["path"]}')
            continue
        declared.add(path)
        expected = artifact.get('sha256')
        if not isinstance(expected, str) or not re.fullmatch('[0-9a-f]{64}', expected):
            errors.append(f'artifact {artifact["path"]}: SHA-256 required')
            continue
        try:
            if not path.is_file():
                errors.append(f'artifact is not a regular readable file: {artifact["path"]}')
                continue
            actual = hashlib.sha256()
            with path.open('rb') as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                    actual.update(chunk)
            if actual.hexdigest() != expected:
                errors.append(f'artifact changed: {artifact["path"]}')
            else:
                verified.add(path)
        except OSError as error:
            errors.append(f'artifact unavailable: {artifact["path"]}: {error.strerror}')
    checks = packet.get('checks')
    required = packet.get('required_checks')
    if not isinstance(checks, list):
        errors.append('checks must be a list')
        checks = []
    if not isinstance(required, list) or any(not isinstance(x, str) or not x.strip() for x in required):
        errors.append('required_checks must be a list of nonempty names')
        required = []
    if len(set(required)) != len(required):
        errors.append('required_checks contains duplicates')
    acknowledged = packet.get('acknowledged_missing', [])
    if not isinstance(acknowledged, list) or any(not isinstance(x, str) for x in acknowledged):
        errors.append('acknowledged_missing must contain check names')
        acknowledged = []
    if acknowledged and phase != 'blocking':
        errors.append('only a blocking review may acknowledge nonterminal checks')
    by_name = {}
    nonpassing = []
    for index, check in enumerate(checks):
        if not isinstance(check, dict) or not isinstance(check.get('name'), str) or not check['name'].strip():
            errors.append(f'check {index}: name required')
            continue
        name = check['name']
        if name in by_name:
            errors.append(f'duplicate check: {name}')
            continue
        by_name[name] = check
        status = check.get('status')
        if not isinstance(status, str) or status not in STATUSES:
            errors.append(f'check {name}: unknown status')
            by_name[name] = dict(check, status=None)
            continue
        if status in TERMINAL:
            evidence = check.get('evidence')
            if not isinstance(evidence, str) or (base / evidence).resolve() not in verified:
                errors.append(f'check {name}: terminal evidence must be a verified artifact')
            if status == 'skipped' and (not isinstance(check.get('reason'), str) or not check['reason'].strip()):
                errors.append(f'check {name}: skip reason required')
            if status != 'passed':
                nonpassing.append(name)
    for name in required:
        check = by_name.get(name)
        if check is None:
            errors.append(f'required check missing: {name}')
        elif phase in {'readiness', 'completion'} and check.get('status') not in TERMINAL:
            errors.append(f'required check not terminal: {name}')
        elif phase == 'blocking' and check.get('status') not in TERMINAL and name not in acknowledged:
            errors.append(f'nonterminal check must be acknowledged: {name}')
    for name in acknowledged:
        if name not in by_name or by_name[name].get('status') in TERMINAL:
            errors.append(f'acknowledgement does not name a nonterminal check: {name}')
    return {'phase': phase, 'packet_complete_for_phase': not errors,
            'errors': errors, 'verified_artifacts': len(verified),
            'observed_nonpassing_checks': nonpassing, 'acknowledged_missing': acknowledged,
            'gate_decision': 'not_evaluated'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('packet', type=Path)
    args = parser.parse_args()
    try:
        result = check_packet(json.loads(args.packet.read_text()), args.packet.resolve().parent)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        result = {'packet_complete_for_phase': False, 'errors': [str(error)],
                  'gate_decision': 'not_evaluated'}
    print(json.dumps(result, indent=2))
    return 0 if result['packet_complete_for_phase'] else 1


if __name__ == '__main__':
    sys.exit(main())
