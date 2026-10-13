import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('implementation_fixture', Path(__file__).resolve().parents[1] / 'scripts/implementation_fixture.py')
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)


class ImplementationFixtureTests(unittest.TestCase):
    def setUp(self):
        scratch = Path(os.environ.get('TMPDIR', '/home/hao/.cache/codex-scratch'))
        scratch.mkdir(parents=True, exist_ok=True)
        self.root = Path(tempfile.mkdtemp(prefix='task.', dir=scratch))
        self.count = 0

    def workspace(self):
        self.count += 1
        workspace = self.root / str(self.count)
        metadata = fixture.build(workspace)
        return workspace, metadata

    def public(self, workspace):
        return subprocess.run([sys.executable, '-I', '-B', '-c',
            'import sys,unittest;sys.path.insert(0,sys.argv[1]);s=unittest.defaultTestLoader.discover(sys.argv[1]+"/tests");r=unittest.TextTestRunner(verbosity=2).run(s);sys.exit(not r.wasSuccessful())',
            str(workspace)], capture_output=True, text=True, timeout=10)

    def test_build_metadata_and_hidden_material_separation(self):
        workspace, metadata = self.workspace()
        self.assertEqual(metadata['writable_paths'], ['durations.py', 'attempts.py', 'report.py'])
        self.assertEqual(metadata['public_command'], ['python', '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-v'])
        self.assertEqual(metadata['fixture_sha256'], hashlib.sha256(json.dumps(fixture.FILES, sort_keys=True).encode()).hexdigest())
        for path in workspace.rglob('*'):
            if path.is_file():
                self.assertNotIn('ORACLES', path.read_text())
                self.assertNotIn('REFERENCE', path.read_text())
        self.assertIn('D1: Duration values', metadata['retrieval_task'])
        self.assertIn('A2: Final state', metadata['retrieval_task'])
        self.assertIn('A3: Unknown', metadata['retrieval_task'])
        self.assertNotIn('125.125', ''.join(p.read_text() for p in workspace.rglob('*') if p.is_file()))
        with self.assertRaises(FileExistsError):
            fixture.build(workspace)

    def test_initial_broken_modules_fail_public_and_hidden_checks(self):
        workspace, _ = self.workspace()
        self.assertNotEqual(self.public(workspace).returncode, 0)
        checks = fixture.validate(workspace)
        self.assertFalse(all(checks.values()))
        self.assertFalse(checks['mixed_units_zero_unknown_final'])
        self.assertFalse(checks['known_retry_work'])
        self.assertFalse(checks['invalid_record_0'])

    def test_independent_reference_passes_all_explicit_oracles_and_public_tests(self):
        workspace, _ = self.workspace()
        fixture.install_reference(workspace)
        run = self.public(workspace)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn('Ran 4 tests', run.stderr)
        checks = fixture.validate(workspace)
        self.assertTrue(all(checks.values()), checks)
        self.assertGreaterEqual(len(checks), 25)
        # Direct literal oracle inspection verifies the intended denominators and units.
        mixed = copy.deepcopy(fixture.ORACLES[1][2])
        self.assertEqual(mixed['totals'], {'jobs': 3, 'successful_jobs': 1, 'failed_jobs': 1,
            'stopped_jobs': 1, 'known_duration_ms': 125.125, 'duration_ms': None, 'unknown_attempts': 1})
        self.assertEqual(mixed['jobs'][1]['last_attempt'], 9)
        self.assertEqual(mixed['jobs'][1]['attempts'], 2)

    def test_module_mutants_fail_meaningful_hidden_cases(self):
        mutants = [
            ('millisecond_scale', 'durations.py', 'value if unit == "ms" else value * 1000', 'value / 1000 if unit == "ms" else value * 1000', 'mixed_units_zero_unknown_final'),
            ('boolean_numeric', 'durations.py', 'type(value) not in (int, float)', 'not isinstance(value, (int, float))', 'invalid_record_0'),
            ('unknown_to_zero', 'durations.py', 'if duration is None:\n        return None', 'if duration is None:\n        return 0', 'all_unknown'),
            ('input_order_final', 'attempts.py', 'if attempt > row["last_attempt"]:', 'if True:', 'known_retry_work'),
            ('final_success_bias', 'attempts.py', 'if attempt > row["last_attempt"]:', 'if attempt > row["last_attempt"] or status == "success":', 'mixed_units_zero_unknown_final'),
            ('deduplicate_silently', 'attempts.py', 'raise ValueError("duplicate")', 'continue', 'duplicate_identity'),
            ('insertion_order', 'attempts.py', 'return sorted(groups.values(), key=lambda row: row["job"])', 'return list(groups.values())', 'mixed_units_zero_unknown_final'),
            ('report_rounding', 'report.py', 'known = sum(row["known_duration_ms"] for row in rows)', 'known = round(sum(row["known_duration_ms"] for row in rows), 2)', 'mixed_units_zero_unknown_final'),
        ]
        for name, module, before, after, check in mutants:
            with self.subTest(mutant=name):
                workspace, _ = self.workspace()
                fixture.install_reference(workspace)
                path = workspace / module
                self.assertIn(before, path.read_text())
                path.write_text(path.read_text().replace(before, after))
                self.assertFalse(fixture.validate(workspace)[check], name)

    def test_raw_probe_receipts_preserve_evidence_and_stay_outside_workspace(self):
        workspace, _ = self.workspace()
        fixture.install_reference(workspace)
        evidence = self.root / 'oracle-probes.json'
        checks = fixture.validate(workspace, evidence_path=evidence)
        receipt = json.loads(evidence.read_text())
        self.assertEqual(receipt['checks'], checks)
        self.assertEqual(len(receipt['probes']), len(checks))
        probe = next(p for p in receipt['probes'] if p['name'] == 'mixed_units_zero_unknown_final')
        self.assertEqual(probe['payload'], fixture.ORACLES[1][1])
        self.assertEqual(probe['expected'], fixture.ORACLES[1][2])
        self.assertEqual(probe['actual'], probe['expected'])
        self.assertEqual(probe['returncode'], 0)
        self.assertEqual(json.loads(probe['stdout']), probe['actual'])
        self.assertEqual(probe['stderr'], '')
        with self.assertRaises(ValueError):
            fixture.validate(workspace, evidence_path=workspace / 'leaked-truth.json')
        self.assertFalse((workspace / 'leaked-truth.json').exists())
        # Native program failure remains raw evidence, not an absent observation.
        (workspace / 'report.py').write_text('import sys;print("untrusted stdout");print("failure detail", file=sys.stderr);sys.exit(7)')
        fixture.validate(workspace, evidence_path=evidence)
        failed = json.loads(evidence.read_text())['probes'][0]
        self.assertEqual(failed['returncode'], 7)
        self.assertEqual(failed['stdout'], 'untrusted stdout\n')
        self.assertEqual(failed['stderr'], 'failure detail\n')
        self.assertIsNone(failed['actual'])
        self.assertFalse(failed['passed'])

    def test_correct_cli_facade_does_not_mask_broken_documented_normalize_api(self):
        workspace, _ = self.workspace()
        fixture.install_reference(workspace)
        duration = workspace / 'durations.py'
        duration.write_text(duration.read_text() + '\ngood_normalize = normalize\ndef normalize(duration):\n    return 999\n')
        attempts = workspace / 'attempts.py'
        attempts.write_text(attempts.read_text().replace('from durations import normalize',
                                                        'from durations import good_normalize as normalize'))
        checks = fixture.validate(workspace)
        for name, _, _ in fixture.ORACLES:
            self.assertTrue(checks[name], name)
        self.assertFalse(checks['normalize_api_zero'])
        self.assertFalse(checks['normalize_api_unknown'])
        self.assertFalse(checks['normalize_api_invalid_0'])

    def test_import_probes_reject_output_and_stdin_consumption(self):
        for side_effect in ('print("unexpected")', 'import sys;sys.stdin.read()'):
            with self.subTest(side_effect=side_effect):
                workspace, _ = self.workspace()
                fixture.install_reference(workspace)
                path = workspace / 'durations.py'
                path.write_text(path.read_text() + '\n' + side_effect + '\n')
                probe = fixture._probe(workspace, None, entrypoint='imports')
                self.assertNotEqual(probe['returncode'], 0)
                self.assertIn('RuntimeError', probe['stderr'])

    def test_hidden_validation_preserves_workspace_and_bool_is_not_numeric_output(self):
        workspace, _ = self.workspace()
        fixture.install_reference(workspace)
        before = {p.relative_to(workspace).as_posix(): p.read_bytes() for p in workspace.rglob('*') if p.is_file()}
        self.assertTrue(all(fixture.validate(workspace).values()))
        after = {p.relative_to(workspace).as_posix(): p.read_bytes() for p in workspace.rglob('*') if p.is_file()}
        self.assertEqual(before, after)
        self.assertFalse(fixture._equal({'number': True}, {'number': 1}))
        self.assertFalse(fixture._equal({'number': float('inf')}, {'number': 1}))


if __name__ == '__main__':
    unittest.main()
