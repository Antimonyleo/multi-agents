"""Current Codex accounting through the monitor's public measurement interface."""
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    'long_task_monitor_current', ROOT / 'scripts/long_task_monitor.py')
MONITOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MONITOR)
CASES = {'modern': {'type': 'token_usage_record',
            'timestamp': '2026-10-17T10:02:00Z',
            'payload': {'thread_token_usage': {'input_tokens': 200,
                                               'cached_input_tokens': 150,
                                               'output_tokens': 20,
                                               'total_tokens': 220},
                        'usage': {'input_tokens': 999, 'output_tokens': 999}}},
 'legacy': {'type': 'event_msg',
            'timestamp': '2026-10-17T10:01:00Z',
            'payload': {'type': 'token_count',
                        'info': {'total_token_usage': {'input_tokens': 100,
                                                       'cached_input_tokens': 80,
                                                       'output_tokens': 10,
                                                       'total_tokens': 110},
                                 'last_token_usage': {'input_tokens': 100}}}}}
PARENT = '11111111-2222-3333-4444-555555555555'
CHILD = 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
GRANDCHILD = '99999999-8888-7777-6666-555555555555'
FIELDS = ('input_tokens', 'cached_input_tokens', 'output_tokens', 'total_tokens')


def modern(**changes):
    record = copy.deepcopy(CASES['modern'])
    record['payload']['thread_token_usage'].update(changes)
    return record


def legacy(**changes):
    record = copy.deepcopy(CASES['legacy'])
    record['payload']['info']['total_token_usage'].update(changes)
    return record


class CurrentCodexMonitorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='workflow-current-monitor-')
        self.addCleanup(self.temp.cleanup)
        self.codex_root = Path(self.temp.name) / 'codex'
        self.day = self.codex_root / '2026' / '10' / '17'
        self.day.mkdir(parents=True)

    def session(self, records, sid=PARENT, parent=None):
        payload = {'id': sid}
        if parent is not None:
            payload['parent_thread_id'] = parent
        path = self.day / f'rollout-2026-10-17T10-00-00-{sid}.jsonl'
        meta = {'type': 'session_meta', 'timestamp': '2026-10-17T10:00:00Z',
                'payload': payload}
        path.write_text(''.join(json.dumps(r) + '\n' for r in [meta, *records]))
        return path

    def measure(self, records):
        return MONITOR.measure('codex', self.session(records), self.codex_root)

    def assert_tokens(self, result, source, new, processed):
        self.assertEqual(result['token_source'], source)
        self.assertEqual(result['token_status'], 'valid')
        self.assertEqual(result['new_tokens'], new)
        self.assertEqual(result['processed_tokens'], processed)

    def assert_unknown(self, result):
        self.assertEqual(result['token_source'], 'unknown')
        self.assertEqual(result['token_status'], 'unknown')
        self.assertIsNone(result['new_tokens'])
        self.assertIsNone(result['processed_tokens'])
        self.assertIsNone(result['helper_share_new'])

    def test_native_and_legacy_duplicates_select_native_once(self):
        result = self.measure([legacy(), modern(), modern(), legacy()])
        self.assert_tokens(result, 'native_thread_cumulative', 70, 220)
        self.assertEqual(result['helpers'], 0)
        self.assertIsNone(result['helper_share_new'])

    def test_modern_only_uses_latest_cumulative_not_response_usage(self):
        later = modern(input_tokens=300, cached_input_tokens=200,
                       output_tokens=30, total_tokens=330)
        later['timestamp'] = '2026-10-17T10:03:00Z'
        result = self.measure([modern(), later])
        self.assert_tokens(result, 'native_thread_cumulative', 130, 330)

    def test_valid_legacy_only_preserves_latest_totals(self):
        later = legacy(input_tokens=300, cached_input_tokens=200,
                       output_tokens=30, total_tokens=330)
        later['timestamp'] = '2026-10-17T10:03:00Z'
        self.assert_tokens(self.measure([legacy(), later]), 'legacy_cumulative', 130, 330)

    def test_native_reasoning_is_already_in_output(self):
        result = self.measure([modern(reasoning_output_tokens=15)])
        self.assert_tokens(result, 'native_thread_cumulative', 70, 220)

    def test_zero_cumulative_is_valid_for_both_formats(self):
        for factory, source in ((modern, 'native_thread_cumulative'),
                                (legacy, 'legacy_cumulative')):
            with self.subTest(source=source):
                result = self.measure([factory(input_tokens=0, cached_input_tokens=0,
                                               output_tokens=0, total_tokens=0)])
                self.assert_tokens(result, source, 0, 0)

    def test_required_fields_reject_noninteger_negative_and_bool_values(self):
        for factory in (modern, legacy):
            for field in FIELDS:
                for value in (True, False, -1, 1.5, '10', None):
                    with self.subTest(format=factory.__name__, field=field, value=value):
                        self.assert_unknown(self.measure([factory(**{field: value})]))

    def test_missing_required_fields_are_unknown(self):
        for factory in (modern, legacy):
            for field in FIELDS:
                record = factory()
                tokens = (record['payload']['thread_token_usage'] if factory is modern
                          else record['payload']['info']['total_token_usage'])
                del tokens[field]
                with self.subTest(format=factory.__name__, field=field):
                    self.assert_unknown(self.measure([record]))

    def test_invalid_cached_and_total_relationships_are_unknown(self):
        for factory in (modern, legacy):
            for changes in ({'cached_input_tokens': 1000}, {'total_tokens': 999}):
                with self.subTest(format=factory.__name__, changes=changes):
                    self.assert_unknown(self.measure([factory(**changes)]))

    def test_malformed_latest_native_never_falls_back(self):
        for value in (None, {}, [], 'invalid'):
            bad = modern()
            bad['timestamp'] = '2026-10-17T10:03:00Z'
            bad['payload']['thread_token_usage'] = value
            with self.subTest(value=value):
                self.assert_unknown(self.measure([legacy(), modern(), bad]))
        missing = modern()
        del missing['payload']['thread_token_usage']
        self.assert_unknown(self.measure([legacy(), modern(), missing]))

    def test_latest_regressing_native_is_unknown_even_with_legacy(self):
        regressed = modern(input_tokens=100, cached_input_tokens=80,
                           output_tokens=10, total_tokens=110)
        regressed['timestamp'] = '2026-10-17T10:03:00Z'
        self.assert_unknown(self.measure([legacy(), modern(), regressed]))

    def test_no_usable_telemetry_is_unknown(self):
        response_only = {'type': 'response_item', 'timestamp': '2026-10-17T10:02:00Z',
                         'payload': {'type': 'message', 'role': 'assistant',
                                     'content': [], 'usage': {'input_tokens': 999,
                                                              'output_tokens': 999}}}
        for records in ([], [response_only]):
            with self.subTest(records=records):
                self.assert_unknown(self.measure(records))

    def test_parent_and_descendants_sum_each_canonical_source_once(self):
        path = self.session([legacy(), modern()])
        self.session([legacy()], CHILD, PARENT)
        self.session([legacy(), modern()], GRANDCHILD, CHILD)
        result = MONITOR.measure('codex', path, self.codex_root)
        self.assert_tokens(result, 'mixed', 170, 550)
        self.assertEqual(result['helpers'], 2)
        self.assertAlmostEqual(result['helper_share_new'], 100 / 170)

    def test_unknown_parent_or_child_makes_family_unknown(self):
        for parent_records, child_records in (([modern()], []), ([], [legacy()])):
            with self.subTest(parent_records=parent_records, child_records=child_records):
                path = self.session(parent_records)
                self.session(child_records, CHILD, PARENT)
                result = MONITOR.measure('codex', path, self.codex_root)
                self.assert_unknown(result)
                self.assertEqual(result['helpers'], 1)

    def test_unknown_compare_show_and_cli_json_are_safe(self):
        path = self.session([])
        result = MONITOR.measure('codex', path, self.codex_root)
        self.assert_unknown(result)
        table = MONITOR.compare(result)
        helper_row = next(row for row in table if row['measure'] == 'helper_share_new')
        self.assertIsNone(helper_row['session'])
        self.assertIsNone(helper_row['below'])
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            MONITOR.show(result, table)
        self.assertRegex(stream.getvalue().lower(),
                         r'(?:unknown|—) new / (?:unknown|—) processed tokens')
        output = Path(self.temp.name) / 'result.json'
        original_measure = MONITOR.measure
        with mock.patch.object(MONITOR, 'find_session', return_value=('codex', path)), \
                mock.patch.object(MONITOR, 'measure', side_effect=lambda runtime, transcript:
                                  original_measure(runtime, transcript, self.codex_root)), \
                mock.patch('sys.argv', ['long_task_monitor.py', PARENT, '--json', str(output)]), \
                contextlib.redirect_stdout(io.StringIO()):
            MONITOR.main()
        saved = json.loads(output.read_text())
        self.assert_unknown(saved['result'])
        self.assertEqual(saved['baseline'], table)


if __name__ == '__main__':
    unittest.main()
