import copy
import importlib.util
import tempfile
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('native_calibration', Path(__file__).resolve().parents[1] / 'scripts/native_calibration.py')
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)


class CalibrationTest(unittest.TestCase):
    def test_independent_raw_truth(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / 'fixture'
            generated = native.build_fixture(root)
            self.assertEqual(generated, native.reference(root))
            self.assertEqual(len(generated['entries']), 96)
            self.assertTrue(native.score(generated, generated))
            for mutate in ('omitted', 'unsorted', 'wrong', 'duplicate', 'type'):
                bad = copy.deepcopy(generated)
                if mutate == 'omitted': bad['entries'].pop()
                elif mutate == 'unsorted': bad['entries'].reverse()
                elif mutate == 'wrong': bad['entries'][0]['revision'] += 3
                elif mutate == 'duplicate': bad['entries'][1] = bad['entries'][0]
                else: bad['entries'][0]['revision'] = str(bad['entries'][0]['revision'])
                self.assertFalse(native.score(bad, generated), mutate)

    def test_prose_fixture_raw_truth(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / 'fixture'
            generated = native.build_prose_fixture(root)
            self.assertEqual(generated, native.prose_reference(root))
            self.assertEqual(len(generated['entries']), 40)
            self.assertTrue(native.score(generated, generated))
            # Distractors must never be the answer: withdrawn/pending/draft labels are excluded.
            self.assertFalse({'label-withdrawn', 'label-pending', 'label-older'} & {e['label'] for e in generated['entries']})
            bad = copy.deepcopy(generated)
            bad['entries'][0]['revision'] += 2
            self.assertFalse(native.score(bad, generated))

    def test_codex_cumulative_snapshots_not_added(self):
        trace = [{'type': 'session_meta', 'payload': {'id': 'parent'}},
                 {'type': 'turn_context', 'payload': {'model': 'gpt-6.1-sol', 'effort': 'high'}}]
        for n in (10, 20, 20):
            trace.append({'type': 'event_msg', 'payload': {'type': 'token_count', 'info': {'total_token_usage': {'input_tokens': n}}}})
        result = native.normalize('codex', [{'type': 'turn.completed', 'usage': {'input_tokens': 20}}], [trace])
        self.assertEqual(result['thread_usage'][0]['usage_last_cumulative']['input_tokens'], 20)
        self.assertFalse(result['net_cost_claim_supported'])

    def test_codex_compaction_usage_kept_separate_from_event_snapshot(self):
        before = {'input_tokens': 100, 'output_tokens': 10}
        compact = {'input_tokens': 30, 'output_tokens': 5}
        total = {'input_tokens': 130, 'output_tokens': 15}
        record = {'type': 'token_usage_record', 'payload': {
            'response_id': 'compact', 'usage': compact, 'thread_token_usage': total}}
        trace = [{'type': 'session_meta', 'payload': {'id': 'parent'}},
                 {'type': 'event_msg', 'payload': {'type': 'token_count', 'info': {'total_token_usage': before}}},
                 record, record,
                 {'type': 'compacted', 'payload': {'compaction_response_id': 'compact'}}]
        result = native.normalize('codex', [], [trace])
        usage = result['thread_usage'][0]
        self.assertEqual(usage['usage_last_cumulative'], before)
        self.assertEqual(usage['usage_last_record_cumulative'], total)
        self.assertEqual(usage['compaction_response_usage'], {'compact': compact})
        self.assertTrue(usage['compaction_usage_complete'])
        self.assertIsNone(result['usable_provider_usage'])
        self.assertFalse(result['net_cost_claim_supported'])

    def test_codex_missing_compaction_record_is_unknown(self):
        trace = [{'type': 'compacted', 'payload': {'compaction_response_id': 'missing'}}]
        usage = native.normalize('codex', [], [trace])['thread_usage'][0]
        self.assertIsNone(usage['usage_last_record_cumulative'])
        self.assertIsNone(usage['compaction_response_usage'])
        self.assertFalse(usage['compaction_usage_complete'])

    def test_codex_conflicting_or_invalid_compaction_usage_is_unknown(self):
        first = {'type': 'token_usage_record', 'payload': {
            'response_id': 'compact', 'usage': {'input_tokens': 30, 'output_tokens': 5}}}
        for changed in ({'input_tokens': 31, 'output_tokens': 5},
                        {'input_tokens': True, 'output_tokens': 5}):
            with self.subTest(changed=changed):
                other = copy.deepcopy(first)
                other['payload']['usage'] = changed
                trace = [first, other, {'type': 'compacted', 'payload': {'compaction_response_id': 'compact'}}]
                usage = native.normalize('codex', [], [trace])['thread_usage'][0]
                self.assertIsNone(usage['compaction_response_usage'])
                self.assertFalse(usage['compaction_usage_complete'])

    def test_codex_legacy_trace_does_not_imply_zero_compaction_cost(self):
        usage = native.normalize('codex', [], [[]])['thread_usage'][0]
        self.assertIsNone(usage['usage_last_record_cumulative'])
        self.assertIsNone(usage['compaction_response_usage'])
        self.assertIsNone(usage['compaction_usage_complete'])

    def test_codex_latest_invalid_record_does_not_reuse_earlier_total(self):
        for last in (None, {}, {'input_tokens': True, 'output_tokens': 0}):
            with self.subTest(last=last):
                trace = [{'type': 'token_usage_record', 'payload': {
                    'thread_token_usage': {'input_tokens': 10, 'output_tokens': 2}}},
                    {'type': 'token_usage_record', 'payload': {'thread_token_usage': last}}]
                usage = native.normalize('codex', [], [trace])['thread_usage'][0]
                self.assertIsNone(usage['usage_last_record_cumulative'])

    def test_codex_invalid_earlier_compaction_usage_stays_unknown(self):
        for invalid in (True, 1.0):
            with self.subTest(invalid=invalid):
                trace = [{'type': 'token_usage_record', 'payload': {
                    'response_id': 'compact', 'usage': {'input_tokens': invalid, 'output_tokens': 0}}},
                    {'type': 'token_usage_record', 'payload': {
                        'response_id': 'compact', 'usage': {'input_tokens': 1, 'output_tokens': 0}}},
                    {'type': 'compacted', 'payload': {'compaction_response_id': 'compact'}}]
                usage = native.normalize('codex', [], [trace])['thread_usage'][0]
                self.assertIsNone(usage['compaction_response_usage'])
                self.assertFalse(usage['compaction_usage_complete'])

    def test_codex_invalid_cache_write_counts_are_unknown(self):
        for invalid in (-1, True, 1.0, '1'):
            with self.subTest(invalid=invalid):
                value = {'input_tokens': 1, 'output_tokens': 0, 'cache_write_input_tokens': invalid}
                trace = [{'type': 'token_usage_record', 'payload': {
                    'response_id': 'compact', 'usage': value, 'thread_token_usage': value}},
                    {'type': 'compacted', 'payload': {'compaction_response_id': 'compact'}}]
                usage = native.normalize('codex', [], [trace])['thread_usage'][0]
                self.assertIsNone(usage['usage_last_record_cumulative'])
                self.assertIsNone(usage['compaction_response_usage'])
                self.assertFalse(usage['compaction_usage_complete'])

    def test_children_never_count_as_zero(self):
        stream = [{'type': 'assistant', 'message': {'model': 'opus', 'content': [
            {'type': 'tool_use', 'name': 'Agent', 'id': 'a', 'input': {'subagent_type': 'scientific_explorer'}}]}},
            {'type': 'result', 'usage': {'input_tokens': 100}, 'total_cost_usd': 0.1, 'modelUsage': {'opus': {'inputTokens': 100}}}]
        result = native.normalize('claude', stream)
        self.assertEqual(result['whole_family_accounting'], 'unverified')
        self.assertFalse(result['net_cost_claim_supported'])
        self.assertEqual(len(result['delegate_calls']), 1)

    def test_parent_child_relationship(self):
        child = [{'type': 'session_meta', 'payload': {'id': 'child', 'agent_role': 'scientific_explorer',
                  'source': {'subagent': {'thread_spawn': {'parent_thread_id': 'parent'}}}}},
                 {'type': 'turn_context', 'payload': {'model': 'gpt-6-luna', 'effort': 'high'}}]
        result = native.normalize('codex', [], [child])
        self.assertEqual(result['native_children'][0]['parent'], 'parent')
        self.assertEqual(result['observed_models'], ['gpt-6-luna'])
        self.assertEqual(result['whole_family_accounting'], 'unverified')

    def test_repeated_message_fragments_do_not_multiply_context_or_tools(self):
        usage = {'input_tokens': 10, 'cache_creation_input_tokens': 20, 'cache_read_input_tokens': 30}
        message = {'type': 'assistant', 'message': {'id': 'message1', 'usage': usage,
                   'content': [{'type': 'tool_use', 'id': 'tool1', 'name': 'Bash', 'input': {}}]}}
        child = copy.deepcopy(message)
        child['parent_tool_use_id'] = 'parent-call'
        child['message']['id'] = 'child-message'
        result = native.normalize('claude', [message, message, child])
        self.assertEqual(result['assistant_response_count'], 1)
        self.assertEqual(result['first_input_context_tokens'], 60)
        self.assertEqual(result['input_tokens_processed_from_messages'], 60)
        self.assertEqual(result['tools']['Bash'], 1)

    def test_missing_response_identity_or_usage_is_unknown(self):
        result = native.normalize('claude', [{'type': 'assistant', 'message': {'content': []}}])
        self.assertIsNone(result['assistant_response_count'])
        self.assertIsNone(result['input_tokens_processed_from_messages'])

    def test_partial_response_telemetry_never_reports_complete_total(self):
        usage = {'input_tokens': 10, 'cache_creation_input_tokens': 20, 'cache_read_input_tokens': 30}
        valid = {'type': 'assistant', 'message': {'id': 'first', 'usage': usage}}
        for missing in ({'usage': usage}, {'id': 'second'}):
            with self.subTest(missing=missing):
                result = native.normalize('claude', [valid, {'type': 'assistant', 'message': missing}])
                self.assertIsNone(result['input_tokens_processed_from_messages'])
                self.assertFalse(result['response_telemetry_complete'])
                if 'id' not in missing:
                    self.assertIsNone(result['assistant_response_count'])

    def test_later_fragment_completes_same_response(self):
        usage = {'input_tokens': 10, 'cache_creation_input_tokens': 20, 'cache_read_input_tokens': 30}
        stream = [{'type': 'assistant', 'message': {'id': 'first'}},
                  {'type': 'assistant', 'message': {'id': 'first', 'usage': usage}},
                  {'type': 'assistant', 'message': {'id': 'first'}}]
        result = native.normalize('claude', stream)
        self.assertEqual(result['input_tokens_processed_from_messages'], 60)
        self.assertEqual(result['assistant_response_count'], 1)
        self.assertTrue(result['response_telemetry_complete'])

    def test_malformed_trace_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'trace.jsonl'
            p.write_text('{bad}\n')
            with self.assertRaises(ValueError): native.events(p)



class CollectorTest(unittest.TestCase):
    def test_sqlite_source_string_does_not_hide_child(self):
        import json
        import sqlite3
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            out = home / 'out'
            out.mkdir()
            state = home / '.codex'
            state.mkdir()
            db = sqlite3.connect(state / 'state_5.sqlite')
            db.execute('create table threads (id text, rollout_path text, source text, cwd text)')
            for ident, parent in [('parent', None), ('child', 'parent'), ('unrelated', None)]:
                path = home / (ident + '.jsonl')
                meta = {'id': ident, 'parent_thread_id': parent}
                path.write_text(json.dumps({'type': 'session_meta', 'payload': meta}) + '\n')
                db.execute('insert into threads values (?, ?, ?, ?)',
                           (ident, str(path), 'subagent' if parent else 'exec', str(out / 'workspace')))
            db.commit()
            db.close()
            with patch.object(native.Path, 'home', return_value=home):
                traces = native.collect_codex(out, [{'type': 'thread.started', 'thread_id': 'parent'}])
            self.assertEqual({t[0]['payload']['id'] for t in traces}, {'parent', 'child'})
            self.assertFalse((out / 'native/unrelated.jsonl').exists())



class PairControlTest(unittest.TestCase):
    def setUp(self):
        from unittest.mock import patch
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / 'home'
        for folder, config in [('.claude', 'settings.json'), ('.codex', 'config.toml')]:
            path = self.home / folder
            (path / 'agents').mkdir(parents=True)
            (path / config).write_text('{}' if folder == '.claude' else '')
        self.home_patch = patch.object(native.Path, 'home', return_value=self.home)
        self.home_patch.start()
        self.addCleanup(self.home_patch.stop)

    def pair(self, provider='claude', comparison='routing', task='inventory'):
        from types import SimpleNamespace
        paths = []
        for arm in ['baseline', 'workflow']:
            out = self.root / (provider + '-' + comparison + '-' + task + '-' + arm)
            native.prepare(SimpleNamespace(output=str(out), provider=provider, arm=arm,
                                           comparison=comparison, task=task, budget_usd=2))
            paths.append(out)
        return paths

    def test_routing_keeps_tool_and_skill_availability_equal(self):
        import json
        a, b = self.pair()
        ma, mb = [json.loads((p / 'manifest.json').read_text()) for p in (a, b)]
        for option in ('--tools', '--allowedTools'):
            self.assertEqual(ma['command'][ma['command'].index(option) + 1],
                             mb['command'][mb['command'].index(option) + 1])
        self.assertEqual(ma['before'], mb['before'])
        self.assertTrue(native.audit_pair(a, b)['controls_match'])

    def test_deployment_difference_is_declared_not_instruction_effect(self):
        a, b = self.pair(comparison='deployment')
        result = native.audit_pair(a, b)
        self.assertTrue(result['controls_match'])
        self.assertTrue(result['declared_capability_differences'])
        self.assertEqual(result['question'], 'capability deployment overhead')
        self.assertFalse(result['savings_claim_supported'])

    def test_command_drift_rejects_even_when_summary_fields_match(self):
        import json
        a, b = self.pair()
        p = b / 'manifest.json'; data = json.loads(p.read_text())
        data['command'][data['command'].index('--model') + 1] = 'sonnet'
        native.write(p, data)
        self.assertFalse(native.audit_pair(a, b)['controls_match'])

    def test_identical_command_tampering_cannot_bypass_declared_controls(self):
        import json
        for provider, option, replacement in [('claude', '--model', 'sonnet'),
                                               ('claude', '--max-budget-usd', '999'),
                                               ('codex', '--cd', '/tmp/unchecked-workspace')]:
            with self.subTest(option=option):
                a, b = self.pair(provider=provider)
                for root in (a, b):
                    p = root / 'manifest.json'; data = json.loads(p.read_text())
                    data['command'][data['command'].index(option) + 1] = replacement
                    native.write(p, data)
                self.assertFalse(native.audit_pair(a, b)['controls_match'])
                import shutil
                shutil.rmtree(a); shutil.rmtree(b)

    def test_new_native_agent_is_detected(self):
        a, b = self.pair()
        (self.home / '.claude/agents/ordinary.md').write_text('new capability')
        self.assertFalse(native.audit_pair(a, b)['controls_match'])

    def test_global_skill_addition_and_change_are_detected(self):
        entry = self.home / '.agents/skills/ordinary/SKILL.md'
        entry.parent.mkdir(parents=True)
        entry.write_text('original')
        a, b = self.pair()
        entry.write_text('changed')
        self.assertFalse(native.audit_pair(a, b)['controls_match'])
        entry.write_text('original')
        added = self.home / '.claude/skills/new/SKILL.md'
        added.parent.mkdir(parents=True)
        added.write_text('new capability')
        self.assertFalse(native.audit_pair(a, b)['controls_match'])

    def test_fixture_drift_is_caught_before_inference(self):
        a, b = self.pair()
        (b / 'workspace/inventory/group_00/component_000.json').write_text('{}')
        result = native.audit_pair(a, b)
        self.assertFalse(result['controls_match'])
        self.assertTrue(any('workspace' in e for e in result['errors']))

    def test_prose_fixture_keeps_its_existing_reference(self):
        a, b = self.pair(task='prose')
        result = native.audit_pair(a, b)
        self.assertTrue(result['controls_match'])
        self.assertIn('not evidence of implementation or review benefit', result['limitations'])

    def test_codex_pair_and_unequal_budget(self):
        import json
        a, b = self.pair(provider='codex')
        self.assertTrue(native.audit_pair(a, b)['controls_match'])
        p = b / 'manifest.json'; data = json.loads(p.read_text())
        data['timeout_s'] += 10
        native.write(p, data)
        self.assertFalse(native.audit_pair(a, b)['controls_match'])

    def test_run_requires_peer_before_importing_runner(self):
        from unittest.mock import patch
        a, _ = self.pair()
        with patch.object(native.importlib.util, 'spec_from_file_location',
                          side_effect=AssertionError('runner import before pair guard')):
            with self.assertRaisesRegex(ValueError, 'peer'):
                native.run(a)

    def test_peer_missing_usage_stops_before_runner_import(self):
        from unittest.mock import patch
        a, b = self.pair()
        (b / 'trace.jsonl').write_text('{}\n')
        native.write(b / 'execution.json', {'returncode': 0, 'timed_out': False})
        native.write(b / 'metrics.json', {'checks': {'terminal_success': True,
                     'workspace_unchanged': True, 'usage_present': False, 'support_cap': True}})
        with patch.object(native.importlib.util, 'spec_from_file_location',
                          side_effect=AssertionError('runner imported after missing peer telemetry')):
            with self.assertRaisesRegex(ValueError, 'usage_present'):
                native.run(a, b)

    def test_legacy_pair_cannot_certify_matched_routing(self):
        import json
        a, b = self.pair()
        for root in (a, b):
            p = root / 'manifest.json'; data = json.loads(p.read_text())
            data.pop('comparison', None)
            native.write(p, data)
        self.assertFalse(native.audit_pair(a, b)['controls_match'])

if __name__ == '__main__': unittest.main()
