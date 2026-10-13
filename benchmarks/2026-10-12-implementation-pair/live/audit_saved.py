"""Deterministic saved-evidence extraction; independent review decides acceptance."""
import collections
import hashlib
import json
from pathlib import Path
import sys

base = Path(__file__).resolve().parents[1]
arm = sys.argv[1]
out = base / 'prepared-final' / arm
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
def events(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
def save(name, value):
    (base/'live'/f'{arm}-{name}.json').write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')

manifest = read(out/'manifest.json')
usage = read(out/'usage.json')
keys = ('input_tokens','output_tokens','cache_read_input_tokens','cache_creation_input_tokens')
cli_keys = dict(zip(keys, ('inputTokens','outputTokens','cacheReadInputTokens','cacheCreationInputTokens')))
rows, errors = [], []
thread_totals = {}
model_totals = collections.defaultdict(lambda: dict.fromkeys(keys,0))
for path in sorted((out/'native').glob('*.jsonl')):
    by_id = {}
    for event in events(path):
        if event.get('type') != 'assistant' or event.get('parent_tool_use_id'):
            continue
        m = event.get('message',{})
        if not isinstance(m,dict) or not isinstance(m.get('id'),str) or not m['id']:
            errors.append('missing message ID: '+path.name)
            continue
        by_id.setdefault(m['id'],[]).append(m)
    totals = dict.fromkeys(keys,0)
    for ident, messages in by_id.items():
        final = messages[-1]
        counts = final.get('usage',{})
        if not all(type(counts.get(k)) is int and counts[k]>=0 for k in keys):
            errors.append('missing final usage: '+ident)
            continue
        model = final.get('model')
        variants=[]
        for m in messages:
            v=m.get('usage',{})
            compact={k:v.get(k) for k in keys}
            if compact not in variants: variants.append(compact)
        # Known native fragments repeat the same response ID; input counters stay
        # fixed and the final output count grows. Retain every variant for review.
        if any(m.get('model')!=model for m in messages):errors.append('model conflict: '+ident)
        if any(v.get(k)!=counts[k] for v in variants for k in keys if k!='output_tokens'):
            errors.append('input counter conflict: '+ident)
        output_counts=[v.get('output_tokens') for v in variants]
        if any(type(v) is not int for v in output_counts) or output_counts!=sorted(output_counts):
            errors.append('unsupported output counter fragments: '+ident)
        rows.append({'thread_file':path.name,'message_id':ident,'model':model,
                     'record_count':len(messages),'usage_variants':variants,'final_usage':{k:counts[k] for k in keys}})
        for k in keys:totals[k]+=counts[k];model_totals[model][k]+=counts[k]
    thread_totals[path.name]=totals
terminal = usage.get('provider_result_model_usage') or {}
comparisons={}
for model, totals in model_totals.items():
    target=terminal.get(model,{})
    comparisons[model]={k:{'owned_sum':totals[k],'terminal':target.get(cli_keys[k]),
                          'matches':totals[k]==target.get(cli_keys[k])} for k in keys}
if set(model_totals)!=set(terminal):errors.append('model inventories differ')
if any(not v['matches'] for comp in comparisons.values() for v in comp.values()):errors.append('token reconciliation mismatch')
save('accounting',{'method':'Latest native assistant usage per stable message ID within owned thread; child stream echoes excluded. Input counters checked stable and output variants retained. Exact four-category terminal reconciliation is required, independently reviewed.','rows':rows,'thread_totals':thread_totals,'model_totals':dict(model_totals),'terminal_model_usage':terminal,'comparisons':comparisons,'extraction_errors':errors,'reconciles_exactly':not errors,'family_reported_usd':usage.get('provider_reported_cost_usd'),'cost_scope':'Native family estimate including same-model reviewer; coordinator/external assessment and billing unknown.'})

stream=events(out/'trace.jsonl')
tools=[]
for index,event in enumerate(stream):
    m=event.get('message',{});m=m if isinstance(m,dict) else {}
    for block in m.get('content',[]) or []:
        if isinstance(block,dict) and block.get('type') in ('tool_use','tool_result'):
            tools.append({'event_index':index,'event_type':event.get('type'),
                          'parent_tool_use_id':event.get('parent_tool_use_id'),'block':block})
save('tools',tools)
workspace=out/'workspace'
after={str(p.relative_to(workspace)):sha(p) for p in workspace.rglob('*') if p.is_file()}
before=manifest['before']
changed=[name for name in before if after.get(name)!=before[name]]
new=[name for name in after if name not in before]
forbidden=[name for name in changed if name not in manifest['writable_paths']]+[name for name in new if not name.startswith('receipts/')]
receipt=read(workspace/'receipts/review-input.json')
digests=receipt.get('sha256',receipt)
binding={name:{'recorded':digest,'actual':after.get(name),'matches':after.get(name)==digest} for name,digest in digests.items()}
required=set(manifest['writable_paths'])|{'receipts/public.log'}
review_calls=[t for t in tools if t['block'].get('type')=='tool_use' and t['block'].get('name') in ('Agent','Task') and not t['parent_tool_use_id']]
review_indices=[t['event_index'] for t in review_calls if t['block'].get('input',{}).get('subagent_type')=='scientific_reviewer']
mutating_after=[t for t in tools if review_indices and t['event_index']>min(review_indices) and not t['parent_tool_use_id'] and t['block'].get('type')=='tool_use' and t['block'].get('name') in ('Write','Edit','Bash')]
children=read(out/'children.json')
child_summary=[]
for c in children:
    ev=c['events'];texts=[];reads=[];models=[]
    for e in ev:
        m=e.get('message',{});m=m if isinstance(m,dict) else {}
        if e.get('type')=='assistant':
            if m.get('model'):models.append(m['model'])
            for b in m.get('content',[]) or []:
                if b.get('type')=='text':texts.append(b.get('text'))
                if b.get('type')=='tool_use':reads.append({'name':b.get('name'),'input':b.get('input')})
    child_summary.append({**{k:v for k,v in c.items() if k!='events'},'models':sorted(set(models)),'tools':reads,'responses':texts})
save('evidence',{'changed_existing':changed,'new_files':new,'forbidden_workspace_changes':forbidden,
                 'review_hash_binding':binding,'review_hash_covers_required':required<=set(binding),
                 'review_dispatch_indices':review_indices,'mutating_or_check_calls_after_review':mutating_after,
                 'children':child_summary,'oracle_checks':read(out/'oracle.json'),
                 'terminal_sha256':sha(out/'terminal.json'),'terminal_checks':read(out/'terminal.json')['terminal_checks'],
                 'public_log_sha256':sha(workspace/'receipts/public.log'),
                 'public_exit':read(workspace/'receipts/public-exit.json'),
                 'acceptance_decision':'not evaluated; independent raw-evidence review required'})
print(json.dumps({'arm':arm,'accounting_extraction_errors':errors,'thread_totals':thread_totals,
                  'forbidden_changes':forbidden,'post_review_mutating_or_check_calls':len(mutating_after),
                  'hidden_passed':sum(read(out/'oracle.json').values()),'hidden_total':len(read(out/'oracle.json'))},indent=2))
