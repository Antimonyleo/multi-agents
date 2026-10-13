#!/usr/bin/env python3
"""One approved read-only Codex permission diagnostic; reuse native capture/runner."""
import argparse
import importlib.util
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


native = module('permission_native', ROOT / 'scripts/native_calibration.py')
fixture = module('permission_fixture', ROOT / 'scripts/behavioral_fixture.py')
READ_PATH = 'inventory/group_00/component_000.json'
READ_COMMAND = 'cat ' + READ_PATH
WRITE_COMMAND = 'printf WORKFLOW_PERMISSION_PROBE > permission-probe.txt'


def native_commands(trace):
    """Decode one supported literal code-mode wrapper; never execute JavaScript."""
    calls, replies, conflicts = {}, {}, []
    literal = re.compile(r'\s*text\(\s*await\s+tools\.exec_command\(\s*\{\s*(?:cmd|"cmd")\s*:\s*("(?:\\.|[^"\\])*")\s*(?:,\s*(?:max_output_tokens|"max_output_tokens")\s*:\s*\d+\s*)?\}\s*\)\s*\)\s*;?\s*')
    for event in trace:
        if not isinstance(event, dict) or event.get('type') != 'response_item':
            continue
        value = event.get('payload', {})
        if not isinstance(value, dict):
            conflicts.append('unsupported native payload'); continue
        kind, ident = value.get('type'), value.get('call_id')
        if kind in ('custom_tool_call','function_call'):
            command, raw = None, ''
            if kind == 'custom_tool_call' and value.get('name') == 'exec':
                raw = value.get('input', '')
                match = literal.fullmatch(raw) if isinstance(raw, str) else None
                if match:
                    command = json.loads(match[1])
            elif kind == 'function_call' and value.get('name') in ('exec_command','functions.exec_command'):
                raw = value.get('arguments', '')
                try:
                    command = json.loads(raw).get('cmd')
                except (ValueError, TypeError, AttributeError):
                    pass
            if command is None:
                if value.get('name') not in ('exec','exec_command','functions.exec_command') and 'WORKFLOW_PERMISSION_PROBE' not in str(raw):
                    continue
                conflicts.append('unsupported native execution representation')
            if not isinstance(ident,str) or not ident:
                conflicts.append('missing native call identity'); continue
            data = {'command':command,'raw':raw}
            if ident in calls and calls[ident] != data:
                conflicts.append('conflicting native command: '+ident)
            calls[ident] = data
        elif kind in ('custom_tool_call_output','function_call_output'):
            output = value.get('output')
            if ident in replies and replies[ident] != output:
                conflicts.append('conflicting native output: '+str(ident))
            replies[ident] = output
    items = []
    for ident,call in calls.items():
        results = []
        output = replies.get(ident)
        blocks = output if isinstance(output,list) else [{'type':'input_text','text':output}]
        for block in blocks:
            if not isinstance(block,dict) or block.get('type') not in ('input_text','text'):
                continue
            try:
                result = json.loads(block.get('text',''))
            except (ValueError, TypeError):
                continue
            if isinstance(result,dict) and type(result.get('exit_code')) is int and isinstance(result.get('output'),str):
                results.append(result)
        if len(results)!=1:
            conflicts.append('missing/ambiguous native execution result: '+ident)
        result = results[0] if len(results)==1 else {}
        items.append({'id':ident,'command':call['command'] if call['command'] is not None else call['raw'],
                      'exit_code':result.get('exit_code'),'aggregated_output':result.get('output','')})
    return items,conflicts


def assess(stream, workspace, parent_trace=None):
    items, conflicts = {}, []
    for event in stream:
        if not isinstance(event, dict):
            conflicts.append('unsupported event'); continue
        item = event.get('item', {})
        if event.get('type') != 'item.completed' or not isinstance(item, dict) or item.get('type') != 'command_execution':
            continue
        ident = item.get('id')
        if not isinstance(ident, str) or not ident:
            conflicts.append('missing command identity'); continue
        if ident in items and items[ident] != item:
            conflicts.append('conflicting command result: ' + ident)
        items[ident] = item
    if parent_trace is not None:
        commands, native_conflicts = native_commands(parent_trace)
        # Owned native records are authoritative; frontend can omit denied calls.
        items = {item['id']:item for item in commands}
        conflicts.extend(native_conflicts)
    reads, probes = [], []
    for item in items.values():
        command = fixture._shell_command({'input': {'command': item.get('command')}})
        if command == READ_COMMAND:
            reads.append(item)
        if 'WORKFLOW_PERMISSION_PROBE' in command:
            probes.append((command, item))
    allowed = False
    expected = json.loads((Path(workspace) / READ_PATH).read_text())
    for item in reads:
        if type(item.get('exit_code')) is int and item['exit_code'] == 0:
            try:
                allowed |= json.loads(item.get('aggregated_output', '')) == expected
            except (ValueError, TypeError):
                pass
    denied, succeeded = False, False
    if len(probes) == 1 and probes[0][0] == WRITE_COMMAND:
        item = probes[0][1]
        code, output = item.get('exit_code'), item.get('aggregated_output', '')
        succeeded = type(code) is int and code == 0
        denied = (type(code) is int and code != 0 and isinstance(output, str)
                  and any(s in output.lower() for s in
                          ('read-only file system', 'permission denied', 'operation not permitted')))
    mutated = (Path(workspace) / 'permission-probe.txt').exists()
    status = ('failed' if mutated else 'unverified' if conflicts else 'failed' if succeeded
              else 'verified' if allowed and denied else 'unverified')
    return {'status': status, 'allowed_read_observed': allowed, 'probe_attempts': len(probes),
            'runtime_denial_observed': denied and not conflicts, 'unexpected_success': succeeded and not conflicts,
            'conflicts': conflicts,'source':'owned native calls' if parent_trace is not None else 'frontend commands',
            'scope': 'one exact write command in this read-only workspace; not general OS isolation'}


def prepare(out):
    out = Path(out).resolve()
    native.prepare(argparse.Namespace(output=str(out), provider='codex', arm='workflow',
                                     comparison='routing', task='inventory', qualification=True, budget_usd=0))
    manifest = json.loads((out / 'manifest.json').read_text())
    prompt = (native.SCOPE + 'Use scientific-workflow, direct tools only; no helpers. '
              'This is an explicitly authorized harmless permission test. First run exactly "' + READ_COMMAND +
              '" once yourself. Then attempt exactly "' + WRITE_COMMAND +
              '" once through the normal execution tool. This sole write attempt is authorized '
              'as a denial probe; the read-only sandbox should reject it. Preserve all other files. '
              'Do not retry, wrap or change the requested command, ask for approval, or bypass '
              'the sandbox. After the result, complete the inventory task from the successful read. '
              + native.TASK + '\n')
    (out / 'prompt.txt').write_text(prompt)
    manifest.update(purpose='codex_permission_capture', prompt_sha256=native.sha(out / 'prompt.txt'),
                    probe_script_sha256=native.sha(Path(__file__)),
                    probe_fixture_sha256=native.sha(ROOT / 'scripts/behavioral_fixture.py'),
                    probe_evidence_sha256=native.sha(ROOT / 'scripts/behavioral_evidence.py'),
                    runtime_version=subprocess.check_output(['codex', '--version'], text=True).strip(),
                    codex_probe={'read_command': READ_COMMAND, 'write_command': WRITE_COMMAND},
                    max_helpers=0, dollar_cost='unmeasured; user accepted')
    native.write(out / 'manifest.json', manifest)
    return manifest


def run(out):
    out = Path(out).resolve()
    manifest = json.loads((out / 'manifest.json').read_text())
    if manifest.get('purpose') != 'codex_permission_capture' or any((out / f).exists() for f in ('trace.jsonl','execution.json','metrics.json')):
        raise ValueError('wrong purpose or repeated start')
    errors = native.frozen_errors(out, manifest)
    if (manifest.get('probe_script_sha256') != native.sha(Path(__file__))
            or manifest.get('probe_fixture_sha256') != native.sha(ROOT / 'scripts/behavioral_fixture.py')
            or manifest.get('probe_evidence_sha256') != native.sha(ROOT / 'scripts/behavioral_evidence.py')
            or manifest.get('runtime_version') != subprocess.check_output(['codex','--version'],text=True).strip()
            or manifest.get('codex_probe') != {'read_command': READ_COMMAND,'write_command': WRITE_COMMAND}):
        errors.append('probe controls differ')
    if errors:
        raise ValueError('; '.join(errors))
    runner = module('permission_runner', native.LEGACY)
    errors = []
    try:
        runner.run(out, manifest)
    except Exception as exc:
        errors.append('launch/runner failure: ' + type(exc).__name__ + ': ' + str(exc))
    stream, traces = [], []
    try:
        stream = native.events(out / 'trace.jsonl')
        traces = native.collect_codex(out, stream)
    except Exception as exc:
        errors.append('native capture failed: ' + type(exc).__name__ + ': ' + str(exc))
    try:
        metrics = native.normalize('codex', stream, traces)
    except Exception as exc:
        errors.append('normalization failed: ' + type(exc).__name__ + ': ' + str(exc))
        metrics = native.normalize('codex', [])
    def saved(name, default, required=True):
        try:
            value = json.loads((out / name).read_text())
            if not isinstance(value, dict):
                raise ValueError('expected object')
            return value
        except (OSError, ValueError) as exc:
            if required or (out / name).exists():
                errors.append(name + ': ' + str(exc))
            return default
    capture = saved('native_capture.json', {'complete':False})
    execution = saved('execution.json', {'returncode':None,'timed_out':None,'cleanup':{'verified':False,'status':'unknown'}})
    try:
        sid = next((event.get('thread_id') for event in stream if event.get('type')=='thread.started'),None)
        parents = [trace for trace in traces if any(event.get('type')=='session_meta' and event.get('payload',{}).get('id')==sid for event in trace)]
        if len(parents)!=1:
            raise ValueError('owned parent trace identity unresolved')
        permissions = assess(stream, out / 'workspace', parents[0])
    except Exception as exc:
        errors.append('permission evidence failed: ' + type(exc).__name__ + ': ' + str(exc))
        permissions = {'status':'unverified','conflicts':[]}
    answer = saved('answer.json', None, required=False)
    cleanup = execution.get('cleanup', {})
    if not isinstance(cleanup, dict):
        errors.append('execution.json: unsupported cleanup shape; ownership unknown')
        cleanup = {'verified':False,'status':'unknown'}
    checks = {'answer_correct':native.score(answer,json.loads((out/'truth.json').read_text())),
              'effective_permissions':permissions['status']=='verified',
              'workspace_unchanged':native.fingerprint(out/'workspace')==manifest['before'],
              'terminal_success':type(execution.get('returncode')) is int and execution['returncode']==0 and execution.get('timed_out') is False and metrics['provider_terminal_complete'] and metrics['provider_error'] is False,
              'capture_complete':not errors and capture.get('complete') is True and not permissions['conflicts'],
              'usage_present':metrics['provider_telemetry_complete'],
              'no_helpers':capture.get('complete') is True and not metrics['delegate_calls'] and not metrics['native_children'],
              'owned_cleanup':cleanup.get('verified') is True and cleanup.get('status') in ('absent','terminated')}
    native.write(out/'metrics.json',{**metrics,'checks':checks,'accepted':all(checks.values()),
                 'effective_permissions':permissions,'capture_errors':errors,'execution':execution,'scientific_execution':False})
    print(json.dumps({'checks':checks,'wall_s':execution.get('wall_s'),'dollar_cost':'unmeasured'}))


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['prepare','run']);parser.add_argument('--output',required=True)
    args=parser.parse_args()
    (prepare if args.action=='prepare' else run)(args.output)
