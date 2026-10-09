#!/usr/bin/env python3
"""Install native workflow artifacts without editing runtime configuration."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid

REPO = Path(__file__).resolve().parents[1]


def signature(path):
    """Capture identity without dereferencing symlinks or ignoring tree changes."""
    if path.is_symlink():
        return {'type': 'link', 'target': os.readlink(path)}
    if not path.exists():
        return {'type': 'absent'}
    if path.is_file():
        return {'type': 'file', 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                'mode': path.stat().st_mode & 0o777}
    if path.is_dir():
        return {'type': 'directory', 'entries': {
            str(p.relative_to(path)): signature(p) for p in sorted(path.rglob('*'))}}
    raise ValueError(f'unsupported path type: {path}')


def mappings(args):
    home = Path.home()
    claude = Path(os.environ.get('CLAUDE_HOME', home / '.claude')).absolute()
    codex = Path(os.environ.get('CODEX_HOME', home / '.codex')).absolute()
    agents = Path(os.environ.get('AGENTS_HOME', home / '.agents')).absolute()
    result = []

    def link(src, dst):
        result.append({'source': str(src), 'destination': str(dst), 'kind': 'link',
                       'installed': {'type': 'link', 'target': str(src)}})

    def copy(src, dst):
        result.append({'source': str(src), 'destination': str(dst), 'kind': 'copy',
                       'installed': signature(src)})

    if args.target in ('claude', 'both'):
        link(REPO / 'skill/scientific-workflow', claude / 'skills/scientific-workflow')
        for src in sorted((REPO / 'agents').glob('scientific_*.md')):
            link(src, claude / 'agents' / src.name)
    if args.target in ('codex', 'both'):
        link(REPO / 'skill/scientific-workflow', agents / 'skills/scientific-workflow')
        for src in sorted((REPO / 'agents/codex').glob('scientific_*.toml')):
            copy(src, codex / 'agents' / src.name)
        if args.legacy_manual:
            body = ('# Scientific workflow compatibility pointer\n\n'
                    'The shared workflow is maintained in the repository.\n\n'
                    f'- [Shared skill]({REPO}/skill/scientific-workflow/SKILL.md)\n'
                    f'- [Codex adapter]({REPO}/skill/scientific-workflow/references/codex.md)\n'
                    f'- [Claude adapter]({REPO}/skill/scientific-workflow/references/claude-code.md)\n'
                    f'- [Historical manual]({REPO}/docs/migration/2026-10-09/SCIENTIFIC_AGENT_WORKFLOW.before.md)\n\n'
                    'Project authority and pauses remain in effect. Historical snapshots are not active policy.\n')
            result.append({'destination': str(Path(args.legacy_manual).absolute()),
                           'kind': 'text', 'text': body,
                           'installed': {'type': 'file',
                                         'sha256': hashlib.sha256(body.encode()).hexdigest(),
                                         'mode': 0o644}})
    elif args.legacy_manual:
        raise ValueError('--legacy-manual requires --target codex or both')
    return result


def save_receipt(path, record):
    tmp = path.with_suffix('.pending')
    tmp.write_text(json.dumps(record, indent=2) + '\n')
    with tmp.open('rb') as stream:
        os.fsync(stream.fileno())
    tmp.replace(path)
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def remove(path):
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        raise ValueError(f'unsupported path type: {path}')


def restore_entries(record):
    conflicts = []
    for entry in reversed(record['entries']):
        dest = Path(entry['destination'])
        backup = Path(entry['backup']) if entry.get('backup') else None
        if entry.get('temporary'):
            remove(Path(entry['temporary']))
        # A prepared entry has not yet changed its destination.
        if entry['phase'] == 'prepared':
            continue
        current = signature(dest)
        if current not in (entry['installed'], {'type': 'absent'}):
            conflicts.append(f'destination changed: {dest}')
            continue
        if backup is not None and signature(backup) != entry['before']:
            conflicts.append(f'backup changed or missing: {backup}')
            continue
        if current != {'type': 'absent'}:
            remove(dest)
        if backup is not None:
            backup.replace(dest)
        entry['phase'] = 'restored'
    return conflicts


def rollback(receipt):
    record = json.loads(receipt.read_text())
    if record.get('status') != 'complete':
        raise ValueError('receipt is not a completed installation; inspect interrupted receipts manually')
    # Verify all entries before any restoration. Later edits must not be lost.
    for entry in record['entries']:
        dest = Path(entry['destination'])
        if signature(dest) != entry['installed']:
            raise ValueError(f'rollback blocked: installed destination changed: {dest}')
        if entry.get('backup') and signature(Path(entry['backup'])) != entry['before']:
            raise ValueError(f'rollback blocked: backup changed: {entry["backup"]}')
    conflicts = restore_entries(record)
    if conflicts:
        record['status'] = 'rollback_conflicts'
        record['conflicts'] = conflicts
        save_receipt(receipt, record)
        raise ValueError('rollback encountered a concurrent change; see receipt')
    record['status'] = 'rolled_back'
    save_receipt(receipt, record)
    print(f'rolled back: {receipt}')


def install(args):
    entries = mappings(args)
    if len(entries) != (12 if args.target == 'both' else 6) + bool(args.legacy_manual):
        raise ValueError('expected one skill and five native agent profiles per runtime')
    destinations = [Path(e['destination']).parent.resolve() / Path(e['destination']).name for e in entries]
    for entry, dest in zip(entries, destinations):
        entry['destination'] = str(dest)
        for ancestor in dest.parents:
            if ancestor.exists() and not ancestor.is_dir():
                raise ValueError(f'destination parent is not a directory: {ancestor}')
    if len(set(destinations)) != len(destinations):
        raise ValueError('runtime destinations overlap')
    for left in destinations:
        for right in destinations:
            if left != right and left in right.parents:
                raise ValueError(f'destinations overlap: {left} and {right}')
        if left == REPO or REPO in left.parents or left in REPO.parents:
            raise ValueError(f'destination overlaps source repository: {left}')
    conflicts, changes = [], []
    for entry in entries:
        if 'source' in entry and not Path(entry['source']).exists():
            raise ValueError(f'missing source: {entry["source"]}')
        entry['before'] = signature(Path(entry['destination']))
        if entry['before'] != entry['installed']:
            changes.append(entry)
            if entry['before']['type'] != 'absent':
                conflicts.append(entry['destination'])
    if args.check:
        for entry in changes:
            print(f'drift or missing: {entry["destination"]}')
        if not changes:
            print(f'check passed: {args.target} ({len(entries)} destinations)')
        return bool(changes)
    if args.uninstall:
        if args.target != 'claude':
            raise ValueError('use --rollback RECEIPT for Codex copied profiles or migrations')
        for entry in entries:
            path = Path(entry['destination'])
            if signature(path) == entry['installed']:
                print(f'{"would remove" if args.dry_run else "removed"}: {path}')
                if not args.dry_run:
                    path.unlink()
            else:
                print(f'skipped (not an owned link): {path}')
        return 0
    if conflicts and not args.migrate:
        for path in conflicts:
            print(f'conflict: {path}')
        raise ValueError('entire install blocked before mutation; use --migrate to retain backups')
    for entry in changes:
        print(f'{"backup and install" if entry["before"]["type"] != "absent" else "install"}: {entry["destination"]}')
    if args.dry_run:
        print(f'dry-run: {len(changes)} changes; no writes')
        return 0
    if not changes:
        print('already installed; no changes')
        return 0
    # Backups use same filesystem as their destinations, allowing atomic renames.
    transaction = uuid.uuid4().hex
    state = Path(args.state_dir).absolute()
    if any(d == state or d in state.parents or state in d.parents for d in destinations):
        raise ValueError('state directory overlaps an installed destination')
    receipt_dir = state / 'transactions' / transaction
    receipt_dir.mkdir(parents=True, mode=0o700)
    receipt = receipt_dir / 'receipt.json'
    revision = subprocess.run(['git', '-C', str(REPO), 'rev-parse', 'HEAD'],
                              capture_output=True, text=True).stdout.strip() or None
    record = {'version': 1, 'status': 'installing', 'source_repo': str(REPO),
              'source_revision': revision, 'source_identities': {
                  e['source']: signature(Path(e['source'])) for e in entries if 'source' in e},
              'target': args.target, 'entries': []}
    save_receipt(receipt, record)
    try:
        for index, entry in enumerate(changes):
            dest = Path(entry['destination'])
            if signature(dest) != entry['before']:
                raise ValueError(f'destination changed since preflight: {dest}')
            if 'source' in entry and signature(Path(entry['source'])) != record['source_identities'][entry['source']]:
                raise ValueError(f'source changed since preflight: {entry["source"]}')
            dest.parent.mkdir(parents=True, exist_ok=True)
            entry['phase'] = 'prepared'
            if entry['before']['type'] != 'absent':
                backup_root = dest.parent if entry['kind'] == 'text' else dest.parent.parent
                backup = backup_root / '.scientific-workflow-backups' / transaction / dest.name
                if backup.exists() or backup.is_symlink():
                    raise ValueError(f'backup exists: {backup}')
                entry['backup'] = str(backup)
            record['entries'].append(entry)
            save_receipt(receipt, record)
            if entry.get('backup'):
                Path(entry['backup']).parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                dest.replace(entry['backup'])
                entry['phase'] = 'backed_up'
                save_receipt(receipt, record)
            entry['phase'] = 'installing'
            temporary = dest.with_name(f'.{dest.name}.workflow-install-{transaction}')
            entry['temporary'] = str(temporary)
            save_receipt(receipt, record)
            if entry['kind'] == 'link':
                temporary.symlink_to(entry['source'])
            elif entry['kind'] == 'copy':
                shutil.copy2(entry['source'], temporary)
            else:
                temporary.write_text(entry['text'])
                temporary.chmod(0o644)
            if signature(dest) != {'type': 'absent'}:
                raise ValueError(f'destination changed during install: {dest}')
            temporary.replace(dest)
            entry['phase'] = 'installed'
            if signature(dest) != entry['installed']:
                raise ValueError(f'installed identity mismatch: {dest}')
            save_receipt(receipt, record)
        record['status'] = 'complete'
        save_receipt(receipt, record)
    except BaseException:
        # This lane owns the changes made in this transaction only.
        conflicts = restore_entries(record)
        record['status'] = 'failed_conflicts' if conflicts else 'failed_restored'
        record['conflicts'] = conflicts
        save_receipt(receipt, record)
        outcome = 'preserved concurrent changes; recovery required' if conflicts else 'restored'
        print(f'failed installation {outcome}; receipt: {receipt}', file=sys.stderr)
        raise
    print(f'receipt: {receipt}')
    print('Runtime settings were not changed. Reload sessions for native profile changes.')
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', choices=['claude', 'codex', 'both'], default='claude')
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument('--check', action='store_true')
    actions.add_argument('--uninstall', action='store_true')
    actions.add_argument('--rollback', type=Path, metavar='RECEIPT')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--migrate', action='store_true', help='back up conflicting destinations')
    parser.add_argument('--legacy-manual', help='optional Codex compatibility pointer destination')
    parser.add_argument('--state-dir', default=str(Path.home() / '.local/state/scientific-workflow'))
    args = parser.parse_args()
    try:
        if args.rollback:
            if args.dry_run or args.check or args.uninstall or args.migrate or args.legacy_manual:
                parser.error('--rollback must be used alone')
            rollback(args.rollback.absolute())
            return 0
        return install(args)
    except (OSError, ValueError) as error:
        print(f'error: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
