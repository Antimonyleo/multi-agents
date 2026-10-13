"""Offline maintenance validation; full logs and direct exits, no native models."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
SOURCES = ['scripts/implementation_fixture.py', 'tests/test_implementation_fixture.py',
           'staging/contract-boundary-2026-10-13/scientific-workflow/maintenance.md']
def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def run(name, command):
    start = time.monotonic()
    result = subprocess.run(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    log = OUT / (name + '.log')
    log.write_bytes(result.stdout)
    return name, {'command': command, 'returncode': result.returncode,
                  'wall_s': time.monotonic() - start, 'log': log.name, 'log_sha256': sha(log)}
if __name__ == '__main__':
    before = {s: sha(ROOT / s) for s in SOURCES}
    commands = [('structure', ['python', 'scripts/validate.py']),
                ('full-suite', ['python', '-m', 'unittest', 'discover', '-s', 'tests', '-v']),
                ('staged-skill', ['python', '/home/hao/.codex/skills/.system/skill-creator/scripts/quick_validate.py',
                                  'staging/contract-boundary-2026-10-13/scientific-workflow'])]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        checks = dict(pool.map(lambda item: run(*item), commands))
    after = {s: sha(ROOT / s) for s in SOURCES}
    receipt = {'checks': checks, 'source_sha256': after, 'sources_unchanged': before == after}
    (OUT / 'validation.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))
    raise SystemExit(not (before == after and all(c['returncode'] == 0 for c in checks.values())))
