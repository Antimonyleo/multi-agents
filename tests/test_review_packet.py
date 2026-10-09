import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('review_packet', ROOT / 'scripts/review_packet.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PacketTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='workflow-packet-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.log = self.root / 'test-output.txt'
        self.log.write_text('test result evidence')
        self.packet = {
            'phase': 'completion', 'question': 'Does the scoped change meet its named checks?',
            'scope': 'workflow maintenance only', 'stop_boundary': 'review only, no execution',
            'artifacts': [{'path': self.log.name, 'sha256': hashlib.sha256(self.log.read_bytes()).hexdigest()}],
            'required_checks': ['unit'],
            'checks': [{'name': 'unit', 'status': 'passed', 'evidence': self.log.name}]
        }

    def check(self, expected=True):
        result = MODULE.check_packet(self.packet, self.root)
        self.assertEqual(result['packet_complete_for_phase'], expected, result)
        self.assertEqual(result['gate_decision'], 'not_evaluated')
        return result

    def test_complete_packet_binds_exact_evidence(self):
        self.check()

    def test_missing_terminal_result_blocks_completion(self):
        self.packet['checks'][0]['status'] = 'running'
        self.check(False)

    def test_missing_required_check_blocks_review(self):
        self.packet['required_checks'].append('broad')
        self.check(False)

    def test_changed_artifact_is_detected(self):
        self.log.write_text('later evidence')
        self.check(False)

    def test_missing_artifact_is_detected(self):
        self.log.unlink()
        self.check(False)

    def test_planning_does_not_require_experiment_already_run(self):
        self.packet['phase'] = 'plan'
        self.packet['checks'][0] = {'name': 'unit', 'status': 'planned'}
        self.check()

    def test_blocking_review_explicitly_acknowledges_missing_results(self):
        self.packet['phase'] = 'blocking'
        self.packet['checks'][0]['status'] = 'pending'
        self.check(False)
        self.packet['acknowledged_missing'] = ['unit']
        self.check()

    def test_acknowledgement_does_not_certify_readiness(self):
        self.packet['phase'] = 'readiness'
        self.packet['checks'][0]['status'] = 'running'
        self.packet['acknowledged_missing'] = ['unit']
        self.check(False)

    def test_failure_evidence_is_complete_but_not_accepted(self):
        self.packet['checks'][0]['status'] = 'failed'
        self.assertEqual(self.check()['observed_nonpassing_checks'], ['unit'])

    def test_skip_requires_reason_and_evidence(self):
        self.packet['checks'][0]['status'] = 'skipped'
        self.check(False)
        self.packet['checks'][0]['reason'] = 'authorized exclusion'
        self.check()

    def test_terminal_evidence_cannot_be_unbound_file(self):
        unbound = self.root / 'unbound.log'
        unbound.write_text('not in versioned artifacts')
        self.packet['checks'][0]['evidence'] = unbound.name
        self.check(False)

    def test_duplicate_names_and_unknown_status_rejected(self):
        self.packet['checks'].append(copy.deepcopy(self.packet['checks'][0]))
        self.check(False)
        self.packet['checks'].pop()
        self.packet['checks'][0]['status'] = 'looks good'
        self.check(False)

    def test_invalid_structure_reports_errors(self):
        for packet in (None, [], {}, {'phase': [], 'artifacts': [None], 'checks': [None]}):
            self.assertFalse(MODULE.check_packet(packet, self.root)['packet_complete_for_phase'])

    def test_nonstring_status_reports_error(self):
        self.packet['checks'][0]['status'] = ['passed']
        self.check(False)

    def test_directory_cannot_be_an_artifact(self):
        self.packet['artifacts'][0]['path'] = '.'
        self.check(False)

    def test_cli_is_read_only_and_returns_nonzero_for_incomplete_packet(self):
        path = self.root / 'packet.json'
        path.write_text(json.dumps(self.packet))
        before = {p.name:p.read_bytes() for p in self.root.iterdir()}
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/review_packet.py'), str(path)],capture_output=True,text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(before, {p.name:p.read_bytes() for p in self.root.iterdir()})
        self.packet['checks'][0]['status'] = 'pending'
        path.write_text(json.dumps(self.packet))
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/review_packet.py'), str(path)],capture_output=True,text=True)
        self.assertEqual(result.returncode, 1)

    def test_bad_json_cli_reports_incomplete(self):
        path = self.root / 'packet.json'
        path.write_text('{')
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/review_packet.py'), str(path)],capture_output=True,text=True)
        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)['packet_complete_for_phase'])


if __name__ == '__main__':
    unittest.main()
