import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('permission_native', Path(__file__).resolve().parents[1] / 'scripts/native_calibration.py')
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)


class PermissionProbeTest(unittest.TestCase):
    def probe(self, *, command=None, error=True, denial=True, read=True):
        inputs = {'command': command or native.PERMISSION_COMMAND}
        stream = [
            {'type': 'assistant', 'message': {'content': [
                {'type': 'tool_use', 'id': 'bash', 'name': 'Bash', 'input': inputs}]}},
            {'type': 'user', 'message': {'content': [
                {'type': 'tool_result', 'tool_use_id': 'bash', 'is_error': error, 'content': 'opaque runtime output'}]}},
            {'type': 'result', 'permission_denials': [
                {'tool_name': 'Bash', 'tool_use_id': 'bash', 'tool_input': inputs}] if denial else []},
        ]
        if read:
            stream += [
                {'type': 'assistant', 'message': {'content': [{'type': 'tool_use', 'id': 'read', 'name': 'Read', 'input': {'file_path': '/fixture/input.json'}}]}},
                {'type': 'user', 'message': {'content': [{'type': 'tool_result', 'tool_use_id': 'read', 'content': 'file content'}]}},
            ]
        return stream

    def assess(self, stream):
        return native.permission_probe(stream, Path('/fixture'), {'command': native.PERMISSION_COMMAND, 'read_path': 'input.json'})

    def test_exact_native_denial_and_allowed_read(self):
        self.assertEqual(self.assess(self.probe())['status'], 'verified')

    def test_missing_attempt_or_model_claim_is_unknown(self):
        self.assertEqual(self.assess([])['status'], 'unverified')
        self.assertEqual(self.assess([{'message': {'content': [{'type': 'text', 'text': 'The command was denied.'}]}}])['status'], 'unverified')

    def test_altered_command_and_unrelated_error_are_unknown(self):
        self.assertEqual(self.assess(self.probe(command='printf OTHER'))['status'], 'unverified')
        self.assertEqual(self.assess(self.probe(denial=False))['status'], 'unverified')

    def test_success_fails_even_if_final_claims_denial(self):
        self.assertEqual(self.assess(self.probe(error=False))['status'], 'failed')

    def test_allowed_read_and_parent_scope_are_required(self):
        self.assertEqual(self.assess(self.probe(read=False))['status'], 'unverified')
        stream=self.probe()
        stream[0]['parent_tool_use_id']='helper'
        self.assertEqual(self.assess(stream)['status'], 'unverified')

    def test_conflicting_call_and_duplicate_attempt_not_accepted(self):
        stream=self.probe()
        stream.append({'type': 'assistant', 'message': {'content': [{'type': 'tool_use', 'id': 'bash', 'name': 'Bash', 'input': {'command': 'other'}}]}})
        self.assertEqual(self.assess(stream)['status'], 'unverified')

    def test_malformed_shapes_leave_enforcement_unknown(self):
        for stream in ([None], [{'message': 'bad'}], [{'message': {'content': None}}],
                       [{'type': 'result', 'permission_denials': None}],
                       [{'tool_result_meta': None}]):
            with self.subTest(stream=stream):
                self.assertEqual(self.assess(stream)['status'], 'unverified')
        stream=self.probe()
        stream[2]['permission_denials'][0]['tool_input']='bad'
        self.assertEqual(self.assess(stream)['status'], 'unverified')
        stream=self.probe()
        stream.append({'type': 'assistant', 'message': {'content': [{'type': 'tool_use', 'id': 'other', 'name': 'Bash', 'input': {'command': native.PERMISSION_COMMAND}}]}})
        self.assertEqual(self.assess(stream)['status'], 'unverified')

    def test_native_event_origin_and_read_evidence_required(self):
        stream = self.probe()
        del stream[-1]['message']['content'][0]['content']
        self.assertEqual(self.assess(stream)['status'], 'unverified')
        stream = self.probe()
        stream[-1]['tool_result_meta'] = [{'id': 'read', 'permission_decision': {'decision': 'deny'}}]
        self.assertEqual(self.assess(stream)['status'], 'unverified')
        stream = self.probe()
        stream[1]['type'] = 'assistant'
        self.assertEqual(self.assess(stream)['status'], 'unverified')

    def test_native_system_permission_notification_does_not_erase_results(self):
        stream = self.probe()
        stream.insert(1, {'type': 'system', 'subtype': 'permission_denied', 'message': 'A scoped rule denied this command.'})
        self.assertEqual(self.assess(stream)['status'], 'verified')
        stream.append({'type': 'result', 'is_error': False, 'usage': {'input_tokens': 0, 'output_tokens': 0}})
        metrics = native.normalize('claude', stream)
        self.assertTrue(metrics['provider_telemetry_complete'])
        self.assertTrue(metrics['provider_terminal_complete'])


if __name__ == '__main__':
    unittest.main()
