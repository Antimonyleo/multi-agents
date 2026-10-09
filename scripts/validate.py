#!/usr/bin/env python3
"""Local structure/provenance checks; no model calls or scientific execution."""
import hashlib
import json
from pathlib import Path
import re
import tomllib

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skill/scientific-workflow'


def validate():
    entry = (SKILL / 'SKILL.md').read_text()
    assert entry.startswith('---\n'), 'missing frontmatter'
    header = entry.split('---', 2)[1]
    assert re.search(r'^name: scientific-workflow$', header, re.M), 'invalid skill name'
    assert re.search(r'^description: .+', header, re.M), 'missing description'
    checked = 0
    # Historical sources and frozen benchmark documents can contain original host paths.
    documents = [ROOT / 'README.md', ROOT / 'docs/consolidation.md'] + list(SKILL.rglob('*.md'))
    for path in documents:
        if path.read_text().count('```') % 2:
            raise AssertionError(f'unclosed code fence: {path}')
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', path.read_text()):
            if target.startswith(('https://', 'http://', '#')):
                continue
            assert not target.startswith('/home/'), f'active home-specific link: {path}: {target}'
            dest = path.parent / target.split('#')[0]
            assert dest.exists(), f'broken local reference: {path}: {target}'
            checked += 1
    roles = {'explorer': ('gpt-6-luna', 'high', 'read-only'),
             'researcher': ('gpt-6-luna', 'high', 'read-only'),
             'worker': ('gpt-6.1-sol', 'medium', 'workspace-write'),
             'analyst': ('gpt-6.1-sol', 'high', 'workspace-write'),
             'reviewer': ('gpt-6-astra', 'high', 'read-only')}
    for role, expected in roles.items():
        name = f'scientific_{role}'
        data = tomllib.loads((ROOT / 'agents/codex' / f'{name}.toml').read_text())
        assert data['name'] == name
        assert (data['model'], data['model_reasoning_effort'], data['sandbox_mode']) == expected, name
        assert data['developer_instructions'].strip(), name
    identity = json.loads((ROOT / 'docs/migration/2026-10-09/source-identities.json').read_text())
    original_root = '/home/hao/githubrepo/scientific-workflow-skill/'
    protected = 0
    for original, evidence in identity.items():
        if not original.startswith(original_root):
            continue
        relative = original[len(original_root):]
        if relative.startswith(('agents/', 'benchmarks/')) or relative == 'settings/settings.snippet.json':
            assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == evidence['sha256'], relative
            protected += 1
    json.loads((ROOT / 'settings/settings.snippet.json').read_text())
    print(f'PASS: {checked} local links, {len(roles)} Codex profiles, {protected} protected Claude/benchmark files')


if __name__ == '__main__':
    validate()
