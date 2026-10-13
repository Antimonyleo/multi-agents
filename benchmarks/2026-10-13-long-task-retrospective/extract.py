"""Read-only long-session retrospective; see PLAN.md. No model calls.

Usage:
  python extract.py freeze [--force]   # select sessions and write sample.json (refuses to overwrite)
  python extract.py extract            # verify frozen prefixes, write summary.json and prompt context;
                                       # writes labels.csv only while it holds no labels

Revision 2 (2026-10-13 review): Codex token counters summed across resets, repeated
token_count events dropped, exec-cell `wait` separated from agent orchestration,
redo window opened at helper return, more automated prompts filtered.
"""
import collections
import csv
import datetime
import glob
import hashlib
import json
import os
import re
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HOME = Path(os.path.expanduser('~'))
CLAUDE_PROJECTS = HOME / '.claude/projects'
CODEX_SESSIONS = HOME / '.codex/sessions'
CLAUDE_DIRS = ('-home-hao-githubrepo-sequence-design', '-home-hao-folding-origamifolder7',
               '-home-hao-folding-origamifolder7-kinetic', '-home-hao-AI-codex-direc')
CODEX_CWDS = ('/home/hao/githubrepo/sequence_design', '/home/hao/folding/origamifolder7',
              '/home/hao/AI/codex_direc')
MIN_RESPONSES = 100
GAP_CAP_S = 600
REDO_WINDOW = 30
POST_COMPACT_WINDOW = 20

AUTOMATED_PREFIXES = ('<task-notification', '<local-command', '<command-', 'Another Claude session sent',
                      'This session is being continued', '<system-reminder', 'Caveat:', '<user-prompt-submit-hook',
                      '[SYSTEM NOTIFICATION', '/compact')
CODEX_INJECTED = ('<environment_context', '# AGENTS.md', '<user_instructions', '<permissions', '<turn_aborted',
                  '<subagent', '<skill', '<collaboration', '<codex_internal_context', '<user_shell_command')
CORRECTION = re.compile(
    r"^\s*(no\b|nope|stop\b|wait\b|don'?t\b|do not\b|why (did|do|are|is|would)\b|that'?s (wrong|not)|"
    r"not what\b|you (didn'?t|did not|forgot|missed|should)\b|undo\b|revert\b|wrong\b|incorrect\b|"
    r"i (do not|don'?t) (think|believe|agree)|i said\b|again\b)", re.I)
EDIT_TOOLS = ('Edit', 'Write', 'NotebookEdit', 'MultiEdit')
CODEX_ORCH = ('spawn_agent', 'wait_agent', 'followup_task', 'send_message', 'list_agents',
              'interrupt_agent', 'close_agent')
CODEX_EXEC_WAIT = ('wait', 'sleep')  # `wait` takes a cell_id: it waits on an exec cell, not an agent
CODEX_WAIT_ONLY = CODEX_EXEC_WAIT + ('wait_agent', 'list_agents')
LABEL_COLUMNS = ('outcome', 'on_track', 'rework', 'worth_cost', 'stop_wanted', 'helpers_useful', 'notes')
LIVE_WINDOW_S = 6 * 3600
# Repeated commands containing a read-only inspection or wait word (status, logs, processes, GPUs, files)
MONITOR = re.compile(r'\b(sleep|tail|nvidia-smi|squeue|ps|pgrep|wc -l|ls|stat|du|date|write_stdin|cat|head|'
                     r'find|grep|jq|watch|test -[ef])\b')


def sha_prefix(path, length):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        remaining = length
        while remaining:
            chunk = fh.read(min(1 << 20, remaining))
            if not chunk:
                break
            h.update(chunk)
            remaining -= len(chunk)
    return h.hexdigest()


def read_prefix(entry):
    with open(entry['path'], 'rb') as fh:
        data = fh.read(entry['bytes'])
    assert len(data) == entry['bytes'], f"{entry['path']} shrank"
    assert hashlib.sha256(data).hexdigest() == entry['sha256'], f"{entry['path']} prefix changed"
    out = []
    for line in data.split(b'\n'):
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            pass  # incomplete trailing line of a live file
    return out


def ts(record):
    t = record.get('timestamp')
    if not t:
        return None
    try:
        return datetime.datetime.fromisoformat(t.replace('Z', '+00:00'))
    except ValueError:
        return None


def timing(stamps):
    stamps = sorted(s for s in stamps if s)
    if len(stamps) < 2:
        return None, None, None
    gaps = [(b - a).total_seconds() for a, b in zip(stamps, stamps[1:])]
    return ((stamps[-1] - stamps[0]).total_seconds(), sum(min(g, GAP_CAP_S) for g in gaps),
            stamps[0].isoformat())


def freeze_entry(path, runtime, role, **extra):
    size = os.path.getsize(path)
    with open(path, 'rb') as fh:
        data = fh.read(size)
    cut = data.rfind(b'\n') + 1  # complete lines only
    return dict(path=str(path), runtime=runtime, role=role, bytes=cut,
                sha256=hashlib.sha256(data[:cut]).hexdigest(), **extra)


# ---------------------------------------------------------------- Claude

def claude_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list) and content and all(isinstance(c, dict) and c.get('type') == 'text' for c in content):
        return '\n'.join(c.get('text', '') for c in content)
    return None


def claude_responses(records):
    usage = {}
    for r in records:
        if r.get('type') == 'assistant':
            m = r.get('message') or {}
            if m.get('id') and isinstance(m.get('usage'), dict):
                usage[m['id']] = (m.get('model'), m['usage'])
    return usage


def claude_metrics(records, children=()):
    usage = claude_responses(records)
    tok = collections.Counter()
    ctx = []
    models = collections.Counter()
    for model, u in usage.values():
        models[model] += 1
        for k in ('input_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens', 'output_tokens'):
            tok[k] += int(u.get(k) or 0)
        ctx.append(int(u.get('input_tokens') or 0) + int(u.get('cache_creation_input_tokens') or 0)
                   + int(u.get('cache_read_input_tokens') or 0))
    tools = collections.Counter()
    prompts, corrections, interrupts, automated, errors, compactions = [], [], 0, collections.Counter(), 0, 0
    prompt_ctx = []  # (prompt, last assistant text before it, prompt index)
    last_assistant = ''
    calls = []  # (name, input, id); names starting '__' are markers, not tool calls
    for r in records:
        t = r.get('type')
        m = r.get('message') or {}
        if t == 'assistant':
            for c in m.get('content') or []:
                if isinstance(c, dict) and c.get('type') == 'tool_use':
                    tools[c['name']] += 1
                    calls.append((c['name'], c.get('input') or {}, c.get('id')))
                elif isinstance(c, dict) and c.get('type') == 'text' and c.get('text', '').strip():
                    last_assistant = c['text']
        elif t == 'user':
            content = m.get('content')
            if isinstance(content, list):
                for c in content:
                    if isinstance(c, dict) and c.get('type') == 'tool_result':
                        if c.get('is_error'):
                            errors += 1
                        calls.append(('__result__', {}, c.get('tool_use_id')))
            text = claude_text(content)
            if text is None or r.get('isMeta') or r.get('isCompactSummary'):
                if r.get('isCompactSummary'):
                    calls.append(('__compact__', {}, None))
                continue
            if '[Request interrupted by user' in text:
                interrupts += 1
                continue
            stripped = text.lstrip()
            auto = next((p for p in AUTOMATED_PREFIXES if stripped.startswith(p)), None)
            if auto:
                automated[auto] += 1
                if auto == '<task-notification':
                    calls.append(('__notify__', {'text': stripped[:600]}, None))
                continue
            prompt_ctx.append((stripped, last_assistant, len(prompts)))
            prompts.append(stripped)
            if CORRECTION.match(stripped):
                corrections.append(stripped)
        elif t == 'system' and r.get('subtype') == 'compact_boundary':
            compactions += 1
            calls.append(('__compact__', {}, None))

    # Repeated reads and commands, post-compaction rereads, redo after helper.
    last_read, written_since = {}, set()
    unchanged_rereads = post_compact_rereads = 0
    seen_cmd, repeat_cmds = {}, 0
    since_compact = None
    read_paths_ever = set()
    edits = 0
    for name, inp, _ in calls:
        if name == '__compact__':
            since_compact = 0
            continue
        if name.startswith('__'):
            continue
        if since_compact is not None:
            since_compact += 1
        if name in EDIT_TOOLS:
            edits += 1
            p = inp.get('file_path') or inp.get('notebook_path')
            if p:
                written_since.add(p)
        elif name == 'Read':
            p = inp.get('file_path')
            key = (p, inp.get('offset'), inp.get('limit'))
            if since_compact is not None and since_compact <= POST_COMPACT_WINDOW and p in read_paths_ever:
                post_compact_rereads += 1
            if key in last_read and p not in written_since:
                unchanged_rereads += 1
            last_read[key] = True
            written_since.discard(p)
            read_paths_ever.add(p)
        elif name == 'Bash':
            cmd = (inp.get('command') or '').strip()
            if cmd in seen_cmd and seen_cmd[cmd] == edits:
                repeat_cmds += 1
            seen_cmd[cmd] = edits

    background = {cid: bool(inp.get('run_in_background')) for n, inp, cid in calls if n in ('Agent', 'Task')}
    helpers = []
    for child in children:
        crec = child['records']
        cu = claude_responses(crec)
        ctok = collections.Counter()
        cmodels = collections.Counter()
        for model, u in cu.values():
            cmodels[model] += 1
            for k in ('input_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens', 'output_tokens'):
                ctok[k] += int(u.get(k) or 0)
        child_reads = set()
        for r in crec:
            if r.get('type') == 'assistant':
                for c in (r.get('message') or {}).get('content') or []:
                    if isinstance(c, dict) and c.get('type') == 'tool_use' and c.get('name') == 'Read':
                        child_reads.add((c.get('input') or {}).get('file_path'))
        tool_use_id = child['meta'].get('toolUseId')
        agent_id = child.get('agent_id')
        redo, returned = None, helper_return(calls, tool_use_id, agent_id)
        if returned is not None and child_reads:
            window = [c for c in calls[returned + 1:] if not c[0].startswith('__')][:REDO_WINDOW]
            redo = len({inp.get('file_path') for n, inp, _ in window if n == 'Read'} & child_reads)
        span, active, _ = timing([ts(r) for r in crec])
        helpers.append(dict(agent_type=child['meta'].get('agentType'), models=dict(cmodels), tokens=dict(ctok),
                            responses=len(cu), active_s=active, child_files_read=len(child_reads),
                            depth=child['meta'].get('spawnDepth'), background=background.get(tool_use_id),
                            return_located=returned is not None, parent_rereads_of_child_files=redo))

    span, active, start = timing([ts(r) for r in records])
    return dict(start=start, span_s=span, active_s=active, responses=len(usage), models=dict(models),
                tokens=dict(tok), context_max=max(ctx) if ctx else None,
                context_median=statistics.median(ctx) if ctx else None,
                context_mean=statistics.fmean(ctx) if ctx else None,
                context_first10_median=statistics.median(ctx[:10]) if ctx else None,
                responses_over_150k_context=sum(c > 150_000 for c in ctx),
                tool_calls=sum(tools.values()), tools=dict(tools.most_common(15)), tool_errors=errors,
                compactions=compactions, user_prompts=len(prompts), correction_candidates=len(corrections),
                interrupts=interrupts, automated_wakeups=dict(automated),
                unchanged_rereads=unchanged_rereads, post_compaction_rereads=post_compact_rereads,
                repeated_commands_no_edit=repeat_cmds, edits=edits, helpers=helpers,
                last_record=last_stamp(records), _prompts=prompts, _corrections=corrections, _prompt_ctx=prompt_ctx)


def last_stamp(records):
    last = max((t for t in (ts(r) for r in records) if t), default=None)
    return last.isoformat() if last else None


def helper_return(calls, tool_use_id, agent_id):
    """Index in `calls` where a helper's result reached the parent, or None.

    A foreground helper returns with its tool_result. A background helper's tool_result
    only acknowledges the launch; it returns with the task notification naming its
    tool-use ID or agent ID. Depth-2 helpers were launched by another helper, so their
    parent call is not in this transcript.
    """
    launched = next((i for i, (n, _, cid) in enumerate(calls) if cid == tool_use_id and not n.startswith('__')), None)
    if launched is None:
        return None
    if not calls[launched][1].get('run_in_background'):
        return next((i for i in range(launched + 1, len(calls))
                     if calls[i][0] == '__result__' and calls[i][2] == tool_use_id), None)
    keys = [k for k in (tool_use_id, agent_id) if k]
    return next((i for i in range(launched + 1, len(calls)) if calls[i][0] == '__notify__'
                 and any(k in calls[i][1]['text'] for k in keys)), None)


# ---------------------------------------------------------------- Codex

def codex_meta(path):
    with open(path) as fh:
        first = json.loads(fh.readline())
    return first.get('payload', {})


def codex_metrics(records):
    """Codex session metrics.

    The cumulative token counter can drop mid-file (a new segment starts near zero), so the
    total is the sum of each segment's final value. A token_count event that repeats the
    previous cumulative value is not a new model call. Tool calls since the previous model
    call belong to the next one, which gives per-call tool sets for wait-only responses.
    """
    seg_totals, cur_total, prev_key, resets = [], None, None, 0
    ctx, durations = [], []
    tools, orch, exec_waits = collections.Counter(), collections.Counter(), collections.Counter()
    prompts, corrections, models, compactions, aborted = [], [], collections.Counter(), 0, 0
    prompt_ctx, last_assistant = [], ''
    seen_cmd, repeat_cmds, edits, repeat_kinds = {}, 0, 0, collections.Counter()
    pending, wait_only, wait_only_ctx, wait_agent_only = [], 0, 0, 0
    wait_timeouts = collections.Counter()
    for r in records:
        t, p = r.get('type'), r.get('payload') or {}
        if t == 'turn_context' and p.get('model'):
            models[p['model']] += 1
        elif t == 'compacted':
            compactions += 1
        elif t == 'event_msg':
            et = p.get('type')
            if et == 'token_count' and p.get('info'):
                info = p['info']
                tot = info.get('total_token_usage')
                key = json.dumps(tot, sort_keys=True) if tot else None
                if key is not None and key == prev_key:
                    continue  # repeated event, not a new model call
                prev_key = key
                if tot:
                    if cur_total and int(tot.get('total_tokens') or 0) < int(cur_total.get('total_tokens') or 0):
                        seg_totals.append(cur_total)
                        resets += 1
                    cur_total = tot
                if info.get('last_token_usage'):
                    c = int(info['last_token_usage'].get('input_tokens') or 0)
                    ctx.append(c)
                    if pending and all(n in CODEX_WAIT_ONLY for n in pending):
                        wait_only += 1
                        wait_only_ctx += c
                        wait_agent_only += all(n == 'wait_agent' for n in pending)
                pending = []
            elif et == 'task_complete' and p.get('duration_ms'):
                durations.append(p['duration_ms'] / 1000)
            elif et == 'turn_aborted':
                aborted += 1
        elif t == 'response_item':
            pt = p.get('type')
            if pt in ('function_call', 'custom_tool_call'):
                name = p.get('name')
                tools[name] += 1
                pending.append(name)
                if name in CODEX_ORCH:
                    orch[name] += 1
                    if name == 'wait_agent':
                        try:
                            ms = json.loads(p.get('arguments') or '{}').get('timeout_ms')
                        except (json.JSONDecodeError, AttributeError):
                            ms = None
                        wait_timeouts['unknown' if not isinstance(ms, (int, float)) else '<=60s' if ms <= 60_000
                                      else '<=5min' if ms <= 300_000 else '>5min'] += 1
                elif name in CODEX_EXEC_WAIT:
                    exec_waits[name] += 1
                arg = str(p.get('arguments', p.get('input', '')))
                if 'apply_patch' in arg or name == 'apply_patch':
                    edits += 1
                elif name in ('exec', 'shell', 'exec_command'):
                    key = arg.strip()
                    if key in seen_cmd and seen_cmd[key] == edits:
                        repeat_cmds += 1
                        repeat_kinds['inspect_or_wait' if MONITOR.search(key) else 'other'] += 1
                    seen_cmd[key] = edits
            elif pt == 'message' and p.get('role') == 'assistant':
                text = '\n'.join(c.get('text', '') for c in p.get('content') or [] if isinstance(c, dict))
                if text.strip():
                    last_assistant = text
            elif pt == 'message' and p.get('role') == 'user':
                text = '\n'.join(c.get('text', '') for c in p.get('content') or [] if isinstance(c, dict))
                s = text.lstrip()
                if not s or s.startswith(CODEX_INJECTED):
                    continue
                prompt_ctx.append((s, last_assistant, len(prompts)))
                prompts.append(s)
                if CORRECTION.match(s):
                    corrections.append(s)
    totals = seg_totals + ([cur_total] if cur_total else [])
    tokens = None
    if totals:
        tokens = collections.Counter()
        for tot in totals:
            tokens.update({k: int(v or 0) for k, v in tot.items() if isinstance(v, (int, float))})
        tokens = dict(tokens)
    span, active, start = timing([ts(r) for r in records])
    return dict(start=start, span_s=span, active_s=active, responses=len(ctx), models=dict(models),
                tokens=tokens, counter_resets=resets, context_max=max(ctx) if ctx else None,
                context_median=statistics.median(ctx) if ctx else None,
                context_mean=statistics.fmean(ctx) if ctx else None,
                context_first10_median=statistics.median(ctx[:10]) if ctx else None,
                responses_over_150k_context=sum(c > 150_000 for c in ctx),
                tool_calls=sum(tools.values()), tools=dict(tools.most_common(15)), orchestration_calls=dict(orch),
                exec_waits=dict(exec_waits), wait_only_responses=wait_only, wait_only_input_tokens=wait_only_ctx,
                wait_agent_only_responses=wait_agent_only, wait_agent_timeouts=dict(wait_timeouts),
                compactions=compactions, user_prompts=len(prompts), correction_candidates=len(corrections),
                interrupts=aborted, turn_durations_s=sum(durations) if durations else None,
                repeated_commands_no_edit=repeat_cmds, repeated_command_kinds=dict(repeat_kinds), edits=edits,
                last_record=last_stamp(records), _prompts=prompts, _corrections=corrections, _prompt_ctx=prompt_ctx)


# ---------------------------------------------------------------- freeze / extract

def safe_records(path):
    with open(path) as fh:
        for line in fh:
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                pass


def freeze():
    if (ROOT / 'sample.json').exists() and '--force' not in sys.argv:
        sys.exit('sample.json exists; it is the frozen sample. Use --force only to start a new study.')
    entries = []
    for d in CLAUDE_DIRS:
        for f in sorted((CLAUDE_PROJECTS / d).glob('*.jsonl')):
            n = len(claude_responses(safe_records(f)))
            if n < MIN_RESPONSES:
                continue
            parent = freeze_entry(f, 'claude', 'parent', project=d, responses_at_freeze=n)
            entries.append(parent)
            for c in sorted((f.parent / f.stem / 'subagents').glob('*.jsonl')):
                meta = c.with_suffix('.meta.json')
                entries.append(freeze_entry(c, 'claude', 'child', parent=str(f),
                                            meta=json.loads(meta.read_text()) if meta.exists() else {}))
    files = sorted(glob.glob(str(CODEX_SESSIONS / '**/*.jsonl'), recursive=True))
    metas = {f: codex_meta(f) for f in files}
    by_parent = collections.defaultdict(list)
    for f, m in metas.items():
        if m.get('parent_thread_id'):
            by_parent[m['parent_thread_id']].append(f)
    for f, m in metas.items():
        if m.get('source') not in ('cli', 'vscode', 'exec') or m.get('cwd') not in CODEX_CWDS:
            continue
        n = 0
        with open(f) as fh:
            for line in fh:
                if '"token_count"' in line and '"info":{' in line.replace(' ', ''):
                    n += 1
        if n < MIN_RESPONSES:
            continue
        entries.append(freeze_entry(f, 'codex', 'parent', project=m['cwd'], responses_at_freeze=n))
        stack, seen = [m.get('id')], set()
        while stack:
            pid = stack.pop()
            for c in by_parent.get(pid, []):
                if c in seen or c == f:
                    continue
                seen.add(c)
                cm = metas[c]
                src = cm.get('source')
                kind = 'guardian' if cm.get('thread_source') == 'guardian_review' else 'spawn'
                sp = (src or {}).get('subagent', {}).get('thread_spawn', {}) if isinstance(src, dict) else {}
                entries.append(freeze_entry(c, 'codex', 'child', parent=f, kind=kind,
                                            meta=dict(agent_role=sp.get('agent_role'), depth=sp.get('depth'),
                                                      history_mode=cm.get('history_mode'),
                                                      forked=bool(cm.get('forked_from_id')))))
                stack.append(cm.get('id'))
    sample = dict(frozen_at=datetime.datetime.now(datetime.timezone.utc).isoformat(), plan='PLAN.md',
                  rule=dict(min_responses=MIN_RESPONSES, claude_dirs=CLAUDE_DIRS, codex_cwds=CODEX_CWDS),
                  entries=entries)
    (ROOT / 'sample.json').write_text(json.dumps(sample, indent=1) + '\n')
    roles = collections.Counter((e['runtime'], e['role']) for e in entries)
    print('frozen', dict(roles))


def excerpt(s, n=150):
    s = ' '.join(s.split())
    return s[:n] + ('…' if len(s) > n else '')


def extract():
    sample = json.loads((ROOT / 'sample.json').read_text())
    children = collections.defaultdict(list)
    for e in sample['entries']:
        if e['role'] == 'child':
            children[e['parent']].append(e)
    frozen_at = datetime.datetime.fromisoformat(sample['frozen_at'])
    families, labels, correction_samples, prompt_context = [], [], [], {}
    for e in sample['entries']:
        if e['role'] != 'parent':
            continue
        records = read_prefix(e)
        if e['runtime'] == 'claude':
            kids = [dict(records=read_prefix(c), meta=c.get('meta', {}),
                         agent_id=Path(c['path']).stem.removeprefix('agent-')) for c in children[e['path']]]
            m = claude_metrics(records, kids)
        else:
            m = codex_metrics(records)
            helpers = []
            for c in children[e['path']]:
                cm = codex_metrics(read_prefix(c))
                helpers.append(dict(kind=c['kind'], agent_role=c['meta'].get('agent_role'),
                                    depth=c['meta'].get('depth'), forked=c['meta'].get('forked'),
                                    models=cm['models'], tokens=cm['tokens'], counter_resets=cm['counter_resets'],
                                    responses=cm['responses'], active_s=cm['active_s'],
                                    context_first10_median=cm['context_first10_median'],
                                    orchestration_calls=cm['orchestration_calls']))
            m['helpers'] = helpers
        sid = Path(e['path']).stem[-36:]
        prompts, corr, pctx = m.pop('_prompts'), m.pop('_corrections'), m.pop('_prompt_ctx')
        prompt_context[sid[:8]] = [dict(i=i, prompt=p[:2000], before=excerpt(a, 400)) for p, a, i in pctx]
        correction_samples += [dict(session=sid, text=excerpt(c, 120)) for c in corr]
        last = datetime.datetime.fromisoformat(m['last_record']) if m['last_record'] else None
        m['live_at_freeze'] = bool(last and (frozen_at - last).total_seconds() < LIVE_WINDOW_S)
        families.append(dict(session=sid, runtime=e['runtime'], project=e['project'], path=e['path'], **m))
        longest = sorted(prompts, key=len, reverse=True)[:3]
        labels.append(dict(session=sid[:8], runtime=e['runtime'],
                           project=Path(e['project']).name.replace('-home-hao-', ''),
                           start=(m['start'] or '')[:10], active_h=round((m['active_s'] or 0) / 3600, 1),
                           live_at_freeze='yes' if m['live_at_freeze'] else '',
                           prompts=m['user_prompts'], helpers=len(m['helpers']),
                           first_request=excerpt(prompts[0]) if prompts else '',
                           last_request=excerpt(prompts[-1]) if prompts else '',
                           key_requests=' || '.join(excerpt(p, 200) for p in longest),
                           **{k: '' for k in LABEL_COLUMNS}))
    out = dict(sample_frozen_at=sample['frozen_at'],
               extractor_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               families=families,
               limits=['Observational; tasks differ, so no causal or savings claim.',
                       'Codex tokens sum the final cumulative counter of each counter segment; '
                       'compaction calls may still be omitted.',
                       'Correction and repeat counts are heuristic candidates, not proven drift or waste.',
                       'Claude and Codex token categories differ and are not prices.'])
    (ROOT / 'summary.json').write_text(json.dumps(out, indent=1) + '\n')
    (ROOT / 'correction-candidates.json').write_text(json.dumps(correction_samples, indent=1) + '\n')
    # Prompt text with the preceding assistant message, for hand-coding. Local only (see .gitignore).
    (ROOT / 'prompt-context.json').write_text(json.dumps(prompt_context, indent=1) + '\n')
    labels.sort(key=lambda r: r['start'])
    target = ROOT / 'labels.csv'
    if target.exists() and any(r.get(k) for r in csv.DictReader(open(target)) for k in LABEL_COLUMNS):
        target = ROOT / 'labels.generated.csv'
        print('labels.csv holds labels; wrote', target.name, 'instead')
    with open(target, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(labels[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(labels)
    print('families', len(families))


if __name__ == '__main__':
    {'freeze': freeze, 'extract': extract}[sys.argv[1]]()
