#!/usr/bin/env python3
"""Preview or explicitly apply one project/session-bound native recovery hook.

Does not create goals, trust hooks, change permissions or install global settings.
"""
import argparse
import json
import os
from pathlib import Path
import shlex
import sys
import tempfile

import recover

MARKER = 'scientific-workflow continuity'


def fragment(project, plan, state, episode, session, pin, runtime, script):
    if recover.read_bytes(script) != recover.read_bytes(Path(recover.__file__)):
        raise ValueError('callback must match the validated recovery version')
    probe = recover.recovery({'hook_event_name': 'SessionStart', 'source': 'startup',
                              'cwd': str(project), 'session_id': session}, project, state,
                             plan, episode, pin, strict=True, expected_session=session)
    context = probe['hookSpecificOutput']['additionalContext']
    if '"status":"SOURCE_MATCHED_ONLY"' not in context:
        raise ValueError('binding failed strict validation: ' + context)
    command = shlex.join([sys.executable, '-I', str(script), 'hook', '--project', str(project),
                          '--plan', plan, '--state', state, '--episode', episode,
                          '--anchor-sha256', pin, '--session-id', session, '--strict'])
    handler = {'type': 'command', 'command': command, 'timeout': 5, 'statusMessage': MARKER}
    if runtime == 'codex':
        handler['additionalContextLimit'] = 0
    return {'matcher': '^(startup|resume|clear|compact)$', 'hooks': [handler]}


def apply(project, runtime, group, replace_owned=False):
    relative = '.codex/hooks.json' if runtime == 'codex' else '.claude/settings.local.json'
    path = project / relative
    if not recover.within(path.resolve(), project) or path.is_symlink():
        raise ValueError('native config must stay inside the project and not be a symlink')
    old = recover.read_regular(path) if path.exists() else None
    data = recover.json_object(old) if old is not None else {}
    hooks = data.setdefault('hooks', {})
    if not isinstance(hooks, dict):
        raise ValueError('existing hooks must be an object')
    groups = hooks.setdefault('SessionStart', [])
    if not isinstance(groups, list) or any(not isinstance(item, dict) for item in groups):
        raise ValueError('existing SessionStart must be a list of groups')
    owned = []
    for item in groups:
        handlers = item.get('hooks')
        if not isinstance(handlers, list) or any(not isinstance(h, dict) for h in handlers):
            raise ValueError('existing matcher handlers must be a list of objects')
        if any(h.get('statusMessage') == MARKER for h in handlers):
            if any(h.get('statusMessage') != MARKER for h in handlers):
                raise ValueError('mixed owned/user handler group requires manual reconciliation')
            owned.append(item)
    if owned == [group]:
        return {'path': relative, 'changed': False, 'trust': 'native review still required'}
    if owned and not replace_owned:
        raise ValueError('existing continuity binding; inspect owner before --replace-owned')
    hooks['SessionStart'] = [item for item in groups if item not in owned] + [group]
    new = json.dumps(data, indent=2) + '\n'
    path.parent.mkdir(parents=True, exist_ok=True)
    if old is not None:
        backup = path.with_name(path.name + '.continuity-' + recover.digest(old)[:12] + '.bak')
        try:
            fd = os.open(backup, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, 'w', encoding='utf-8', newline='') as handle:
                handle.write(old)
        except FileExistsError:
            if recover.read_regular(backup) != old:
                raise ValueError('native config backup conflicts')
    fd, temporary = tempfile.mkstemp(prefix='.continuity-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as handle:
            handle.write(new)
            handle.flush()
            os.fsync(handle.fileno())
        current = recover.read_regular(path) if path.exists() else None
        if current != old:
            raise ValueError('native config changed; application refused')
        if old is not None:
            os.chmod(temporary, path.stat().st_mode & 0o777)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return {'path': relative, 'changed': True, 'trust': 'review via native /hooks before relying on it'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True, type=Path)
    parser.add_argument('--runtime', required=True, choices=('codex', 'claude'))
    for name in ('plan', 'state', 'episode', 'session-id', 'anchor-sha256'):
        parser.add_argument('--' + name, required=True)
    parser.add_argument('--script', type=Path, default=Path(recover.__file__))
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--replace-owned', action='store_true')
    args = parser.parse_args()
    try:
        project = args.project.resolve(strict=True)
        group = fragment(project, args.plan, args.state, args.episode, args.session_id,
                         args.anchor_sha256, args.runtime, args.script.resolve(strict=True))
        result = apply(project, args.runtime, group, args.replace_owned) if args.apply else {
            'hooks': {'SessionStart': [group]}}
        print(json.dumps(result, indent=2))
        return 0
    except (OSError, ValueError, TypeError) as error:
        print('continuity binding: ' + str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
