"""Required offline checks, full logs/direct exits and frozen source identities."""
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
STAGE = ROOT / 'staging/long-task-rules-2026-10-14/scientific-workflow'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def sources():
    names = subprocess.check_output(['git', 'ls-files', 'scripts', 'tests'], cwd=ROOT, text=True).splitlines()
    return {str(p.relative_to(ROOT)): sha(p) for p in [*(ROOT / n for n in names), *STAGE.rglob('*.md')] if p.is_file()}
def run(item):
    name, command = item
    start = time.monotonic()
    result = subprocess.run(command, cwd=ROOT, capture_output=True)
    log = OUT / (name + '.log')
    log.write_bytes(result.stdout + result.stderr)
    return name, {'command': command, 'returncode': result.returncode, 'wall_s': time.monotonic() - start,
                  'log': log.name, 'log_sha256': sha(log), 'capture': 'Complete stdout followed by complete stderr; direct process exit.'}
if __name__ == '__main__':
    scratch_base = os.environ.get('TMPDIR') or '/home/hao/.cache/codex-scratch'
    scratch = subprocess.check_output(['mktemp', '-d', str(Path(scratch_base) / 'task.XXXXXX')], text=True).strip()
    os.environ['TMPDIR'] = scratch
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    before = sources()
    commands = [('structure', ['python', 'scripts/validate.py']),
                ('full-suite', ['python', '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-v']),
                ('staged-skill', ['/usr/bin/python3', '/home/hao/.codex/skills/.system/skill-creator/scripts/quick_validate.py', str(STAGE)])]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        checks = dict(pool.map(run, commands))
    after = sources()
    receipt = {'checks': checks, 'source_sha256': after, 'sources_unchanged': before == after,
               'scratch_retained': scratch, 'no_model_or_scientific_execution': True}
    (OUT / 'validation.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'checks': {k: v['returncode'] for k, v in checks.items()},
                      'sources_unchanged': before == after, 'scratch_retained': scratch}, indent=2))
    raise SystemExit(not (before == after and all(c['returncode'] == 0 for c in checks.values())))
