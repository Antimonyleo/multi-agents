import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('behavioral_calibration',Path(__file__).resolve().parents[1]/'scripts/behavioral_calibration.py')
cal=importlib.util.module_from_spec(spec)
spec.loader.exec_module(cal)


class BehavioralCaptureTest(unittest.TestCase):
    def test_correlated_results_and_child_actor_preserved(self):
        call={'type':'assistant','message':{'content':[{'type':'tool_use','id':'a','name':'Read','input':{'file_path':'input'}}]}}
        reply={'type':'user','message':{'content':[{'type':'tool_result','tool_use_id':'a','content':'raw','is_error':False}]}}
        obs=cal.observations([{**call,'parent_tool_use_id':'dispatch'},{**reply,'parent_tool_use_id':'dispatch'}],
                             [{'id':'child','parent_tool_use_id':'dispatch','events':[call,reply]}],{'before':{}},{})
        self.assertEqual(len(obs['tools']),1)
        self.assertEqual(obs['tools'][0]['actor'],'child')
        self.assertEqual(obs['tools'][0]['result']['content'],'raw')
        self.assertEqual(obs['tool_conflicts'],[])

    def test_conflicting_calls_are_not_silently_deduplicated(self):
        def call(path):
            return {'type':'assistant','message':{'content':[{'type':'tool_use','id':'a','name':'Read','input':{'file_path':path}}]}}
        obs=cal.observations([call('one'),call('two')],[],{'before':{}},{})
        self.assertEqual(obs['tool_conflicts'],['a'])

    def test_conflicting_results_and_spoofed_origins_fail_capture(self):
        call={'type':'assistant','message':{'content':[{'type':'tool_use','id':'a','name':'Read','input':{'file_path':'input'}}]}}
        def reply(error):
            return {'type':'user','message':{'content':[{'type':'tool_result','tool_use_id':'a','content':'raw','is_error':error}]}}
        self.assertTrue(cal.observations([call,reply(True),reply(False)],[],{'before':{}},{})['tool_conflicts'])
        self.assertEqual(cal.observations([call,reply(False),reply(False)],[],{'before':{}},{})['tool_conflicts'],[])
        spoof={**reply(False),'type':'assistant'}
        obs=cal.observations([call,spoof],[],{'before':{}},{})
        self.assertTrue(obs['tool_conflicts'])
        self.assertIsNone(obs['tools'][0]['result'])

    def test_unlinked_wrong_role_and_nested_helpers_fail(self):
        manifest={'max_helpers':1,'allowed_roles':['scientific_reviewer']}
        metric={'delegate_calls':[{'tool_use_id':'a','role':'scientific_reviewer'}]}
        child={'id':'child','role':'scientific_reviewer','depth':1,'models':['opus'],'parent_tool_use_id':'a'}
        self.assertTrue(cal.boundary(metric,[child],manifest)['verified'])
        for changed in ({'role':'scientific_worker'},{'parent_tool_use_id':'other'},{'depth':2},{'models':[]}):
            self.assertFalse(cal.boundary(metric,[{**child,**changed}],manifest)['verified'])
        self.assertFalse(cal.boundary(metric,[],manifest)['verified'])

    def test_preparation_snapshot_includes_guidance_and_skill_setup(self):
        scratch=Path(os.environ.get('TMPDIR','/home/hao/.cache/codex-scratch'))
        root=Path(tempfile.mkdtemp(prefix='task.',dir=scratch))
        home=root/'home'
        (home/'.claude').mkdir(parents=True)
        (home/'.claude/settings.json').write_text('{}')
        with patch.object(cal.native.Path,'home',return_value=home), patch.object(cal.subprocess,'check_output',return_value='test-version'):
            manifest=cal.prepare(root/'routine','routine_restraint')
            truth=json.loads((root/'routine/truth.json').read_text())
            self.assertEqual(truth['initial'],manifest['before'])
            self.assertEqual(cal.frozen_errors(root/'routine',manifest),[])
            (root/'routine/prompt.txt').write_text('drift')
            self.assertIn('input differs: prompt.txt',cal.frozen_errors(root/'routine',manifest))

    def test_stage_requires_accepted_immediate_predecessor(self):
        scratch=Path(os.environ.get('TMPDIR','/home/hao/.cache/codex-scratch'))
        root=Path(tempfile.mkdtemp(prefix='task.',dir=scratch))
        prior=root/'prior'; prior.mkdir()
        (prior/'manifest.json').write_text(json.dumps({'case':'receipt_reuse','provider':'claude','stage':1}))
        for metrics in ({'accepted':False,'checks':{'output':False}},
                        {'accepted':True,'checks':{}}, {'accepted':True,'checks':{'output':1}}):
            (prior/'metrics.json').write_text(json.dumps(metrics))
            with self.assertRaisesRegex(ValueError,'not accepted'):
                cal.prepare(root/('next-'+str(len(list(root.iterdir())))), 'receipt_reuse', previous=prior, stage=2)
        (prior/'metrics.json').write_text(json.dumps({'accepted':True,'checks':{'output':True}}))
        with self.assertRaisesRegex(ValueError,'predecessor differs'):
            cal.prepare(root/'skipped', 'receipt_reuse', previous=prior, stage=3)
        with self.assertRaisesRegex(ValueError,'stage 1'):
            cal.prepare(root/'no-predecessor', 'receipt_reuse', stage=2)


if __name__=='__main__':
    unittest.main()
