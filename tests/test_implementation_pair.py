import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('implementation_pair', ROOT / 'scripts/implementation_pair.py')
pair = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pair)


class PairTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.out = self.base / 'pair'
        self.protocol = self.base / 'protocol.md'
        self.protocol.write_text('test protocol')
        self.env = patch.object(pair, 'environment', return_value={'runtime_version': 'offline',
            'native_config_sha256': 'test', 'native_capability_files': {}})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.seal = pair.prepare(self.out, self.protocol)

    def authorize(self):
        allocation = pair.read(self.out / 'allocation.json')
        allocation.update(approved=True, authority='OFFLINE TEST ONLY')
        pair.write(self.out / 'allocation.json', allocation)
        pair.write(self.out / 'readiness.json', {'accepted': True, 'reviewer': 'offline reviewer',
            'seal_sha256': pair.sha(self.out / 'seal.json')})

    def test_authorized_fake_launch_records_terminal_without_self_accepting(self):
        self.authorize()
        arm = self.seal['order'][0]
        out = self.out / arm
        def fake_run(destination, manifest):
            self.assertTrue((destination / 'started.json').is_file())
            pair.write(destination / 'execution.json', {'returncode': 0, 'timed_out': False,
                       'cleanup': {'verified': True}})
            (destination / 'trace.jsonl').write_text('')
        def fake_collect(destination, session):
            pair.write(destination / 'native_capture.json', {'complete': True})
            return []
        runner = SimpleNamespace(run=fake_run)
        spec = SimpleNamespace(loader=SimpleNamespace(exec_module=lambda value: None))
        fixture = SimpleNamespace(validate=lambda path, **kwargs: {'fake_probe': True})
        with patch.object(pair.importlib.util, 'spec_from_file_location', return_value=spec), \
             patch.object(pair.importlib.util, 'module_from_spec', return_value=runner), \
             patch.object(pair.native, 'collect_claude', side_effect=fake_collect), \
             patch.object(pair, 'module', return_value=fixture):
            pair.launch(self.out, arm)
        terminal = pair.read(out / 'terminal.json')
        self.assertIsNone(terminal['measurement_valid'])
        self.assertIsNone(terminal['task_accepted'])
        self.assertTrue(terminal['terminal_checks']['cleanup_verified'])
        self.assertIn('trace.jsonl', terminal['artifacts'])
        with self.assertRaisesRegex(ValueError, 'already started'):
            pair.launch(self.out, arm)

    def test_loader_failure_leaves_terminal_and_cannot_retry(self):
        self.authorize()
        arm = self.seal['order'][0]
        with patch.object(pair.importlib.util, 'spec_from_file_location', side_effect=RuntimeError('test failure')), \
             patch.object(pair.native, 'collect_claude', side_effect=ValueError('no native start')):
            pair.launch(self.out, arm)
        terminal = pair.read(self.out / arm / 'terminal.json')
        self.assertFalse(terminal['terminal_checks']['execution_success'])
        self.assertFalse(terminal['terminal_checks']['capture_complete'])
        self.assertTrue(terminal['errors'])
        self.assertFalse((self.out / arm / 'oracle.json').exists())
        with self.assertRaisesRegex(ValueError, 'already started'):
            pair.launch(self.out, arm)

    def test_corrected_preparation_can_retain_original_order(self):
        corrected = self.base / 'corrected'
        seal = pair.prepare(corrected, self.protocol, order=self.seal['order'])
        self.assertEqual(seal['order'], self.seal['order'])
        with self.assertRaisesRegex(ValueError, 'invalid arm order'):
            pair.prepare(self.base / 'invalid', self.protocol, order=['owner', 'owner'])

    def test_equal_workspaces_tools_budget_and_distinct_sessions(self):
        owner = pair.read(self.out / 'owner/manifest.json')
        support = pair.read(self.out / 'support/manifest.json')
        for key in ('before', 'envelope', 'public_command', 'writable_paths', 'timeout_s'):
            self.assertEqual(owner[key], support[key])
        self.assertNotEqual(owner['session_id_requested'], support['session_id_requested'])
        for flag in ('--tools', '--allowedTools', '--model', '--effort', '--permission-mode'):
            self.assertEqual(owner['command'][owner['command'].index(flag)+1],
                             support['command'][support['command'].index(flag)+1])
        self.assertTrue(pair.check(self.out)['prepared_inputs_valid'])
        self.assertEqual(sorted(self.seal['order']), ['owner', 'support'])

    def test_unapproved_start_never_imports_runner(self):
        with patch.object(pair.importlib.util, 'spec_from_file_location') as load:
            with self.assertRaisesRegex(ValueError, 'not approved'):
                pair.launch(self.out, self.seal['order'][0])
            load.assert_not_called()
        self.assertFalse(any(self.out.rglob('started.json')))

    def test_budget_or_seal_changes_invalidate_allocation(self):
        self.authorize()
        allocation = pair.read(self.out / 'allocation.json')
        allocation['limits']['nominal_total_usd'] = 99
        pair.write(self.out / 'allocation.json', allocation)
        with self.assertRaisesRegex(ValueError, 'not approved'):
            pair.launch(self.out, self.seal['order'][0])

    def test_readiness_is_bound_to_exact_inputs(self):
        self.authorize()
        pair.write(self.out / 'readiness.json', {'accepted': True, 'seal_sha256': 'stale'})
        with self.assertRaisesRegex(ValueError, 'stale'):
            pair.launch(self.out, self.seal['order'][0])

    def test_source_prompt_and_extra_workspace_file_drift(self):
        self.protocol.write_text('changed protocol')
        (self.out / 'owner/prompt.txt').write_text('changed prompt')
        (self.out / 'support/workspace/extra.txt').write_text('unexpected')
        errors = pair.check(self.out)['errors']
        self.assertTrue(any('source differs' in e for e in errors))
        self.assertTrue(any('input differs' in e for e in errors))
        self.assertIn('initial workspace differs: support', errors)

    def test_runtime_drift(self):
        with patch.object(pair, 'environment', return_value={}):
            self.assertIn('runtime/config/capability inventory differs', pair.check(self.out)['errors'])

    def test_repeat_and_out_of_order_refuse_before_runner(self):
        self.authorize()
        first, second = self.seal['order']
        with self.assertRaises(FileNotFoundError):
            pair.launch(self.out, second)
        pair.write(self.out / first / 'started.json', {'test': True})
        with self.assertRaisesRegex(ValueError, 'already started'):
            pair.launch(self.out, first)

    def test_second_requires_terminal_checks_and_frozen_peer_evidence(self):
        self.authorize()
        first, second = self.seal['order']
        peer = self.out / first
        pair.write(peer / 'terminal.json', {'terminal_checks': {}, 'artifacts': {}})
        pair.write(peer / 'continuation.json', {'measurement_valid': True, 'reviewer': 'test',
            'checks': dict.fromkeys(pair.CONTINUATION_CHECKS, True),
            'terminal_sha256': pair.sha(peer / 'terminal.json')})
        with self.assertRaisesRegex(ValueError, 'not independently accepted'):
            pair.launch(self.out, second)
        evidence = peer / 'trace.jsonl'
        evidence.write_text('original')
        pair.write(peer / 'terminal.json', {'terminal_checks': dict.fromkeys(
            ('execution_success','cleanup_verified','capture_complete'), True),
            'artifacts': {'trace.jsonl': pair.sha(evidence)}})
        pair.write(peer / 'continuation.json', {'measurement_valid': True, 'reviewer': 'test',
            'checks': dict.fromkeys(pair.CONTINUATION_CHECKS, True),
            'terminal_sha256': pair.sha(peer / 'terminal.json')})
        evidence.write_text('changed')
        with self.assertRaisesRegex(ValueError, 'peer evidence changed'):
            pair.launch(self.out, second)


if __name__ == '__main__':
    unittest.main()
