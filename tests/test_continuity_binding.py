import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'skill/scientific-workflow/scripts'
SPEC = importlib.util.spec_from_file_location('bound_recovery', SCRIPTS / 'recover.py')
recover = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(recover)


class BindingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'verify.py').write_text('raise SystemExit(0)\n')
        sha = hashlib.sha256((self.root / 'verify.py').read_bytes()).hexdigest()
        tasks = '## Tasks\n- [ ] test: Run full acceptance suite\n'
        policy = {'argv': ['python', 'verify.py'], 'inputs': {'verify.py': sha}, 'outputs': ['REPORT.md']}
        self.anchor = ('## Execution contract\nEpisode: bound-1\nTasks: test\nTask definitions: ' +
                       recover.tasks_digest(tasks) + '\nVerify: ' + json.dumps(policy) + '\n')
        (self.root / 'WORK.md').write_text(self.anchor + tasks +
            '## Boundaries\nNo real science.\n## Current work\nEpisode: bound-1\nStatus: active\nNext: test\n')
        self.args = [sys.executable, str(SCRIPTS / 'bind.py'), '--project', str(self.root),
                     '--runtime', 'codex', '--plan', 'WORK.md', '--state', 'WORK.md',
                     '--episode', 'bound-1', '--session-id', 'session-1',
                     '--anchor-sha256', recover.digest(self.anchor)]

    def run_bind(self, *extra, expected=0):
        result = subprocess.run(self.args + list(extra), capture_output=True, text=True)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def test_preview_is_strict_session_bound_and_read_only(self):
        fragment = json.loads(self.run_bind().stdout)
        handler = fragment['hooks']['SessionStart'][0]['hooks'][0]
        self.assertIn('--session-id session-1', handler['command'])
        self.assertIn('--strict', handler['command'])
        self.assertEqual(handler['additionalContextLimit'], 0)
        self.assertFalse((self.root / '.codex').exists())

    def test_apply_preserves_native_fields_and_unrelated_hooks_and_is_idempotent(self):
        path = self.root / '.codex/hooks.json'
        path.parent.mkdir()
        unrelated = {'matcher': 'startup', 'hooks': [{'type': 'command', 'command': 'true'}]}
        initial = {'other': 17, 'hooks': {'SessionStart': [unrelated], 'PostToolUse': []}}
        path.write_text(json.dumps(initial))
        self.run_bind('--apply')
        after = json.loads(path.read_text())
        self.assertEqual(after['other'], 17)
        self.assertEqual(after['hooks']['PostToolUse'], [])
        self.assertEqual(after['hooks']['SessionStart'][0], unrelated)
        self.assertFalse(json.loads(self.run_bind('--apply').stdout)['changed'])
        self.assertEqual(len(list(path.parent.glob('*.bak'))), 1)

    def test_new_session_requires_explicit_owner_replacement(self):
        self.run_bind('--apply')
        path = self.root / '.codex/hooks.json'
        before = path.read_bytes()
        self.args[self.args.index('session-1')] = 'session-2'
        self.run_bind('--apply', expected=2)
        self.assertEqual(path.read_bytes(), before)
        self.run_bind('--apply', '--replace-owned')
        self.assertIn('session-2', path.read_text())
        self.assertEqual(len(json.loads(path.read_text())['hooks']['SessionStart']), 1)

    def test_wrong_or_missing_session_never_injects_saved_task(self):
        for session in ('session-1', 'session-2', None):
            event = {'hook_event_name': 'SessionStart', 'source': 'compact',
                     'cwd': str(self.root), 'session_id': session}
            result = recover.recovery(event, self.root, 'WORK.md', 'WORK.md', 'bound-1',
                       recover.digest(self.anchor), strict=True, expected_session='session-1')
            text = result['hookSpecificOutput']['additionalContext']
            self.assertLessEqual(len(text.encode()), 4096)
            if session == 'session-1':
                self.assertIn('SOURCE_MATCHED_ONLY', text)
            else:
                self.assertIn('HANDOFF_UNVERIFIED', text)
                self.assertNotIn('Run full acceptance suite', text)

    def test_external_config_symlink_and_invalid_source_are_refused(self):
        with tempfile.TemporaryDirectory() as outside:
            (self.root / '.codex').symlink_to(outside, target_is_directory=True)
            self.run_bind('--apply', expected=2)
            self.assertFalse((Path(outside) / 'hooks.json').exists())
        self.run_bind('--session-id', 'invalid id', expected=2)
        (self.root / 'other.py').write_text('print("not recovery")\n')
        self.run_bind('--script', str(self.root / 'other.py'), expected=2)

    def test_claude_fragment_uses_native_shape(self):
        self.args[self.args.index('codex')] = 'claude'
        self.run_bind('--apply')
        path = self.root / '.claude/settings.local.json'
        handler = json.loads(path.read_text())['hooks']['SessionStart'][0]['hooks'][0]
        self.assertNotIn('additionalContextLimit', handler)
        self.assertFalse((self.root / '.codex').exists())

    def test_callback_fifo_and_oversize_are_rejected_without_blocking(self):
        fifo = self.root / 'callback.fifo'
        os.mkfifo(fifo)
        for path in (fifo, self.root / 'large.py'):
            if path != fifo:
                path.write_bytes(b'x' * (recover.MAX_FILE_BYTES + 1))
            result = subprocess.run(self.args + ['--script', str(path)], capture_output=True,
                                    text=True, timeout=3)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
