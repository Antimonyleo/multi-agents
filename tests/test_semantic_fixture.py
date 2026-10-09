import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('semantic_fixture',Path(__file__).resolve().parents[1]/'scripts/semantic_fixture.py')
fixture=importlib.util.module_from_spec(spec); spec.loader.exec_module(fixture)

class SemanticFixtureTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)/'workspace'
        self.truth=fixture.build(self.root)
        self.answer={'cases':copy.deepcopy(self.truth['cases']),'findings':[
            {'path':'sources.py','line':4,'quote':fixture.FILES['sources.py'].splitlines()[3]},
            {'path':'remote_driver.py','line':4,'quote':fixture.FILES['remote_driver.py'].splitlines()[3]}]}
    def test_manual_outcomes_match_executable_behavior(self):
        self.assertTrue(fixture.verify(self.root,self.truth))
        self.assertTrue(fixture.score(self.answer,self.truth,self.root))
        self.assertEqual(len(self.truth['cases']),10)
    def test_wrong_unsupported_or_missing_claims_rejected(self):
        for category in ['wrong_case','missing_case','bool_as_int','wrong_line','wrong_quote','duplicate_finding','extra_finding','irrelevant_line']:
            answer=copy.deepcopy(self.answer)
            if category=='wrong_case': answer['cases'][0]['retries']=99
            elif category=='missing_case': answer['cases'].pop()
            elif category=='bool_as_int': next(r for r in answer['cases'] if r['id']=='env_fallback')['retries']=True
            elif category=='wrong_line': answer['findings'][0]['line']=999
            elif category=='wrong_quote': answer['findings'][0]['quote']='fabricated'
            elif category=='duplicate_finding': answer['findings'][1]=answer['findings'][0]
            elif category=='extra_finding': answer['findings'].append(answer['findings'][0])
            else:
                answer['findings'][0]['line']=1
                answer['findings'][0]['quote']=fixture.FILES['sources.py'].splitlines()[0]
            self.assertFalse(fixture.score(answer,self.truth,self.root),category)
    def test_no_answer_key_written_to_workspace(self):
        self.assertFalse(any('truth' in p.name or 'answer' in p.name for p in self.root.rglob('*')))
        self.assertNotIn('zero_retry_ignored', (self.root/'cases.json').read_text())

if __name__=='__main__': unittest.main()
