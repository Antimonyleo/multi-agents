from pathlib import Path
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'skill/scientific-workflow/scripts/recover.py'
SPEC = importlib.util.spec_from_file_location('progress_recovery', SCRIPT)
recover = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(recover)


class ProgressTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.evidence = self.root / 'result.log'
        self.evidence.write_bytes(b'observed result\r\n')
        self.sha = hashlib.sha256(self.evidence.read_bytes()).hexdigest()
        self.anchor = '## Execution contract\nEpisode: fix-1\nKeep units seconds.\nTasks: inspect, fix\n'
        self.current = '## Current work\nEpisode: fix-1\nStatus: active\nNext: fix\n'
        self.tasks = ('## Tasks\n- [x] inspect: reproduce '
                      f'[evidence](result.log#sha256={self.sha})\n- [ ] fix: repair and verify\n')
        self.boundaries = '## Boundaries\nTrial ceiling 4; retain negative results.\n'
        self.record = self.anchor + self.tasks + self.boundaries + self.current
        self.target = self.root / 'WORK.md'
        self.target.write_text(self.record)

    def progress(self, anchor=None, current=None, tasks=None):
        return recover.progress(self.root, anchor or self.anchor, current or self.current,
                                self.anchor + (tasks or self.tasks))

    def replace(self, new=None, expected=None, **kwargs):
        draft = self.root / 'draft.md'
        draft.write_text(new or self.record.replace('ceiling', 'ceiling'))
        return recover.replace_record(self.root, 'WORK.md', 'draft.md',
                                      expected or recover.digest(self.record), 'fix-1', **kwargs)

    def test_progress_retains_pending_task_and_counts(self):
        result = self.progress()
        self.assertEqual((result['completed'], result['total'], result['next_task']), (1, 2, 'fix'))
        self.assertEqual(result['pending'], ['fix'])
        self.assertFalse(result['records_complete'])
        self.assertEqual(result['acceptance'], 'not_evaluated')

    def test_missing_task_cannot_disappear_from_scope(self):
        with self.assertRaisesRegex(ValueError, 'pinned Tasks'):
            self.progress(tasks=self.tasks.split('- [ ]')[0])

    def test_added_or_duplicate_tasks_are_rejected(self):
        for row in ('- [ ] extra: polish\n', '- [ ] fix: duplicate\n'):
            with self.subTest(row=row), self.assertRaises(ValueError):
                self.progress(tasks=self.tasks + row)

    def test_duplicate_pinned_ids_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'unique task IDs'):
            self.progress(anchor=self.anchor.replace('inspect, fix', 'fix, fix'))

    def test_checked_task_requires_evidence(self):
        with self.assertRaisesRegex(ValueError, 'hashed evidence'):
            self.progress(tasks=self.tasks.replace('- [ ] fix:', '- [x] fix:'))

    def test_changed_missing_and_empty_evidence_are_rejected(self):
        for value in (b'changed', b'', None):
            with self.subTest(value=value):
                if value is None:
                    self.evidence.unlink()
                else:
                    self.evidence.write_bytes(value)
                with self.assertRaises((ValueError, OSError)):
                    self.progress()

    def test_binary_evidence_can_be_verified(self):
        value = b'\x89PNG\x00\xff'
        self.evidence.write_bytes(value)
        self.progress(tasks=self.tasks.replace(self.sha, hashlib.sha256(value).hexdigest()))

    def test_shared_evidence_is_read_once(self):
        tasks = self.tasks.replace('- [ ] fix: repair and verify',
                                  f'- [x] fix: checked [evidence](./result.log#sha256={self.sha})')
        with patch.object(recover, 'read_bytes', wraps=recover.read_bytes) as reader:
            self.progress(tasks=tasks, current=self.current.replace('Next: fix', 'Next: none'))
        self.assertEqual(reader.call_count, 1)

    def test_reference_budget_prevents_duplicate_link_explosion(self):
        link = f'[evidence](result.log#sha256={self.sha}) '
        tasks = '## Tasks\n- [x] inspect: ' + link * 2000 + '\n- [ ] fix: repair\n'
        with patch.object(recover, 'read_bytes', wraps=recover.read_bytes) as reader:
            with self.assertRaisesRegex(ValueError, '128 references'):
                self.progress(tasks=tasks)
        self.assertEqual(reader.call_count, 1)

    def test_distinct_file_and_aggregate_byte_budgets(self):
        for byte_size, count, message in ((1, 33, '32 files'), (250000, 5, '1 MiB')):
            with self.subTest(byte_size=byte_size):
                links = []
                value = b'x' * byte_size
                sha = hashlib.sha256(value).hexdigest()
                for index in range(count):
                    name = f'{byte_size}-{index}.log'
                    (self.root / name).write_bytes(value)
                    links.append(f'[evidence]({name}#sha256={sha})')
                tasks = '## Tasks\n- [x] inspect: ' + ' '.join(links) + '\n- [ ] fix: repair\n'
                with self.assertRaisesRegex(ValueError, message):
                    self.progress(tasks=tasks)

    def test_evidence_outside_project_is_rejected(self):
        with self.assertRaises((ValueError, OSError)):
            self.progress(tasks=self.tasks.replace('result.log#', '../result.log#'))

    def test_invalid_completion_does_not_hide_pending_work(self):
        with self.assertRaisesRegex(ValueError, 'completion contradicts'):
            self.progress(current=self.current.replace('active', 'complete').replace('Next: fix', 'Next: none'))

    def test_next_item_cannot_be_completed_missing_or_absent(self):
        for next_item in ('inspect', 'missing', 'none'):
            with self.subTest(next_item=next_item), self.assertRaises(ValueError):
                self.progress(current=self.current.replace('Next: fix', 'Next: ' + next_item))

    def test_pause_and_block_need_a_reason_and_retain_next_item(self):
        for state in ('paused', 'blocked'):
            current = self.current.replace('active', state)
            with self.subTest(state=state):
                with self.assertRaisesRegex(ValueError, 'Reason'):
                    self.progress(current=current)
                result = self.progress(current=current + 'Reason: explicit boundary\n')
                self.assertFalse(result['records_complete'])
                self.assertEqual(result['next_task'], 'fix')

    def test_fenced_examples_are_not_tasks_or_status(self):
        self.progress(tasks=self.tasks + '```\n- [x] extra: fake\n```\n',
                      current=self.current + '```\nStatus: complete\n```\n')

    def test_ambiguous_status_and_malformed_task_fail(self):
        with self.assertRaises(ValueError):
            self.progress(current=self.current + 'Status: complete\n')
        with self.assertRaises(ValueError):
            self.progress(tasks=self.tasks.replace('- [ ] fix:', '- [!] fix:'))

    def test_hook_adds_only_small_progress_summary(self):
        result = recover.recovery({'hook_event_name': 'SessionStart', 'source': 'compact',
                                   'cwd': str(self.root)}, self.root, 'WORK.md', 'WORK.md',
                                  'fix-1', recover.digest(self.anchor), check_tasks=True)
        context = result['hookSpecificOutput']['additionalContext']
        data = json.loads(context.split('\n', 1)[1])
        self.assertEqual(data['progress']['next_task'], 'fix')
        self.assertNotIn(self.sha, context)
        self.assertLessEqual(len(context.encode()), 4096)

    def test_hook_refuses_false_completion_as_verified_source(self):
        self.target.write_text(self.record.replace('Status: active', 'Status: complete'))
        result = recover.recovery({'hook_event_name': 'SessionStart', 'source': 'resume',
                                   'cwd': str(self.root)}, self.root, 'WORK.md', 'WORK.md',
                                  'fix-1', recover.digest(self.anchor), check_tasks=True)
        self.assertIn('HANDOFF_UNVERIFIED', result['hookSpecificOutput']['additionalContext'])

    def test_completed_records_still_do_not_establish_acceptance(self):
        tasks = self.tasks.replace('- [ ] fix: repair and verify',
                                  f'- [x] fix: checked [evidence](result.log#sha256={self.sha})')
        current = self.current.replace('active', 'complete').replace('Next: fix', 'Next: none')
        result = self.progress(tasks=tasks, current=current)
        self.assertTrue(result['records_complete'])
        self.assertEqual(result['acceptance'], 'not_evaluated')

    def test_replace_preserves_prior_bytes_and_does_not_rebind(self):
        new = self.record.replace('Keep units seconds.', 'Keep units seconds. Also validate the control.')
        result = self.replace(new, check_tasks=True)
        self.assertEqual(self.target.read_text(), new)
        self.assertEqual((self.root / result['prior_bytes']).read_text(), self.record)
        self.assertFalse(result['binding_changed'])
        self.assertEqual(result['anchor_sha256'], recover.digest(recover.section(new, 'Execution contract')))

    def test_replacement_refuses_stale_expected_file(self):
        with self.assertRaisesRegex(ValueError, 'current file changed'):
            self.replace(expected='0' * 64)
        self.assertEqual(self.target.read_text(), self.record)
        self.assertFalse(list(self.root.glob('*.bak')))

    def test_replacement_refuses_changed_boundaries_or_episode(self):
        for new in (self.record.replace('ceiling 4', 'ceiling 8'), self.record.replace('fix-1', 'other')):
            with self.subTest(new=new), self.assertRaises(ValueError):
                self.replace(new)
            self.assertEqual(self.target.read_text(), self.record)

    def test_scope_replacement_cannot_resume_paused_record(self):
        paused = self.record.replace('Status: active', 'Status: paused\nReason: user pause')
        for check_tasks in (False, True):
            with self.subTest(check_tasks=check_tasks):
                self.target.write_text(paused)
                with self.assertRaisesRegex(ValueError, 'cannot resume'):
                    self.replace(expected=recover.digest(paused), check_tasks=check_tasks)
                self.assertEqual(self.target.read_text(), paused)

    def test_default_replace_cli_cannot_clear_pause(self):
        paused = self.record.replace('Status: active', 'Status: paused\nReason: user pause')
        self.target.write_text(paused)
        (self.root / 'draft.md').write_text(self.record)
        result = subprocess.run([sys.executable, str(SCRIPT), 'replace', '--project', str(self.root),
                                 '--target', 'WORK.md', '--candidate', 'draft.md', '--episode', 'fix-1',
                                 '--expected-sha256', recover.digest(paused)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(self.target.read_text(), paused)
        self.assertFalse(list(self.root.glob('*.bak')))

    def test_failed_atomic_replace_keeps_old_record_and_unlabelled_backup(self):
        with patch.object(recover.os, 'replace', side_effect=PermissionError('denied')):
            with self.assertRaises(PermissionError):
                self.replace(self.record.replace('Keep units', 'Preserve units'), check_tasks=True)
        self.assertEqual(self.target.read_text(), self.record)
        backups = list(self.root.glob('*.bak'))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), self.record)
        self.assertNotIn('superseded', backups[0].read_text())
        self.assertFalse(list(self.root.glob('.WORK.md.*')))

    def test_replacement_preserves_crlf_mode_and_backup_privacy(self):
        old = self.record.replace('\n', '\r\n')
        self.target.write_bytes(old.encode())
        os.chmod(self.target, 0o640)
        new = old.replace('Keep units', 'Preserve units')
        (self.root / 'draft.md').write_bytes(new.encode())
        result = recover.replace_record(self.root, 'WORK.md', 'draft.md', recover.digest(old), 'fix-1')
        self.assertEqual(self.target.read_bytes(), new.encode())
        backup = self.root / result['prior_bytes']
        self.assertEqual(backup.read_bytes(), old.encode())
        self.assertEqual(backup.stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.target.stat().st_mode & 0o777, 0o640)

    def test_cli_completion_checks_records_and_is_read_only(self):
        before = self.target.read_bytes()
        result = subprocess.run([sys.executable, str(SCRIPT), 'check', '--project', str(self.root),
                                 '--plan', 'WORK.md', '--state', 'WORK.md', '--episode', 'fix-1',
                                 '--anchor-sha256', recover.digest(self.anchor), '--completion'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(json.loads(result.stdout)['next_task'], 'fix')
        self.assertEqual(self.target.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
