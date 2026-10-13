#!/usr/bin/env python3
"""Synthetic dependent implementation fixture; no model or scientific execution.

build(workspace) writes only task inputs, defective modules and public tests.
validate(workspace) executes bounded isolated JSON probes and compares literal,
independently specified outputs held in this evaluator, outside the workspace.
install_reference(workspace) exists only for offline fixture unit tests.
One synthetic comparison cannot establish representative or long-task savings.
"""
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

WRITABLE_PATHS = ['durations.py', 'attempts.py', 'report.py']
PUBLIC_COMMAND = ['python', '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-v']
RETRIEVAL_TASK = '''Read ONLY docs/durations.md and docs/attempts.md. Retrieve the complete
text under sections "D1: Duration values", "A2: Final state" and "A3: Unknown
duration". Return path, section heading, exact excerpts, and any missing section;
maximum 450 words. Do not infer outputs, implement, execute commands, write or
delegate. These retrieved requirements replace the owner's reading of these
three sections; the owner retains code tracing, integration and checks.'''

FILES = {
    'CONTRACT.md': '''# Batch-attempt report repair

This is synthetic software maintenance. It contains no scientific inputs.
Repair durations.py, attempts.py and report.py as one dependent implementation.
Preserve other files. All requirements are in the three documents below.

## Entrypoints
- durations.normalize(duration): return milliseconds as a finite number. Unknown
  duration returns None; invalid duration raises ValueError.
- attempts.summarize(records): validate a list of attempt records and return job
  rows; invalid input raises ValueError. It calls durations.normalize.
- report.generate(payload): return the report or {"error":"invalid_input"}.
  The payload is an object with an attempts list. Additional payload keys are
  ignored. Additional attempt keys are ignored.
- python -B report.py: read one JSON payload from stdin, emit one JSON result
  and a newline. Invalid JSON emits {"error":"invalid_input"}. Exit normally.
  Imports must not consume stdin or print. Use only the Python standard library.

## Complete requirements
Read docs/durations.md, docs/attempts.md and docs/report.md. These documents are
normative, including error, unknown, zero, final-state and ordering rules.
Run python -B -m unittest discover -s tests -v and preserve the complete output
and direct exit. Passing public tests alone is not completion; external hidden
checks cover additional instances of these same documented requirements.
''',
    'docs/durations.md': '''# Duration requirements

## D1: Duration values
A duration is absent or null (unknown), or an object with exactly two keys:
value and unit. The unit must be the exact string ms or s. The value must be
an int or float, excluding bool, finite and nonnegative. Zero is valid.
Normalize ms unchanged and s multiplied by 1000. Do not round or truncate.
The normalized value must be representable as a finite number; reject overflow.
Strings, missing value/unit, extra duration keys and unsupported units are invalid.

## D2: Arithmetic
All duration sums must be finite. Reject overflow as invalid input. Numeric JSON
fields may use integer or float encodings; bool is never a numeric output.
Do not replace unknown duration with zero. Unknowns have the separate rules in A3.
''',
    'docs/attempts.md': '''# Attempt requirements

## A1: Attempt identity
records must be a list. Each record must be an object with job, attempt and
status. job is a string with at least one non-whitespace character; preserve
its exact identity. attempt is an integer >= 1, excluding bool. status is the
exact string success, failed or stopped. duration is optional, as specified in
D1. A duplicate (job, attempt) is invalid even when both records are identical.
Attempt numbers may have gaps. Input order is arbitrary. Empty records are valid.

## A2: Final state
Group by exact job identity. The final attempt is the largest numeric attempt
number, not the last input row. Its status alone is the job state. Earlier success
does not override a final failed or stopped attempt. attempts is the count of
actual records for that job; last_attempt is the largest attempt number.
Sum durations across ALL attempts, including failed and stopped attempts.

## A3: Unknown duration
For each job, unknown_attempts counts absent or null durations. known_duration_ms
is the sum of known durations, with zero for no known durations. duration_ms is
that sum only when unknown_attempts is zero; otherwise it is null. This includes
unknown durations on an earlier failed attempt even if the final success is known.
Zero duration is known, and does not increment unknown_attempts.
''',
    'docs/report.md': '''# Report requirements

## R1: Stable report
The result has exactly jobs and totals keys. jobs is an array sorted by job using
Python string ordering. Each job row has exactly job, attempts, last_attempt,
state, duration_ms, known_duration_ms and unknown_attempts. state uses the final
attempt status, with the same success/failed/stopped enum.
Totals has exactly jobs, successful_jobs, failed_jobs, stopped_jobs,
known_duration_ms, duration_ms and unknown_attempts. jobs counts job rows.
State counts count JOBS, not attempts. known_duration_ms sums known durations
across all attempts. unknown_attempts sums job unknown counts. duration_ms is
null if any attempt is unknown; otherwise it is the full known sum. An empty
batch has an empty jobs array and every total numeric field equal to zero.
Retain unrounded milliseconds. Numeric fields must be finite, never bool.

## R2: Invalid input
If ANY record, duration, duplicate identity, payload shape or sum is invalid,
report.generate returns exactly {"error":"invalid_input"}. Do not silently
skip malformed records or return partial jobs. A missing attempts key or a
non-list attempts value is invalid. Use ValueError between internal modules.
''',
    'durations.py': '''def normalize(duration):
    if not duration or not duration.get("value"):
        return None
    value = float(duration["value"])
    return value * 1000 if duration.get("unit") == "s" else value / 1000
''',
    'attempts.py': '''from durations import normalize

def summarize(records):
    groups = {}
    for record in records:
        job = record["job"]
        row = groups.setdefault(job, {"job": job, "attempts": 0, "last_attempt": 0,
            "state": "failed", "duration_ms": 0, "known_duration_ms": 0, "unknown_attempts": 0})
        row["attempts"] += 1
        row["last_attempt"] = record["attempt"]
        if record["status"] == "success":
            row["state"] = "success"
        amount = normalize(record.get("duration"))
        row["known_duration_ms"] += amount or 0
        row["duration_ms"] = row["known_duration_ms"]
    return list(groups.values())
''',
    'report.py': '''import json
import sys
from attempts import summarize

def generate(payload):
    rows = summarize(payload["attempts"])
    total = round(sum(row["known_duration_ms"] for row in rows), 2)
    return {"jobs": rows, "totals": {"jobs": len(rows),
        "successful_jobs": sum(row["state"] == "success" for row in rows),
        "failed_jobs": sum(row["state"] == "failed" for row in rows),
        "stopped_jobs": sum(row["state"] == "stopped" for row in rows),
        "known_duration_ms": total, "duration_ms": total, "unknown_attempts": 0}}

if __name__ == "__main__":
    print(json.dumps(generate(json.load(sys.stdin))))
''',
    'tests/test_public.py': '''import unittest
from durations import normalize
from report import generate

class PublicContract(unittest.TestCase):
    def test_duration_zero_and_units(self):
        self.assertEqual(normalize({"value": 0, "unit": "ms"}), 0)
        self.assertEqual(normalize({"value": 0.125, "unit": "s"}), 125)
        self.assertEqual(normalize({"value": 0.125, "unit": "ms"}), 0.125)

    def test_largest_attempt_controls_state(self):
        result = generate({"attempts": [
            {"job": "j", "attempt": 4, "status": "failed", "duration": {"value": 1, "unit": "s"}},
            {"job": "j", "attempt": 2, "status": "success", "duration": {"value": 2, "unit": "ms"}}]})
        row = result["jobs"][0]
        self.assertEqual((row["last_attempt"], row["state"], row["attempts"]), (4, "failed", 2))
        self.assertEqual(row["duration_ms"], 1002)

    def test_unknown_is_separate_from_known_zero(self):
        result = generate({"attempts": [{"job": "j", "attempt": 1, "status": "stopped"}]})
        self.assertIsNone(result["totals"]["duration_ms"])
        self.assertEqual(result["totals"]["unknown_attempts"], 1)
        self.assertEqual(result["totals"]["known_duration_ms"], 0)

    def test_invalid_duration_is_whole_input_error(self):
        self.assertEqual(generate({"attempts": [{"job": "j", "attempt": 1,
            "status": "success", "duration": {"value": True, "unit": "ms"}}]}), {"error": "invalid_input"})
''',
}

# Explicit reference implementation, evaluator-side only; never included by build.
REFERENCE = {
    'durations.py': '''import math

def normalize(duration):
    if duration is None:
        return None
    if not isinstance(duration, dict) or set(duration) != {"value", "unit"}:
        raise ValueError("duration")
    value, unit = duration["value"], duration["unit"]
    if type(value) not in (int, float) or unit not in ("ms", "s") or type(unit) is not str:
        raise ValueError("duration")
    try:
        amount = value if unit == "ms" else value * 1000
        if not math.isfinite(amount) or amount < 0:
            raise ValueError("duration")
    except (OverflowError, ValueError):
        raise ValueError("duration")
    return amount
''',
    'attempts.py': '''import math
from durations import normalize

def summarize(records):
    if not isinstance(records, list):
        raise ValueError("records")
    groups, seen = {}, set()
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("record")
        job, attempt, status = record.get("job"), record.get("attempt"), record.get("status")
        if not isinstance(job, str) or not job.strip() or type(attempt) is not int or attempt < 1 or status not in ("success", "failed", "stopped"):
            raise ValueError("record")
        identity = job, attempt
        if identity in seen:
            raise ValueError("duplicate")
        seen.add(identity)
        row = groups.setdefault(job, {"job": job, "attempts": 0, "last_attempt": 0,
            "state": "failed", "duration_ms": 0, "known_duration_ms": 0, "unknown_attempts": 0})
        row["attempts"] += 1
        if attempt > row["last_attempt"]:
            row["last_attempt"], row["state"] = attempt, status
        amount = normalize(record.get("duration"))
        if amount is None:
            row["unknown_attempts"] += 1
        else:
            row["known_duration_ms"] += amount
            try:
                if not math.isfinite(row["known_duration_ms"]):
                    raise ValueError("overflow")
            except OverflowError:
                raise ValueError("overflow")
    for row in groups.values():
        row["duration_ms"] = None if row["unknown_attempts"] else row["known_duration_ms"]
    return sorted(groups.values(), key=lambda row: row["job"])
''',
    'report.py': '''import json
import math
import sys
from attempts import summarize

def generate(payload):
    try:
        if not isinstance(payload, dict) or "attempts" not in payload:
            raise ValueError("payload")
        rows = summarize(payload["attempts"])
        known = sum(row["known_duration_ms"] for row in rows)
        if not math.isfinite(known):
            raise ValueError("overflow")
        unknown = sum(row["unknown_attempts"] for row in rows)
        return {"jobs": rows, "totals": {"jobs": len(rows),
            "successful_jobs": sum(row["state"] == "success" for row in rows),
            "failed_jobs": sum(row["state"] == "failed" for row in rows),
            "stopped_jobs": sum(row["state"] == "stopped" for row in rows),
            "known_duration_ms": known, "duration_ms": None if unknown else known,
            "unknown_attempts": unknown}}
    except (ValueError, OverflowError):
        return {"error": "invalid_input"}

if __name__ == "__main__":
    try:
        result = generate(json.load(sys.stdin))
    except ValueError:
        result = {"error": "invalid_input"}
    print(json.dumps(result, allow_nan=False))
''',
}

# Manually specified outcomes; no reference algorithm creates these expectations.
ORACLES = [
    ('empty', {'attempts': []}, {'jobs': [], 'totals': {'jobs': 0, 'successful_jobs': 0, 'failed_jobs': 0, 'stopped_jobs': 0, 'known_duration_ms': 0, 'duration_ms': 0, 'unknown_attempts': 0}}),
    ('mixed_units_zero_unknown_final', {'attempts': [
        {'job': 'beta', 'attempt': 9, 'status': 'failed', 'duration': {'value': .125, 'unit': 'ms'}},
        {'job': 'alpha', 'attempt': 4, 'status': 'success', 'duration': {'value': .125, 'unit': 's'}},
        {'job': 'beta', 'attempt': 2, 'status': 'success', 'duration': {'value': 0, 'unit': 'ms'}},
        {'job': 'alpha', 'attempt': 1, 'status': 'failed'},
        {'job': 'gamma', 'attempt': 3, 'status': 'stopped', 'duration': {'value': 0, 'unit': 's'}}]},
        {'jobs': [
            {'job': 'alpha', 'attempts': 2, 'last_attempt': 4, 'state': 'success', 'duration_ms': None, 'known_duration_ms': 125, 'unknown_attempts': 1},
            {'job': 'beta', 'attempts': 2, 'last_attempt': 9, 'state': 'failed', 'duration_ms': .125, 'known_duration_ms': .125, 'unknown_attempts': 0},
            {'job': 'gamma', 'attempts': 1, 'last_attempt': 3, 'state': 'stopped', 'duration_ms': 0, 'known_duration_ms': 0, 'unknown_attempts': 0}],
         'totals': {'jobs': 3, 'successful_jobs': 1, 'failed_jobs': 1, 'stopped_jobs': 1, 'known_duration_ms': 125.125, 'duration_ms': None, 'unknown_attempts': 1}}),
    ('known_retry_work', {'attempts': [
        {'job': 'j', 'attempt': 7, 'status': 'success', 'duration': {'value': 1.5, 'unit': 's'}},
        {'job': 'j', 'attempt': 1, 'status': 'failed', 'duration': {'value': 25, 'unit': 'ms'}}]},
        {'jobs': [{'job': 'j', 'attempts': 2, 'last_attempt': 7, 'state': 'success', 'duration_ms': 1525, 'known_duration_ms': 1525, 'unknown_attempts': 0}],
         'totals': {'jobs': 1, 'successful_jobs': 1, 'failed_jobs': 0, 'stopped_jobs': 0, 'known_duration_ms': 1525, 'duration_ms': 1525, 'unknown_attempts': 0}}),
    ('large_integer_ms', {'attempts': [
        {'job': 'large', 'attempt': 1, 'status': 'success', 'duration': {'value': 9007199254740993, 'unit': 'ms'}}]},
        {'jobs': [{'job': 'large', 'attempts': 1, 'last_attempt': 1, 'state': 'success', 'duration_ms': 9007199254740993, 'known_duration_ms': 9007199254740993, 'unknown_attempts': 0}],
         'totals': {'jobs': 1, 'successful_jobs': 1, 'failed_jobs': 0, 'stopped_jobs': 0, 'known_duration_ms': 9007199254740993, 'duration_ms': 9007199254740993, 'unknown_attempts': 0}}),
    ('large_integer_seconds', {'attempts': [
        {'job': 'large', 'attempt': 1, 'status': 'success', 'duration': {'value': 9007199254740993, 'unit': 's'}}]},
        {'jobs': [{'job': 'large', 'attempts': 1, 'last_attempt': 1, 'state': 'success', 'duration_ms': 9007199254740993000, 'known_duration_ms': 9007199254740993000, 'unknown_attempts': 0}],
         'totals': {'jobs': 1, 'successful_jobs': 1, 'failed_jobs': 0, 'stopped_jobs': 0, 'known_duration_ms': 9007199254740993000, 'duration_ms': 9007199254740993000, 'unknown_attempts': 0}}),
    ('exact_identity_and_ignored_keys', {'extra_payload': 'ignored', 'attempts': [
        {'job': 'j', 'attempt': 1, 'status': 'success', 'extra_attempt': 7, 'duration': {'value': 2, 'unit': 'ms'}},
        {'job': ' j ', 'attempt': 1, 'status': 'stopped', 'extra_attempt': False, 'duration': {'value': 3, 'unit': 'ms'}}]},
        {'jobs': [
            {'job': ' j ', 'attempts': 1, 'last_attempt': 1, 'state': 'stopped', 'duration_ms': 3, 'known_duration_ms': 3, 'unknown_attempts': 0},
            {'job': 'j', 'attempts': 1, 'last_attempt': 1, 'state': 'success', 'duration_ms': 2, 'known_duration_ms': 2, 'unknown_attempts': 0}],
         'totals': {'jobs': 2, 'successful_jobs': 1, 'failed_jobs': 0, 'stopped_jobs': 1, 'known_duration_ms': 5, 'duration_ms': 5, 'unknown_attempts': 0}}),
    ('all_unknown', {'attempts': [{'job': 'j', 'attempt': 1, 'status': 'stopped', 'duration': None},
                                {'job': 'j', 'attempt': 3, 'status': 'failed'}]},
        {'jobs': [{'job': 'j', 'attempts': 2, 'last_attempt': 3, 'state': 'failed', 'duration_ms': None, 'known_duration_ms': 0, 'unknown_attempts': 2}],
         'totals': {'jobs': 1, 'successful_jobs': 0, 'failed_jobs': 1, 'stopped_jobs': 0, 'known_duration_ms': 0, 'duration_ms': None, 'unknown_attempts': 2}}),
]
INVALID_RECORDS = [
    {'job': 'j', 'attempt': 1, 'status': 'success', 'duration': {'value': True, 'unit': 'ms'}},
    {'job': 'j', 'attempt': 1, 'status': 'success', 'duration': {'value': -1, 'unit': 'ms'}},
    {'job': 'j', 'attempt': 1, 'status': 'success', 'duration': {'value': float('inf'), 'unit': 's'}},
    {'job': 'j', 'attempt': 1, 'status': 'success', 'duration': {'value': float('nan'), 'unit': 'ms'}},
    {'job': 'j', 'attempt': 1, 'status': 'success', 'duration': {'value': '2', 'unit': 'ms'}},
    {'job': 'j', 'attempt': 1, 'status': 'success', 'duration': {'value': 2, 'unit': 'MS'}},
    {'job': 'j', 'attempt': 1, 'status': 'success', 'duration': {'value': None, 'unit': 'ms'}},
    {'job': 'j', 'attempt': 1, 'status': 'success', 'duration': {'value': 0}},
    {'job': 'j', 'attempt': 1, 'status': 'success', 'duration': {'value': 1, 'unit': 'ms', 'extra': 1}},
    {'job': 'j', 'attempt': True, 'status': 'success'},
    {'job': 'j', 'attempt': 0, 'status': 'success'},
    {'job': ' ', 'attempt': 1, 'status': 'success'},
    {'job': 'j', 'attempt': 1, 'status': 'pending'},
    {'job': 'j', 'attempt': 1},
    17,
]


def _write(root, files):
    for name, content in files.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)


def build(workspace):
    root = Path(workspace)
    root.mkdir(parents=True, exist_ok=False)
    _write(root, FILES)
    digest = hashlib.sha256(json.dumps(FILES, sort_keys=True).encode()).hexdigest()
    return {'prompt': 'Repair the three dependent modules according to CONTRACT.md and its normative documents. '
            'Choose direct ownership or the optional independent retrieval lane only if it replaces useful owner reading. '
            'Complete the named public check, preserve its full log/direct exit, and return changed paths, checks and limits. '
            'Do not alter tests, documentation or other files. This is one synthetic diagnostic; it establishes no scientific '
            'result, representative reliability or long-task savings.',
            'writable_paths': WRITABLE_PATHS.copy(), 'public_command': PUBLIC_COMMAND.copy(),
            'retrieval_task': RETRIEVAL_TASK, 'fixture_sha256': digest}


def install_reference(workspace):
    """Offline unit-test helper only. Caller must never offer it to a native arm."""
    _write(Path(workspace), REFERENCE)


def _equal(actual, expected):
    if isinstance(expected, (int, float)) and type(expected) is not bool:
        return type(actual) in (int, float) and math.isfinite(actual) and actual == expected
    if type(actual) is not type(expected):
        return False
    if isinstance(expected, dict):
        return set(actual) == set(expected) and all(_equal(actual[k], v) for k, v in expected.items())
    if isinstance(expected, list):
        return len(actual) == len(expected) and all(_equal(a, b) for a, b in zip(actual, expected))
    return actual == expected


def _probe(workspace, payload, *, raw=False, entrypoint="cli"):
    prefix = 'import sys,json;sys.path.insert(0,sys.argv[1]);'
    if entrypoint == "cli":
        launcher = prefix + 'import runpy;runpy.run_path(sys.argv[1]+"/report.py",run_name="__main__")'
    elif entrypoint == "imports":
        launcher = prefix + """
class ForbiddenInput:
    def read(self, *a, **k): raise RuntimeError("import consumed stdin")
    readline = read
    readlines = read
    __iter__ = read
class ForbiddenOutput:
    def write(self, *a, **k): raise RuntimeError("import emitted output")
    def flush(self): pass
saved = sys.stdin, sys.stdout, sys.stderr
sys.stdin, sys.stdout, sys.stderr = ForbiddenInput(), ForbiddenOutput(), ForbiddenOutput()
try:
    import durations, attempts, report
finally:
    sys.stdin, sys.stdout, sys.stderr = saved
print(json.dumps({"import_silent": True}))
"""
    else:
        module, function = entrypoint.split(".")
        launcher = prefix + f"""
import {module}
payload = json.load(sys.stdin)
try:
    actual = {module}.{function}(payload)
except ValueError:
    actual = {{"raised": "ValueError"}}
print(json.dumps(actual, allow_nan=False))
"""
    command = [sys.executable, '-I', '-B', '-c', launcher, str(Path(workspace).resolve())]
    record = {'entrypoint': entrypoint, 'payload': payload, 'raw_input': raw,
              'command': command, 'actual': None, 'returncode': None,
              'stdout': '', 'stderr': '', 'timed_out': False, 'error': None}
    try:
        run = subprocess.run(command, input=payload if raw else json.dumps(payload),
                             text=True, capture_output=True, timeout=3)
        record.update(returncode=run.returncode, stdout=run.stdout, stderr=run.stderr)
        if run.returncode == 0:
            try:
                record['actual'] = json.loads(run.stdout)
            except ValueError as exc:
                record['error'] = str(exc)
    except subprocess.TimeoutExpired as exc:
        record.update(timed_out=True, stdout=_text(exc.stdout), stderr=_text(exc.stderr), error=str(exc))
    except OSError as exc:
        record['error'] = str(exc)
    return record


def _text(value):
    return value.decode(errors='replace') if isinstance(value, bytes) else (value or '')


def validate(workspace, *, evidence_path=None):
    """Return strict booleans; optionally save full evaluator-only probe receipts.

    Each subprocess is isolated (-I/-B), bounded to three seconds, and runs only
    synthetic software. evidence_path must be outside the model workspace.
    Receipts retain Python JSON NaN/Infinity literals used as invalid-input tests.
    This is execution isolation, not a security sandbox for arbitrary programs.
    """
    if evidence_path is not None:
        target = Path(evidence_path).resolve()
        if target == Path(workspace).resolve() or Path(workspace).resolve() in target.parents:
            raise ValueError('hidden evidence must remain outside workspace')
    results, probes = {}, []

    def check(name, payload, expected, *, raw=False, entrypoint='cli'):
        record = _probe(workspace, payload, raw=raw, entrypoint=entrypoint)
        passed = (record['returncode'] == 0 and record['error'] is None
                  and _equal(record['actual'], expected))
        record.update(name=name, expected=expected, passed=passed)
        probes.append(record)
        results[name] = passed

    for name, payload, expected in ORACLES:
        check(name, payload, expected)
    error = {'error': 'invalid_input'}
    for n, record in enumerate(INVALID_RECORDS):
        payload = {'attempts': [{'job': 'valid', 'attempt': 1, 'status': 'success', 'duration': {'value': 1, 'unit': 'ms'}}, record]}
        check('invalid_record_' + str(n), payload, error)
    row = {'job': 'j', 'attempt': 1, 'status': 'success'}
    check('duplicate_identity', {'attempts': [row, row]}, error)
    for n, payload in enumerate((None, [], {}, {'attempts': None}, {'attempts': {}})):
        check('invalid_payload_' + str(n), payload, error)
    check('invalid_json', '{bad', error, raw=True)
    check('normalization_overflow', {'attempts': [
        {'job': 'j', 'attempt': 1, 'status': 'success', 'duration': {'value': 1e308, 'unit': 's'}}]}, error)
    check('sum_overflow', {'attempts': [
        {'job': 'j', 'attempt': 1, 'status': 'success', 'duration': {'value': 1e308, 'unit': 'ms'}},
        {'job': 'k', 'attempt': 1, 'status': 'success', 'duration': {'value': 1e308, 'unit': 'ms'}}]}, error)
    for name, value, expected in [
        ('zero', {'value': 0, 'unit': 'ms'}, 0),
        ('fraction', {'value': .125, 'unit': 'ms'}, .125),
        ('seconds', {'value': 1.5, 'unit': 's'}, 1500),
        ('unknown', None, None),
        ('large_ms', {'value': 9007199254740993, 'unit': 'ms'}, 9007199254740993),
        ('large_seconds', {'value': 9007199254740993, 'unit': 's'}, 9007199254740993000)]:
        check('normalize_api_' + name, value, expected, entrypoint='durations.normalize')
    for n, record in enumerate(INVALID_RECORDS[:9]):
        check('normalize_api_invalid_' + str(n), record['duration'], {'raised': 'ValueError'},
              entrypoint='durations.normalize')
    for name, payload, expected in ORACLES:
        check('summarize_api_' + name, payload['attempts'], expected['jobs'], entrypoint='attempts.summarize')
    check('summarize_api_duplicate', [row, row], {'raised': 'ValueError'}, entrypoint='attempts.summarize')
    check('summarize_api_invalid', [INVALID_RECORDS[0]], {'raised': 'ValueError'}, entrypoint='attempts.summarize')
    check('summarize_api_not_list', {}, {'raised': 'ValueError'}, entrypoint='attempts.summarize')
    for name, payload, expected in ORACLES:
        check('generate_api_' + name, payload, expected, entrypoint='report.generate')
    check('generate_api_invalid', {'attempts': [INVALID_RECORDS[0]]}, error, entrypoint='report.generate')
    check('imports_silent', None, {'import_silent': True}, entrypoint='imports')
    if evidence_path is not None:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps({'checks': results, 'probes': probes,
            'limits': 'Synthetic bounded software probes; no scientific or general reliability claim.'}, indent=2) + '\n')
    return results
