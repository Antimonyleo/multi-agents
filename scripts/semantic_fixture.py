#!/usr/bin/env python3
"""Frozen semantic configuration fixture and independently specified grading.

No inference. The reference table is outside the model workspace. Two documented
contracts differ from execution; runtime probes verify the manually set table.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys

FILES = {
'contract.md': '''# Transport configuration contract
CLI options override nonempty environment values, then deployment defaults.
Retries must be an integer from 0 through 5; zero disables retries.
Timeouts must be integers from 10 through 500 milliseconds.
The local client accepts seconds. The remote client accepts milliseconds.
Both drivers must preserve the configured timeout duration.
Invalid configuration fails before calling a driver. JSON output uses null
for unavailable retry, configuration-timeout and client-timeout fields.
''',
'cli.py': '''import argparse

def parse(args):
    p = argparse.ArgumentParser()
    p.add_argument('--retries', type=int)
    p.add_argument('--timeout-ms', type=int)
    p.add_argument('--driver', choices=['local', 'remote'], default='local')
    return p.parse_args(args)
''',
'deployment.py': '''DEFAULT_RETRIES = 3
DEFAULT_TIMEOUT_MS = 40
RETRIES_ENV = 'TRANSPORT_RETRIES'
TIMEOUT_ENV = 'TRANSPORT_TIMEOUT_MS'
''',
'sources.py': '''from deployment import DEFAULT_RETRIES, DEFAULT_TIMEOUT_MS, RETRIES_ENV, TIMEOUT_ENV

def load(opts, env):
    retries = opts.retries or int(env.get(RETRIES_ENV) or DEFAULT_RETRIES)
    timeout = opts.timeout_ms if opts.timeout_ms is not None else int(env.get(TIMEOUT_ENV) or DEFAULT_TIMEOUT_MS)
    return {'retries': retries, 'timeout_ms': timeout, 'driver': opts.driver}
''',
'validation.py': '''def validate(config):
    if not 0 <= config['retries'] <= 5:
        raise ValueError('retries_range')
    if not 10 <= config['timeout_ms'] <= 500:
        raise ValueError('timeout_range')
    return config
''',
'planner.py': '''from sources import load
from validation import validate

def make_plan(opts, env):
    return validate(load(opts, env))
''',
'clients.py': '''class LocalClient:
    def send(self, timeout_seconds, retries):
        return {'client_timeout_ms': timeout_seconds * 1000, 'retries': retries}

class RemoteClient:
    def send(self, timeout_milliseconds, retries):
        return {'client_timeout_ms': timeout_milliseconds, 'retries': retries}
''',
'local_driver.py': '''from clients import LocalClient

def dispatch(plan):
    timeout_seconds = plan['timeout_ms'] / 1000
    return LocalClient().send(timeout_seconds, plan['retries'])
''',
'remote_driver.py': '''from clients import RemoteClient

def dispatch(plan):
    timeout_milliseconds = plan['timeout_ms'] / 1000
    return RemoteClient().send(timeout_milliseconds, plan['retries'])
''',
'coordinator.py': '''import local_driver
import remote_driver
from cli import parse
from planner import make_plan

def execute(args, env):
    try:
        plan = make_plan(parse(args), env)
        driver = remote_driver if plan['driver'] == 'remote' else local_driver
        actual = driver.dispatch(plan)
        return {'retries': actual['retries'], 'timeout_ms': plan['timeout_ms'],
                'client_timeout_ms': actual['client_timeout_ms'], 'error': None}
    except ValueError as exc:
        message = str(exc)
        error = message if message in ('retries_range', 'timeout_range') else 'integer_parse'
        return {'retries': None, 'timeout_ms': None, 'client_timeout_ms': None, 'error': error}
''',
'entry.py': '''import json
import sys
from coordinator import execute

if __name__ == '__main__':
    case = json.load(sys.stdin)
    print(json.dumps(execute(case['args'], case['env'])))
''',
'notes/cache.md': 'The unrelated cache service uses seconds and retries a cache miss once.\n',
'notes/legacy.md': 'An obsolete transport adapter used a 30-second deadline. It is not imported.\n',
'notes/display.md': 'The dashboard rounds milliseconds to two decimal places for labels only.\n',
}
CASES = [
    {'id':'cli_override','args':['--retries','2','--timeout-ms','80'],'env':{'TRANSPORT_RETRIES':'4','TRANSPORT_TIMEOUT_MS':'100'}},
    {'id':'env_fallback','args':[],'env':{'TRANSPORT_RETRIES':'1','TRANSPORT_TIMEOUT_MS':'20'}},
    {'id':'defaults','args':[],'env':{}},
    {'id':'zero_retry','args':['--retries','0'],'env':{'TRANSPORT_RETRIES':'4'}},
    {'id':'negative_retry','args':['--retries','-1'],'env':{}},
    {'id':'bad_environment','args':[],'env':{'TRANSPORT_TIMEOUT_MS':'bad'}},
    {'id':'remote_units','args':['--driver','remote'],'env':{}},
    {'id':'remote_override','args':['--driver','remote','--timeout-ms','100','--retries','5'],'env':{}},
    {'id':'timeout_low','args':['--timeout-ms','9'],'env':{}},
    {'id':'timeout_high_boundary','args':['--timeout-ms','500'],'env':{}},
]
# Literal outcomes specified independently of the fixture implementation.
OUTCOMES = [(2,80,80,None),(1,20,20,None),(3,40,40,None),(4,40,40,None),
            (None,None,None,'retries_range'),(None,None,None,'integer_parse'),
            (3,40,0.04,None),(5,100,0.1,None),(None,None,None,'timeout_range'),
            (3,500,500,None)]
FINDINGS = {'sources.py': 'opts.retries or', 'remote_driver.py': "plan['timeout_ms'] / 1000"}
SCHEMA = {'type':'object','properties':{
    'cases':{'type':'array','items':{'type':'object','properties':{
        'id':{'type':'string'},'retries':{'type':['integer','null']},
        'timeout_ms':{'type':['integer','null']},'client_timeout_ms':{'type':['number','null']},
        'error':{'type':['string','null']}},'required':['id','retries','timeout_ms','client_timeout_ms','error'],'additionalProperties':False}},
    'findings':{'type':'array','items':{'type':'object','properties':{
        'path':{'type':'string'},'line':{'type':'integer'},'quote':{'type':'string'}},
        'required':['path','line','quote'],'additionalProperties':False}}},
    'required':['cases','findings'],'additionalProperties':False}
TASK = '''Read contract.md and cases.json. Trace the configuration pipeline and report
actual outcomes for all cases, sorted by id. Identify every contract violation
present in the executed pipeline. Give each finding its implementing source
path, line and exact nonempty source-line quote. Report only supported violations. Use the requested JSON schema.
All inputs are in this workspace; do not read other directories or hidden keys.
'''
HELPER_ASSIGNMENT = '''Use only Read/Grep/Glob. Retrieve exact numbered source excerpts
from deployment.py, clients.py, local_driver.py and remote_driver.py containing
default constants, client parameter names, both client return expressions
(including timeout_seconds * 1000), and timeout assignments/calls. Return
path:line and the verbatim excerpt for each; at most 220 words. Do not interpret
units, trace execution, determine defects, write files, run tools outside your
reader set or delegate. These four files are your entire scope.
'''


def build(workspace):
    workspace = Path(workspace)
    workspace.mkdir(parents=True, exist_ok=False)
    for name, content in FILES.items():
        path = workspace / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    (workspace/'cases.json').write_text(json.dumps(CASES, indent=2)+'\n')
    rows = [dict(id=case['id'], **dict(zip(('retries','timeout_ms','client_timeout_ms','error'), outcome)))
            for case, outcome in zip(CASES, OUTCOMES)]
    return {'cases':sorted(rows,key=lambda r:r['id']), 'findings':FINDINGS}


def verify(workspace, truth):
    """Compare manual outcomes to executable behavior, outside model inference."""
    observed=[]
    for case in CASES:
        result=subprocess.run([sys.executable,'-B','entry.py'],input=json.dumps(case),
                              cwd=workspace,text=True,capture_output=True,timeout=5,check=True)
        observed.append(dict(id=case['id'], **json.loads(result.stdout)))
    return sorted(observed,key=lambda r:r['id']) == truth['cases']


def score(answer, truth, workspace):
    if not isinstance(answer,dict) or set(answer)!= {'cases','findings'}:
        return False
    if answer['cases']!=truth['cases'] or not isinstance(answer['cases'],list):
        return False
    for row in answer['cases']:
        if not isinstance(row,dict) or set(row)!={'id','retries','timeout_ms','client_timeout_ms','error'}:
            return False
        if type(row['id']) is not str or any(row[k] is not None and type(row[k]) is not int for k in ('retries','timeout_ms')):
            return False
        if row['client_timeout_ms'] is not None and type(row['client_timeout_ms']) not in (int,float):
            return False
        if row['error'] is not None and type(row['error']) is not str:
            return False
    findings=answer['findings']
    if not isinstance(findings,list) or len(findings)!=len(truth['findings']):
        return False
    seen=set()
    for f in findings:
        if not isinstance(f,dict) or set(f)!={'path','line','quote'}:
            return False
        ident=f['path']
        if type(ident) is not str or ident in seen or ident not in truth['findings']:
            return False
        seen.add(ident)
        if type(f['line']) is not int or type(f['quote']) is not str:
            return False
        lines=(Path(workspace)/f['path']).read_text().splitlines()
        if not 1<=f['line']<=len(lines) or f['quote']!=lines[f['line']-1] or not f['quote'].strip():
            return False
        expected_fragment = truth['findings'][ident]
        if expected_fragment not in f['quote']:
            return False
    return seen == set(truth['findings'])


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--workspace',required=True)
    args=p.parse_args()
    truth=build(args.workspace)
    if not verify(args.workspace,truth):
        raise ValueError('manual reference disagrees with executable fixture')
    print(json.dumps({'cases':len(truth['cases']),'modules':sum(n.endswith('.py') for n in FILES),'verified':True}))

if __name__=='__main__':
    main()
