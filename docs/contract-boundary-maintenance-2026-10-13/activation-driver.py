"""Verify byte-identical guidance activation; no installation or model calls."""
import hashlib
import json
from pathlib import Path
import importlib.util
import shutil
spec = importlib.util.spec_from_file_location('validation_driver', Path(__file__).with_name('validation-driver.py'))
validation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validation)
ROOT, OUT = validation.ROOT, validation.OUT

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
if __name__ == '__main__':
    review = json.loads((OUT / 'completion-review.json').read_text())
    if not review['accepted']:
        raise SystemExit('Exact-version review not accepted')
    inputs = json.loads((OUT / 'review-input.json').read_text())
    for path, expected in inputs.items():
        if sha(ROOT / path) != expected:
            raise SystemExit('Reviewed input changed: ' + path)
    source = ROOT / 'staging/contract-boundary-2026-10-13/scientific-workflow/maintenance.md'
    target = ROOT / 'skill/scientific-workflow/maintenance.md'
    shutil.copyfile(source, target)
    commands = [('activated-structure', ['python', 'scripts/validate.py']),
                ('activated-skill', ['python', '/home/hao/.codex/skills/.system/skill-creator/scripts/quick_validate.py', 'skill/scientific-workflow']),
                ('installed-links', ['bash', 'scripts/install.sh', '--target', 'both', '--check']),
                ('instruction-health', ['agent-workflow', 'check', '--repo', str(ROOT)])]
    checks = dict(validation.run(*item) for item in commands)
    receipt = {'checks': checks, 'review_input_sha256': sha(OUT / 'review-input.json'),
               'completion_review_sha256': sha(OUT / 'completion-review.json'),
               'maintenance_sha256': sha(target), 'matches_reviewed_candidate': sha(source) == sha(target)}
    (OUT / 'activation.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))
    raise SystemExit(not (receipt['matches_reviewed_candidate'] and all(c['returncode'] == 0 for c in checks.values())))
