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

if __name__ == '__main__': unittest.main()
