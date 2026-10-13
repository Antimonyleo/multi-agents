"""Second pass over frozen parents: prompt categories and Bash-aware redo-after-helper. Read-only."""
import collections
import json
import re
from pathlib import Path

import extract as X

ROOT = Path(__file__).resolve().parent
CATEGORIES = {
    'continue_no_pause': re.compile(r"no need to (stop|pause|ask|wait)|do ?n[o']t (stop|pause)|without (stopping|pausing)|"
                                    r"(continue|keep going|proceed)\b.{0,40}\b(all|until|through|execut)|this is an override", re.I),
    'overengineering': re.compile(r"over-?engineer|too defensive|so defensive|too cautious|too conservative", re.I),
    'status_check': re.compile(r"\b(status|progress|still running|any update|how is it going|is it done|finished\?)", re.I),
    'disagreement': re.compile(r"i (do not|don'?t) (think|believe|agree)|that'?s (wrong|not right|not what)|incorrect|"
                               r"not what i|you (misunderstood|didn'?t|did not|forgot|missed)", re.I),
    'repeat_request': re.compile(r"\b(again|as i said|i said|i already|i told you)\b", re.I),
}


def path_tokens(text):
    return set(re.findall(r'[\w./-]+\.(?:py|md|json|toml|yaml|yml|txt|csv|log|sh|jsonl|ipynb)\b', text or ''))


def main():
    sample = json.loads((ROOT / 'sample.json').read_text())
    children = collections.defaultdict(list)
    for e in sample['entries']:
        if e['role'] == 'child':
            children[e['parent']].append(e)
    out, examples = [], collections.defaultdict(list)
    for e in sample['entries']:
        if e['role'] != 'parent':
            continue
        records = X.read_prefix(e)
        if e['runtime'] == 'claude':
            m = X.claude_metrics(records)
        else:
            m = X.codex_metrics(records)
        prompts = m['_prompts']
        counts = collections.Counter()
        for p in prompts:
            for k, rx in CATEGORIES.items():
                if rx.search(p[:2000]):
                    counts[k] += 1
                    if len(examples[k]) < 40:
                        examples[k].append(dict(session=Path(e['path']).stem[-36:][:8], text=X.excerpt(p, 140)))
        row = dict(session=Path(e['path']).stem[-36:][:8], runtime=e['runtime'], prompts=len(prompts),
                   categories=dict(counts))
        if e['runtime'] == 'claude':
            # parent calls in order with the files each touches (Read path or Bash-mentioned paths)
            calls = []
            for r in records:
                if r.get('type') == 'assistant':
                    for c in (r.get('message') or {}).get('content') or []:
                        if isinstance(c, dict) and c.get('type') == 'tool_use':
                            inp = c.get('input') or {}
                            files = {inp['file_path']} if inp.get('file_path') else path_tokens(inp.get('command'))
                            calls.append((c.get('id'), c.get('name'), {Path(f).name for f in files}))
            redo = []
            for ch in children[e['path']]:
                crec = X.read_prefix(ch)
                cfiles = set()
                for r in crec:
                    if r.get('type') == 'assistant':
                        for c in (r.get('message') or {}).get('content') or []:
                            if isinstance(c, dict) and c.get('type') == 'tool_use':
                                inp = c.get('input') or {}
                                f = {inp['file_path']} if inp.get('file_path') else path_tokens(inp.get('command') or inp.get('pattern'))
                                cfiles |= {Path(x).name for x in f}
                idx = next((i for i, (cid, _, _) in enumerate(calls) if cid == ch.get('meta', {}).get('toolUseId')), None)
                if idx is None or not cfiles:
                    continue
                later = set()
                for _, name, files in calls[idx + 1: idx + 1 + X.REDO_WINDOW]:
                    if name not in X.EDIT_TOOLS:
                        later |= files
                redo.append(dict(agent_type=ch.get('meta', {}).get('agentType'), child_files=len(cfiles),
                                 parent_touched_same=len(later & cfiles)))
            row['redo'] = dict(helpers=len(redo), any_overlap=sum(1 for r in redo if r['parent_touched_same']),
                               overlap_ge3=sum(1 for r in redo if r['parent_touched_same'] >= 3))
        else:
            row['parent_model_calls'] = m['responses']
            row['orchestration_calls'] = m['orchestration_calls']
        out.append(row)
    (ROOT / 'signals.json').write_text(json.dumps(dict(families=out, examples=examples), indent=1) + '\n')
    tot = collections.Counter()
    for r in out:
        tot.update(r['categories'])
        print(r['session'], r['runtime'], r['prompts'], r['categories'], r.get('redo', ''),
              r.get('parent_model_calls', ''), sum((r.get('orchestration_calls') or {}).values()) or '')
    print('TOTAL', dict(tot), 'families with continue_no_pause:',
          sum(1 for r in out if r['categories'].get('continue_no_pause')), 'of', len(out))


if __name__ == '__main__':
    main()
