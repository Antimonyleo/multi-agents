"""Activate one independently reviewed rule; commits remain separate owner actions."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
STAGE = ROOT / 'staging/long-task-rules-2026-10-14/scientific-workflow'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
if __name__ == '__main__':
    rule = sys.argv[1]
    if rule not in ('1', '2'): raise SystemExit('Expected rule1 or rule2')
    review = json.loads((OUT / 'review.json').read_text())
    if not review['accepted']: raise SystemExit('Independent review not accepted')
    inputs = json.loads((OUT / 'review-input.json').read_text())
    if any(sha(ROOT / p) != digest for p, digest in inputs.items()):
        raise SystemExit('Reviewed input differs')
    patch = OUT / ('rule1-checkpoint.patch' if rule == '1' else 'rule2-waits-qualified.patch')
    subprocess.run(['git', 'apply', '--check', str(patch)], cwd=ROOT, check=True)
    subprocess.run(['git', 'apply', str(patch)], cwd=ROOT, check=True)
    expected_names = ['SKILL.md'] if rule == '1' else ['SKILL.md', 'references/coordination.md', 'references/rationale.md']
    for name in expected_names:
        if sha(ROOT / 'skill/scientific-workflow' / name) != sha(STAGE / name):
            raise SystemExit('Activation mismatch: ' + name)
    print('Activated reviewed rule' + rule + '; no allocation or scientific authority changed.')
