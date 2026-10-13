"""Run the named offline maintenance checks with complete retained receipts."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
if len(sys.argv) > 1:
    OUT = OUT / sys.argv[1]
    OUT.mkdir(exist_ok=False)
scratch_root = Path(os.environ.get('TMPDIR') or '/home/hao/.cache/codex-scratch')
scratch_root.mkdir(parents=True, exist_ok=True)
scratch = tempfile.mkdtemp(prefix='task.', dir=scratch_root)
env = dict(os.environ, TMPDIR=scratch, PYTHONDONTWRITEBYTECODE='1')
commands = {
    'full-suite': ['python', '-m', 'unittest', 'discover', '-s', 'tests', '-v'],
    'structure': ['python', 'scripts/validate.py'],
    'skill-structure': ['python', '/home/hao/.codex/skills/.system/skill-creator/scripts/quick_validate.py',
                        'skill/scientific-workflow'],
}
paths = list((ROOT / 'scripts').glob('*.py')) + list((ROOT / 'tests').glob('*.py'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
before = {str(p.relative_to(ROOT)): sha(p) for p in paths}

def run(item):
    name, command = item
    start = time.monotonic()
    log = OUT / (name + '.log')
    with log.open('wb') as stream:
        result = subprocess.run(command, cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT)
    return name, {'command': command, 'returncode': result.returncode,
                  'wall_s': time.monotonic() - start, 'log': log.name, 'log_sha256': sha(log)}

with ThreadPoolExecutor(max_workers=3) as pool:
    checks = dict(pool.map(run, commands.items()))
report = {'checks': checks, 'source_sha256': before,
          'sources_unchanged': all(p.exists() and sha(p) == before[str(p.relative_to(ROOT))] for p in paths),
          'scratch_retained': scratch}
(OUT / 'validation.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
print(json.dumps({k: v['returncode'] for k, v in checks.items()}))
print('Sources unchanged:', report['sources_unchanged'])
raise SystemExit(0 if report['sources_unchanged'] and all(v['returncode'] == 0 for v in checks.values()) else 1)
