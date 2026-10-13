"""Price-ratio-weighted usage from summary.json and polling.json. Post-hoc; weights are assumptions.

Units are "new-input-token equivalents". Claude: cache read 0.1x, cache write 1.25x,
output 5x (Anthropic's published ratios). Codex: cached input 0.1x, output 8x (assumed).
Neither is verified for these model versions or for plan-based usage limits.
Replaces the inline computation that first produced weighted.log.
"""
import collections
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
S = json.loads((ROOT / 'summary.json').read_text())
P = json.loads((ROOT / 'polling.json').read_text())
DOMINANT = '1ef22ddd'


def weigh(rt, t, cache_read=0.1):
    """Return (uncached_in, cached_in, output) weights for one token record."""
    if not t:
        return (0.0, 0.0, 0.0)
    if rt == 'claude':
        return (t.get('input_tokens', 0) + 1.25 * t.get('cache_creation_input_tokens', 0),
                cache_read * t.get('cache_read_input_tokens', 0), 5.0 * t.get('output_tokens', 0))
    cached = t.get('cached_input_tokens', 0)
    return (t.get('input_tokens', 0) - cached, cache_read * cached, 8.0 * t.get('output_tokens', 0))


def main_model(models):
    return max(models, key=models.get) if models else ''


def totals(families, cache_read=0.1):
    g = collections.defaultdict(lambda: [0.0, 0.0, 0.0])
    for f in families:
        rt = f['runtime']
        for k, v in zip(range(3), weigh(rt, f['tokens'], cache_read)):
            g['parent'][k] += v
        for h in f['helpers']:
            kind = h.get('kind', 'agent')
            label = 'guardian' if kind == 'guardian' else ('luna' if 'luna' in main_model(h.get('models') or {}) else 'other helper')
            for k, v in zip(range(3), weigh(rt, h['tokens'], cache_read)):
                g[label][k] += v
    return g


def report(name, families):
    g = totals(families)
    all_w = sum(sum(v) for v in g.values())
    comp = [sum(v[i] for v in g.values()) / all_w for i in range(3)]
    helpers = sum(sum(v) for k, v in g.items() if k != 'parent') / all_w
    parts = ', '.join(f"{k} {sum(v) / all_w:.0%}" for k, v in sorted(g.items()))
    print(f"{name}: {all_w / 1e6:.0f}M units; helpers {helpers:.0%} ({parts}); components: "
          f"uncached_in {comp[0]:.0%}, cached_in {comp[1]:.0%}, output {comp[2]:.0%}")
    sens = []
    for r in (0.05, 0.1, 0.25):
        gs = totals(families, r)
        a = sum(sum(v) for v in gs.values())
        sens.append(f"{r}x -> {sum(v[1] for v in gs.values()) / a:.0%}")
    print(f"   cached share by cache-read ratio: {'; '.join(sens)}")
    return all_w, g


def polling_weight(group):
    t = P[group]['polling_tokens']
    return sum(weigh('claude', t))


out = {}
for rt in ('claude', 'codex'):
    fams = [f for f in S['families'] if f['runtime'] == rt]
    w, g = report(rt, fams)
    out[rt] = dict(units=w, by_part={k: sum(v) for k, v in g.items()},
                   components=[sum(v[i] for v in g.values()) for i in range(3)])
    if rt == 'claude':
        pw = polling_weight('helper') + polling_weight('parent')
        print(f"   polling responses (parent + helper) weight {pw / 1e6:.0f}M = {pw / w:.0%} of Claude weight")
        out[rt]['polling_units'] = pw
        rest = [f for f in fams if f['session'][:8] != DOMINANT]
        w2, _ = report(f'claude without {DOMINANT}', rest)
        pw2 = polling_weight(f'helper without {DOMINANT}') + polling_weight(f'parent without {DOMINANT}')
        print(f"   polling without {DOMINANT}: {pw2 / 1e6:.0f}M = {pw2 / w2:.0%} of that weight")
        print(f"   {DOMINANT} carries {(w - w2) / w:.0%} of Claude weight")
        out['claude_without_dominant'] = dict(units=w2, polling_units=pw2)
(ROOT / 'weighted.json').write_text(json.dumps(out, indent=1) + '\n')
