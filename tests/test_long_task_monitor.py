import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('long_task_monitor', ROOT / 'scripts/long_task_monitor.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

CLAUDE_ID = '11111111-2222-3333-4444-555555555555'
CODEX_ID = '0aaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
CHILD_ID = '0fffffff-bbbb-cccc-dddd-eeeeeeeeeeee'


def write_jsonl(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(''.join(json.dumps(r) + '\n' for r in records))


def stamp(minute):
    return f'2026-10-13T10:{minute:02d}:00Z'


def assistant(minute, mid, usage, content):
    return dict(type='assistant', timestamp=stamp(minute),
                message=dict(id=mid, model='claude-opus-5-5', usage=usage, content=content))


def token_count(minute, total, last_input):
    return dict(type='event_msg', timestamp=stamp(minute),
                payload=dict(type='token_count', info=dict(total_token_usage=total,
                                                           last_token_usage=dict(input_tokens=last_input))))


class MonitorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='workflow-monitor-')
        self.addCleanup(self.temp.cleanup)
        self.claude_root = Path(self.temp.name) / 'claude'
        self.codex_root = Path(self.temp.name) / 'codex'
        self.codex_root.mkdir()
        self.claude_root.mkdir()

    def test_claude_session_counts_polling_helpers_and_stop_candidates(self):
        parent = self.claude_root / 'project' / f'{CLAUDE_ID}.jsonl'
        write_jsonl(parent, [
            dict(type='user', timestamp=stamp(0), message=dict(role='user', content='Run every step; do not stop.')),
            assistant(1, 'm1', dict(input_tokens=10, cache_creation_input_tokens=100, cache_read_input_tokens=1000,
                                    output_tokens=5),
                      [dict(type='tool_use', id='t1', name='Bash', input=dict(command='sleep 60; date'))]),
            dict(type='user', timestamp=stamp(2), message=dict(role='user', content=[
                dict(type='tool_result', tool_use_id='t1', content='ok')])),
            assistant(3, 'm2', dict(input_tokens=1, cache_creation_input_tokens=0, cache_read_input_tokens=0,
                                    output_tokens=1), [dict(type='text', text='Done.')]),
        ])
        child = parent.parent / CLAUDE_ID / 'subagents' / 'agent-a1.jsonl'
        write_jsonl(child, [assistant(1, 'c1', dict(input_tokens=20, cache_creation_input_tokens=0,
                                                    cache_read_input_tokens=0, output_tokens=20),
                                      [dict(type='text', text='helper result')])])
        child.with_suffix('.meta.json').write_text(json.dumps(dict(agentType='Explore')))
        runtime, path = MODULE.find_session(CLAUDE_ID[:8], self.claude_root, self.codex_root)
        self.assertEqual((runtime, path), ('claude', parent))
        result = MODULE.measure(runtime, path, self.codex_root)
        self.assertEqual(result['helpers'], 1)
        self.assertEqual(result['new_tokens'], 157)
        self.assertAlmostEqual(result['helper_share_new'], 40 / 157)
        self.assertEqual(result['polling_responses'], 1)
        self.assertEqual(result['polling_share'], 1115 / 1157)
        self.assertEqual(sorted(c['category'] for c in result['stop_candidates']),
                         ['continue_broad', 'continue_no_pause'])
        table = {r['measure']: r for r in MODULE.compare(result)}
        self.assertEqual(table['polling_share']['n'], 7)

    def test_codex_session_counts_wait_only_calls_timeouts_and_children(self):
        day = self.codex_root / '2026' / '10' / '13'
        write_jsonl(day / f'rollout-2026-10-13T10-00-00-{CODEX_ID}.jsonl', [
            dict(type='session_meta', timestamp=stamp(0), payload=dict(id=CODEX_ID)),
            dict(type='response_item', timestamp=stamp(0), payload=dict(
                type='message', role='user', content=[dict(type='input_text', text='Start the analysis.')])),
            dict(type='response_item', timestamp=stamp(1), payload=dict(
                type='function_call', name='wait_agent', arguments=json.dumps(dict(timeout_ms=30000)))),
            token_count(2, dict(input_tokens=100, cached_input_tokens=80, output_tokens=10, total_tokens=110), 100),
            dict(type='response_item', timestamp=stamp(3), payload=dict(
                type='function_call', name='exec_command', arguments=json.dumps(dict(cmd='python run.py')))),
            token_count(4, dict(input_tokens=300, cached_input_tokens=200, output_tokens=30, total_tokens=330), 200),
        ])
        write_jsonl(day / f'rollout-2026-10-13T10-01-00-{CHILD_ID}.jsonl', [
            dict(type='session_meta', timestamp=stamp(1), payload=dict(id=CHILD_ID, parent_thread_id=CODEX_ID)),
            token_count(2, dict(input_tokens=50, cached_input_tokens=0, output_tokens=5, total_tokens=55), 50),
        ])
        runtime, path = MODULE.find_session(CODEX_ID, self.claude_root, self.codex_root)
        self.assertEqual(runtime, 'codex')
        result = MODULE.measure(runtime, path, self.codex_root)
        self.assertEqual(result['helpers'], 1)
        self.assertEqual(result['wait_only_share'], 0.5)
        self.assertEqual(result['wait_agent_timeouts'], {'<=60s': 1})
        self.assertAlmostEqual(result['helper_share_new'], 55 / 185)
        self.assertEqual(result['stop_candidates'], [])

    def test_ambiguous_prefix_exits(self):
        for name in ('a', 'b'):
            write_jsonl(self.claude_root / name / f'{CLAUDE_ID}.jsonl', [])
        with self.assertRaises(SystemExit):
            MODULE.find_session(CLAUDE_ID[:8], self.claude_root, self.codex_root)


if __name__ == '__main__':
    unittest.main()
