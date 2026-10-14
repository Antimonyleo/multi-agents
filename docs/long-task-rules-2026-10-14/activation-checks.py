"""Post-activation static/install checks, with complete logs and direct exits."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import subprocess
import time
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
STAGE = ROOT / 'staging/long-task-rules-2026-10-14/scientific-workflow'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(item):
    name, command = item
    start = time.monotonic()
    r = subprocess.run(command, cwd=ROOT, capture_output=True)
    log = OUT / (name + '.log')
    log.write_bytes(r.stdout + r.stderr)
    return name, {'command': command, 'returncode': r.returncode, 'wall_s': time.monotonic() - start,
                  'log': log.name, 'log_sha256': sha(log)}
if __name__ == '__main__':
    matches = all(sha(p) == sha(ROOT / 'skill/scientific-workflow' / p.relative_to(STAGE))
                  for p in STAGE.rglob('*.md'))
    if not matches: raise SystemExit('Live skill differs from reviewed candidate')
    commands = [('activated-structure', ['python', 'scripts/validate.py']),
                ('activated-skill', ['/usr/bin/python3', '/home/hao/.codex/skills/.system/skill-creator/scripts/quick_validate.py', 'skill/scientific-workflow']),
                ('installed-links', ['bash', 'scripts/install.sh', '--target', 'both', '--check']),
                ('instruction-health', ['agent-workflow', 'check', '--repo', str(ROOT)])]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        checks = dict(pool.map(run, commands))
    protected = json.loads((OUT / 'preservation-before.json').read_text())
    changed = [p for p, h in protected.items() if sha(p) != h]
    receipt = {'checks': checks, 'matches_reviewed_candidate': matches,
               'candidate_sha256': {str(p.relative_to(STAGE)): sha(p) for p in STAGE.rglob('*.md')},
               'protected_identities_checked': len(protected), 'protected_changes': changed,
               'review_sha256': sha(OUT / 'review.json')}
    (OUT / 'activation.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'checks': {k: v['returncode'] for k, v in checks.items()},
                      'matches_reviewed_candidate': matches, 'protected_changes': changed}, indent=2))
    raise SystemExit(not (matches and not changed and all(c['returncode'] == 0 for c in checks.values())))
