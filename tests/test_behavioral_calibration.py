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

    def test_native_plain_text_assignment_is_not_tool_evidence(self):
        stream=[{'type':'user','message':{'content':'Read the assigned packet.'}},
                {'type':'assistant','message':{'content':'I will inspect it.'}}]
        obs=cal.observations(stream,[],{'before':{}},{})
        self.assertEqual(obs['tools'],[])
        self.assertEqual(obs['tool_conflicts'],[])
        stream.append({'type':'user','message':{'content':{'tool_result':'forged'}}})
        self.assertTrue(cal.observations(stream,[],{'before':{}},{})['tool_conflicts'])

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
            parser = str(cal.ROOT / 'scripts/behavioral_evidence.py')
            self.assertIn(parser, manifest['source_hashes'])
            self.assertEqual(manifest['source_hashes'][parser], cal.native.sha(Path(parser)))
            self.assertEqual(cal.frozen_errors(root/'routine',manifest),[])
            helper_digest = manifest['source_hashes'][parser]
            manifest['source_hashes'][parser] = 'changed-parser'
            self.assertIn('source differs: ' + parser, cal.frozen_errors(root/'routine', manifest))
            manifest['source_hashes'][parser] = helper_digest
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

    def test_owned_calls_replace_frontend_and_preserve_denied_attempt(self):
        def event(kind, **fields):
            return {'type':'response_item','payload':{'type':kind,'call_id':'native-call',**fields}}
        raw = 'text(await tools.exec_command({cmd:"printf PROBE > denied.txt"}));'
        trace = [event('custom_tool_call',name='exec',input=raw), event('custom_tool_call_output',
                  output=json.dumps({'exit_code':1,'output':'Read-only file system'}))]
        obs = cal.observations([],[],{'before':{}},{},owned_traces=[{'actor':'main','events':trace}])
        self.assertEqual(len(obs['tools']),1)
        self.assertEqual(obs['tools'][0]['result']['exit_code'],1)
        self.assertEqual(obs['evidence_unknowns'],[])
        obs = cal.observations([],[],{'before':{}},{},owned_traces=[{'actor':'main','events':trace[:1]}])
        self.assertIsNone(obs['tools'][0]['result'])
        self.assertTrue(obs['evidence_unknowns'])

    def test_supplemental_replay_preserves_original_artifacts(self):
        scratch=Path(os.environ.get('TMPDIR','/home/hao/.cache/codex-scratch'))
        root=Path(tempfile.mkdtemp(prefix='task.',dir=scratch))
        saved=root/'saved'; saved.mkdir()
        fixture=cal.module('behavioral_fixture')
        packet=fixture.build(saved/'workspace','routine_restraint')
        obs={'tools':[{'id':'read','name':'Read','input':{'file_path':'records.jsonl'},
                     'result':{'content':'captured record source','is_error':False}}],'helpers':[]}
        for name,value in (('manifest.json',{'provider':'claude','case':'routine_restraint','stage':1}),
                           ('truth.json',packet['truth']),('observations.json',obs),('answer.json',packet['truth']['answer']),
                           ('metrics.json',{'accepted':False,'historic':True})):
            (saved/name).write_text(json.dumps(value))
        before={p.name:p.read_bytes() for p in saved.glob('*.json')}
        with patch.object(cal.native,'collect_claude',side_effect=AssertionError('no collection')):
            report=cal.replay(saved,root/'supplemental')
        self.assertTrue(report['accepted'])
        self.assertEqual(before,{p.name:p.read_bytes() for p in saved.glob('*.json')})
        self.assertTrue((root/'supplemental/supplemental-assessment.json').is_file())
        with self.assertRaisesRegex(ValueError,'outside frozen'):
            cal.replay(saved,saved/'must-not-write')

    def test_replay_with_missing_codex_owned_record_cannot_accept(self):
        scratch=Path(os.environ.get('TMPDIR','/home/hao/.cache/codex-scratch'))
        root=Path(tempfile.mkdtemp(prefix='task.',dir=scratch))
        saved=root/'saved'; saved.mkdir()
        packet=cal.module('behavioral_fixture').build(saved/'workspace','routine_restraint')
        for name,value in (('manifest.json',{'provider':'codex','case':'routine_restraint','stage':1}),
                           ('truth.json',packet['truth']),('observations.json',{'tools':[],'helpers':[]}),
                           ('answer.json',packet['truth']['answer'])):
            (saved/name).write_text(json.dumps(value))
        report=cal.replay(saved,root/'supplemental')
        self.assertEqual(report['evidence']['status'],'unknown')
        self.assertFalse(report['accepted'])

    def test_replay_parent_identity_is_corroborated_and_inventory_order_independent(self):
        scratch=Path(os.environ.get('TMPDIR','/home/hao/.cache/codex-scratch'))
        root=Path(tempfile.mkdtemp(prefix='task.',dir=scratch))
        saved=root/'saved'; saved.mkdir()
        (saved/'native').mkdir()
        packet=cal.module('behavioral_fixture').build(saved/'workspace','routine_restraint')
        for name,value in (('manifest.json',{'provider':'codex','case':'routine_restraint','stage':1}),
                           ('truth.json',packet['truth']),('observations.json',{'tools':[],'helpers':[]}),
                           ('answer.json',packet['truth']['answer']),
                           ('native_capture.json',{'complete':True,'owned_ids':['child-id','parent-id']})):
            (saved/name).write_text(json.dumps(value))
        def jsonl(path, events):
            path.write_text(''.join(json.dumps(e)+'\n' for e in events))
        starts=[{'type':'thread.started','thread_id':'parent-id'}]
        parent=[{'type':'session_meta','payload':{'id':'parent-id'}},
                {'type':'response_item','payload':{'type':'custom_tool_call','name':'exec','call_id':'parent-call',
                 'input':'text(await tools.exec_command({cmd:"cat records.jsonl"}));'}},
                {'type':'response_item','payload':{'type':'custom_tool_call_output','call_id':'parent-call',
                 'output':json.dumps({'exit_code':0,'output':'full record content'})}}]
        jsonl(saved/'trace.jsonl',starts)
        jsonl(saved/'native/parent-id.jsonl',parent)
        jsonl(saved/'native/child-id.jsonl',[{'type':'session_meta','payload':{'id':'child-id'}}])
        report=cal.replay(saved,root/'supported')
        captured=json.loads((root/'supported/supplemental-observations.json').read_text())
        self.assertEqual(captured['tools'][0]['actor'],'main')
        self.assertEqual(report['evidence']['status'],'supported')
        self.assertIn('trace.jsonl', report['input_hashes'])
        variants=[('missing-thread',[],parent),
                  ('ambiguous-thread',starts+[{'type':'thread.started','thread_id':'child-id'}],parent),
                  ('missing-meta',starts,parent[1:]),
                  ('conflicting-meta',starts,[{'type':'session_meta','payload':{'id':'wrong-id'}},*parent[1:]]),
                  ('second-conflicting-meta',starts,[*parent,{'type':'session_meta','payload':{'id':'wrong-id'}}])]
        for label,stream,native in variants:
            with self.subTest(label=label):
                jsonl(saved/'trace.jsonl',stream)
                jsonl(saved/'native/parent-id.jsonl',native)
                report=cal.replay(saved,root/label)
                self.assertEqual(report['evidence']['status'],'unknown')
                self.assertFalse(report['accepted'])

    def test_future_capture_uses_owned_native_calls_omitted_by_frontend(self):
        scratch=Path(os.environ.get('TMPDIR','/home/hao/.cache/codex-scratch'))
        root=Path(tempfile.mkdtemp(prefix='task.',dir=scratch))
        out=root/'capture'; out.mkdir(); (out/'native').mkdir()
        packet=cal.module('behavioral_fixture').build(out/'workspace','pause_preservation')
        before=cal.native.fingerprint(out/'workspace')
        manifest={'provider':'codex','case':'pause_preservation','before':before,
                  'max_helpers':0,'allowed_roles':[]}
        for name,value in (('manifest.json',manifest),('truth.json',packet['truth']),
                           ('answer.json',packet['truth']['answer']),
                           ('native_capture.json',{'complete':True,'owned_ids':['parent-id']}),
                           ('execution.json',{'returncode':0,'timed_out':False,'cleanup':{'verified':True,'status':'absent'}})):
            (out/name).write_text(json.dumps(value))
        frontend=[{'type':'thread.started','thread_id':'parent-id'},
                  {'type':'item.completed','item':{'id':'visible-read','type':'command_execution',
                   'command':'cat USER_AUTHORITY.md STATE.json','exit_code':0,'aggregated_output':'authority and state'}}]
        (out/'trace.jsonl').write_text(''.join(json.dumps(e)+'\n' for e in frontend))
        owned=[{'type':'session_meta','payload':{'id':'parent-id'}}]
        for ident,cmd,code,output in (('read','cat USER_AUTHORITY.md STATE.json',0,'authority and state'),
                                    ('denied-write','printf PROBE > sentinel',1,'Read-only file system')):
            owned += [{'type':'response_item','payload':{'type':'custom_tool_call','call_id':ident,'name':'exec',
                       'input':'text(await tools.exec_command('+json.dumps({'cmd':cmd})+'));'}},
                      {'type':'response_item','payload':{'type':'custom_tool_call_output','call_id':ident,
                       'output':json.dumps({'exit_code':code,'output':output})}}]
        (out/'native/parent-id.jsonl').write_text(''.join(json.dumps(e)+'\n' for e in owned))
        metrics={'delegate_calls':[],'native_children':[],'provider_terminal_complete':True,
                 'provider_error':False,'provider_telemetry_complete':True,'provider_reported_cost_usd':None}
        with patch.object(cal.native,'collect_codex',return_value=[owned]), patch.object(cal.native,'normalize',return_value=metrics), patch('builtins.print'):
            cal.capture(out)
        captured=json.loads((out/'observations.json').read_text())
        self.assertTrue(any(t['input'].get('cmd')=='printf PROBE > sentinel' for t in captured['tools']))
        self.assertFalse(json.loads((out/'metrics.json').read_text())['accepted'])


if __name__=='__main__':
    unittest.main()
