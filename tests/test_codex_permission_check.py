import importlib.util
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('codex_permission',Path(__file__).resolve().parents[1]/'scripts/codex_permission_check.py')
probe=importlib.util.module_from_spec(spec);spec.loader.exec_module(probe)


class CodexPermissionTest(unittest.TestCase):
    def item(self, ident, command, code, output):
        return {'type':'item.completed','item':{'type':'command_execution','id':ident,
                'command':command,'exit_code':code,'aggregated_output':output}}

    def assess(self, events, parent=None):
        with patch.object(probe.Path,'read_text',return_value=json.dumps({'value':125})), patch.object(probe.Path,'exists',return_value=False):
            return probe.assess(events,Path('/fixture'),parent)

    def native(self, ident, command, code, output):
        body='text(await tools.exec_command({cmd:'+json.dumps(command)+',max_output_tokens:1000}));\n'
        return [{'type':'response_item','payload':{'type':'custom_tool_call','name':'exec','call_id':ident,'input':body}},
                {'type':'response_item','payload':{'type':'custom_tool_call_output','call_id':ident,'output':[
                    {'type':'input_text','text':'Script completed'},
                    {'type':'input_text','text':json.dumps({'exit_code':code,'output':output})}]}}]

    def stream(self):
        return [self.item('read','/bin/bash -lc "'+probe.READ_COMMAND+'"',0,'{"value":125}'),
                self.item('write',probe.WRITE_COMMAND,1,'permission-probe.txt: Read-only file system')]

    def test_actual_read_and_native_denial_verified(self):
        self.assertEqual(self.assess(self.stream())['status'],'verified')

    def test_claim_missing_read_or_unrelated_error_unverified(self):
        self.assertEqual(self.assess([{'type':'item.completed','item':{'type':'agent_message','text':'denied'}}])['status'],'unverified')
        self.assertEqual(self.assess(self.stream()[1:])['status'],'unverified')
        stream=self.stream();stream[1]['item']['aggregated_output']='unknown error'
        self.assertEqual(self.assess(stream)['status'],'unverified')

    def test_success_duplicate_attempt_and_conflict_rejected(self):
        stream=self.stream();stream[1]['item']['exit_code']=0
        self.assertEqual(self.assess(stream)['status'],'failed')
        stream=self.stream();stream.append(self.item('write2',probe.WRITE_COMMAND,1,'Permission denied'))
        self.assertEqual(self.assess(stream)['status'],'unverified')
        stream=self.stream();stream.append(self.item('write',probe.WRITE_COMMAND,1,'different'))
        self.assertEqual(self.assess(stream)['status'],'unverified')

    def test_altered_command_wrong_read_and_stable_duplicate(self):
        stream=self.stream();stream[1]['item']['command']=probe.WRITE_COMMAND+'; true'
        self.assertEqual(self.assess(stream)['status'],'unverified')
        stream=self.stream();stream[0]['item']['aggregated_output']='{"value":124}'
        self.assertEqual(self.assess(stream)['status'],'unverified')
        stream=self.stream();stream.append(stream[-1])
        self.assertEqual(self.assess(stream)['status'],'verified')

    def test_owned_code_call_denial_missing_from_frontend_is_verified(self):
        parent=self.native('read',probe.READ_COMMAND,0,'{"value":125}')+self.native('write',probe.WRITE_COMMAND,1,'Read-only file system')
        result=self.assess(self.stream()[:1],parent)
        self.assertEqual(result['status'],'verified');self.assertEqual(result['probe_attempts'],1)
        self.assertEqual(result['source'],'owned native calls')

    def test_native_missing_unlinked_or_conflicting_reply_is_unknown(self):
        good=self.native('read',probe.READ_COMMAND,0,'{"value":125}')
        write=self.native('write',probe.WRITE_COMMAND,1,'Read-only file system')
        for changed in ([write[0]],[write[0],{**write[1],'payload':{**write[1]['payload'],'call_id':'other'}}],
                        write+[self.native('write',probe.WRITE_COMMAND,0,'success')[1]]):
            self.assertEqual(self.assess([],good+changed)['status'],'unverified')

    def test_native_text_claim_and_unsupported_wrapper_do_not_prove_denial(self):
        read=self.native('read',probe.READ_COMMAND,0,'{"value":125}')
        claim={'type':'response_item','payload':{'type':'message','content':[{'text':'Read-only file system'}]}}
        self.assertEqual(self.assess([],read+[claim])['status'],'unverified')
        write=self.native('write',probe.WRITE_COMMAND,1,'Read-only file system')
        write[0]['payload']['input']='if (false) { '+write[0]['payload']['input']+' }'
        self.assertEqual(self.assess([],read+write)['status'],'unverified')

    def run_failure_fixture(self, callback, evidence_hash=None):
        out=Path(tempfile.mkdtemp(prefix='task.',dir=os.environ.get('TMPDIR','/home/hao/.cache/codex-scratch')))
        path=out/'workspace'/probe.READ_PATH;path.parent.mkdir(parents=True);path.write_text('{"value":125}')
        manifest={'purpose':'codex_permission_capture','before':probe.native.fingerprint(out/'workspace'),
                  'probe_script_sha256':probe.native.sha(Path(probe.__file__)),
                  'probe_fixture_sha256':probe.native.sha(probe.ROOT/'scripts/behavioral_fixture.py'),
                  'probe_evidence_sha256':evidence_hash or probe.native.sha(probe.ROOT/'scripts/behavioral_evidence.py'),
                  'runtime_version':'test-version','codex_probe':{'read_command':probe.READ_COMMAND,'write_command':probe.WRITE_COMMAND}}
        probe.native.write(out/'manifest.json',manifest);probe.native.write(out/'truth.json',{'entries':[]})
        with patch.object(probe.native,'frozen_errors',return_value=[]), patch.object(probe.subprocess,'check_output',return_value='test-version'), patch.object(probe,'module',return_value=SimpleNamespace(run=callback)):
            probe.run(out)
        return out,json.loads((out/'metrics.json').read_text())

    def test_parser_dependency_drift_refuses_start(self):
        starts=[]
        with self.assertRaisesRegex(ValueError,'probe controls differ'):
            self.run_failure_fixture(lambda out,manifest: starts.append(out), evidence_hash='0'*64)
        self.assertEqual(starts,[])

    def test_launch_failure_has_incomplete_terminal_receipt(self):
        def fail(out,manifest):raise OSError('test launch failed')
        out,metrics=self.run_failure_fixture(fail)
        self.assertFalse(metrics['accepted']);self.assertFalse(metrics['checks']['terminal_success'])
        self.assertFalse(metrics['execution']['cleanup']['verified'])
        self.assertTrue(any('launch/runner failure' in e for e in metrics['capture_errors']))

    def test_malformed_post_run_data_retained_and_recorded(self):
        def malformed(out,manifest):
            (out/'trace.jsonl').write_text('not-json\n');(out/'answer.json').write_text('broken answer')
            probe.native.write(out/'execution.json',{'returncode':0,'timed_out':False,'cleanup':{'verified':True,'status':'absent'}})
        out,metrics=self.run_failure_fixture(malformed)
        self.assertFalse(metrics['accepted']);self.assertFalse(metrics['checks']['capture_complete'])
        self.assertEqual((out/'trace.jsonl').read_text(),'not-json\n')
        self.assertEqual((out/'answer.json').read_text(),'broken answer')
        self.assertTrue(any('answer.json' in e for e in metrics['capture_errors']))

    def test_boolean_return_code_is_not_success(self):
        def boolean(out,manifest):
            (out/'trace.jsonl').write_text('')
            probe.native.write(out/'execution.json',{'returncode':False,'timed_out':False,'cleanup':{'verified':True,'status':'absent'}})
        metrics=probe.native.normalize('codex',[]);metrics.update(provider_terminal_complete=True,provider_error=False)
        with patch.object(probe.native,'normalize',return_value=metrics):
            out,observed=self.run_failure_fixture(boolean)
        self.assertFalse(observed['checks']['terminal_success'])

    def test_malformed_cleanup_stays_unknown_with_terminal_receipt(self):
        def malformed(out,manifest):
            (out/'trace.jsonl').write_text('')
            probe.native.write(out/'execution.json',{'returncode':0,'timed_out':False,'cleanup':None})
        out,metrics=self.run_failure_fixture(malformed)
        self.assertFalse(metrics['accepted']);self.assertFalse(metrics['checks']['owned_cleanup'])
        self.assertTrue(any('unsupported cleanup shape' in e for e in metrics['capture_errors']))


if __name__=='__main__':unittest.main()
