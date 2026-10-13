"""Build one evidence packet per session for blind outcome labelling (PLAN.md, Amendment 2). Read-only.

Each packet holds the session's user prompts in order (no-stop and continue phrases
redacted), the agent's report before each prompt, its last reports, its helpers, and the
first prompts of later sessions in the same project. Packets contain no signal values.
Output: packets/<session>.md and packets/index.json (local only; see .gitignore).
"""
import json
from pathlib import Path

import extract as X
import signals as SG

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'packets'
REDACT = (SG.CATEGORIES['continue_broad'], SG.CATEGORIES['continue_no_pause'])


def redact(text):
    for rx in REDACT:
        text = rx.sub('[…]', text)
    return text


def cwd_of(path):
    with open(path) as fh:
        for i, line in enumerate(fh):
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            cwd = r.get('cwd') or (r.get('payload') or {}).get('cwd')
            if cwd or i > 50:
                return cwd


def final_reports(entry, n=6):
    texts = []
    for r in X.read_prefix(entry):
        if entry['runtime'] == 'claude' and r.get('type') == 'assistant':
            for c in (r.get('message') or {}).get('content') or []:
                if isinstance(c, dict) and c.get('type') == 'text' and c.get('text', '').strip():
                    texts.append((r.get('timestamp', ''), c['text']))
        elif entry['runtime'] == 'codex' and r.get('type') == 'response_item':
            p = r.get('payload') or {}
            if p.get('type') == 'message' and p.get('role') == 'assistant':
                t = '\n'.join(c.get('text', '') for c in p.get('content') or [] if isinstance(c, dict))
                if t.strip():
                    texts.append((r.get('timestamp', ''), t))
    return texts[-n:]


def main():
    sample = json.loads((ROOT / 'sample.json').read_text())
    summary = {f['session'][:8]: f for f in json.loads((ROOT / 'summary.json').read_text())['families']}
    ctx = json.loads((ROOT / 'prompt-context.json').read_text())
    parents = [e for e in sample['entries'] if e['role'] == 'parent']
    for e in parents:
        e['sid'] = Path(e['path']).stem[-36:][:8]
        e['cwd'] = cwd_of(e['path'])
    OUT.mkdir(exist_ok=True)
    index = []
    for e in parents:
        sid, f = e['sid'], summary[e['sid']]
        later = sorted((p for p in parents if p['cwd'] == e['cwd'] and summary[p['sid']]['start'] > f['start']),
                       key=lambda p: summary[p['sid']]['start'])
        lines = [f'# Session {sid}', '',
                 f"- Runtime: {e['runtime']}; project directory: `{e['cwd']}`",
                 f"- Start {f['start'][:16]}, last record {(f['last_record'] or '')[:16]}; "
                 f"still running when frozen: {'yes' if f['live_at_freeze'] else 'no'}",
                 f"- User prompts: {f['user_prompts']}; helper sessions: {len(f['helpers'])}", '',
                 '## User prompts in order, each with the agent report just before it', '',
                 'Phrases asking the agent to continue or not to stop are replaced by […].', '']
        for p in ctx[sid]:
            lines += [f"### Prompt {p['i']}", '', f"Agent before: {X.excerpt(p['before'], 400) or '(none)'}", '',
                      f"User: {X.excerpt(redact(p['prompt']), 700)}", '']
        lines += ['## Last agent reports in the session', '']
        for t, text in final_reports(e):
            lines += [f'### {t[:16]}', '', X.excerpt(text, 1500), '']
        lines += ['## Helpers', '']
        if e['runtime'] == 'claude':
            children = [c for c in sample['entries'] if c.get('parent') == e['path']]
            for c in children:
                m = c.get('meta', {})
                lines.append(f"- {m.get('agentType')} ({m.get('model') or 'inherited'}): {m.get('description')}")
        else:
            roles = {}
            for h in f['helpers']:
                key = (h['kind'], h.get('agent_role') or '-', max(h['models'], key=h['models'].get) if h['models'] else '-')
                roles[key] = roles.get(key, 0) + 1
            lines += [f'- {n} × {kind}, role {role}, model {model}' for (kind, role, model), n in sorted(roles.items())]
            lines.append('- Codex helper task texts are not available in this packet.')
        lines += ['', '## Later sessions in the same project directory (first prompt)', '']
        for p in later:
            first = ctx[p['sid']][0]['prompt'] if ctx[p['sid']] else ''
            lines.append(f"- {p['sid']} ({summary[p['sid']]['start'][:10]}): {X.excerpt(redact(first), 400)}")
        if not later:
            lines.append('- none in the sample')
        (OUT / f'{sid}.md').write_text('\n'.join(lines) + '\n')
        index.append(dict(session=sid, runtime=e['runtime'], cwd=e['cwd'], start=f['start'][:10],
                          end=(f['last_record'] or '')[:10], chars=len('\n'.join(lines))))
    (OUT / 'index.json').write_text(json.dumps(index, indent=1) + '\n')
    print(len(index), 'packets;', sum(i['chars'] for i in index), 'chars')


if __name__ == '__main__':
    main()
