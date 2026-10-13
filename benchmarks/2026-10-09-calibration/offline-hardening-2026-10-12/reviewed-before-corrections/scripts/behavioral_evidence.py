"""Bounded transcript decoding. No shell/JavaScript evaluation occurs here.

Statuses: supported (known representation), rejected (known unsafe or contradicted),
unknown (missing, incomplete, or unsupported). Unknown never proves acceptance.
"""
import json
import re
import shlex


def shell_command(tool):
    inp = tool.get('input', {})
    command = inp.get('command', inp.get('cmd', '')) if isinstance(inp, dict) else inp
    if not isinstance(command, str):
        return ''
    try:
        tokens = shlex.split(command)
    except ValueError:
        return ''
    if len(tokens) == 3 and tokens[0] in ('bash', '/bin/bash', 'sh', '/bin/sh') and tokens[1] in ('-c', '-lc'):
        return tokens[2].strip()
    return command.strip()


def _segment(tokens):
    """Return content-read operands separately from digest/listing operands."""
    if not tokens:
        return None
    cmd, args = tokens[0], tokens[1:]
    reads, digests = [], []
    if cmd in ('echo', 'printf'):
        # Pure literal display only; printf -v assigns and %n/escapes are outside scope.
        if cmd == 'printf' and (not args or args[0].startswith('-') or '%n' in args[0]):
            return None
    elif cmd == 'pwd':
        if args:
            return None
    elif cmd in ('cat', 'sha256sum'):
        if not args or any(a.startswith('-') for a in args):
            return None
        if cmd == 'cat':
            reads = args
        else:
            digests = args
    elif cmd == 'sed':
        if len(args) < 3 or args[0] != '-n' or not re.fullmatch(r'\d+(?:,\d+)?p', args[1]) or any(a.startswith('-') for a in args[2:]):
            return None
        reads = args[2:]
    elif cmd in ('head', 'tail'):
        if len(args) >= 2 and args[0] in ('-n', '-c') and re.fullmatch(r'\d+', args[1]):
            reads = args[2:]
        elif args and re.fullmatch(r'-\d+', args[0]):
            reads = args[1:]
        elif args and not args[0].startswith('-'):
            reads = args
        elif args:
            return None
        if any(a.startswith('-') for a in reads):
            return None
    elif cmd == 'wc':
        if args and args[0] in ('-l', '-c', '-w'):
            args = args[1:]
        if any(a.startswith('-') for a in args):
            return None
        # Counts do not establish source-content evidence.
    elif cmd == 'ls':
        if any(a.startswith('-') and a not in ('-l', '-a', '-la', '-al', '-R') for a in args):
            return None
    elif cmd == 'rg':
        # Only listing mode is currently supported; patterns/options are not file reads.
        if '--files' not in args:
            return None
        i = 0
        while i < len(args):
            if args[i] in ('--files', '--hidden'):
                i += 1
            elif args[i] == '-g' and i + 1 < len(args):
                i += 2
            elif not args[i].startswith('-'):
                i += 1
            else:
                return None
    elif cmd == 'find':
        i = 0
        while i < len(args) and not args[i].startswith('-'):
            i += 1
        if i == 0:
            return None
        while i < len(args):
            if args[i] == '-type' and i + 1 < len(args) and args[i + 1] == 'f':
                i += 2
            elif args[i] == '-maxdepth' and i + 1 < len(args) and args[i + 1].isdigit():
                i += 2
            elif args[i:i + 2] == ['-not', '-path'] and i + 2 < len(args):
                i += 3
            else:
                return None
    else:
        return None
    return {'command': cmd, 'reads': reads, 'digests': digests}


def shell_plan(command):
    """Recognize bounded read-only compound commands, including one literal loop.

    Shell substitution/redirection, sed execution and find/rg exec flags are
    rejected. Other interpreter/shell syntax stays unknown, not a claimed write.
    Listing/head pipelines are safe but never establish file-content reads.
    """
    if not isinstance(command, str) or not command.strip():
        return {'status': 'unknown', 'reason': 'missing command', 'reads': []}
    # One exact literal-file loop observed in the diagnostics. Never general expansion.
    loop = re.fullmatch(r'\s*for f in ([^;\n]+); do echo "== \$f"; cat "\$f"; echo; done(?:; (.*))?\s*', command)
    if loop:
        try:
            files = shlex.split(loop[1])
        except ValueError:
            files = []
        if not files or len(files) > 32 or any(not re.fullmatch(r'[\w./-]+', f) or f.startswith('-') for f in files):
            return {'status': 'unknown', 'reason': 'nonliteral loop inputs', 'reads': []}
        suffix = shell_plan(loop[2]) if loop[2] else {'status': 'supported', 'reads': []}
        if suffix['status'] != 'supported':
            return suffix
        return {'status': 'supported', 'reason': 'literal file loop', 'reads': files + suffix['reads'],
                'digests': suffix.get('digests', [])}
    if any(s in command for s in ('>', '<', '`', '$(', '${', '\n')) or '$' in command:
        if "'" in command or '"' in command:
            return {'status': 'unknown', 'reason': 'quoted metacharacters outside bounded grammar', 'reads': []}
        return {'status': 'rejected', 'reason': 'substitution, redirection or escape outside read grammar', 'reads': []}
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=';&|()')
        lexer.whitespace_split = True
        lexer.commenters = ''
        tokens = list(lexer)
    except ValueError:
        return {'status': 'unknown', 'reason': 'invalid shell quoting', 'reads': []}
    segments, separators, current = [], [], []
    for token in tokens:
        if token in (';', '&&', '|'):
            segments.append(current); separators.append(token); current = []
        elif token and set(token) <= set(';&|()'):
            return {'status': 'unknown', 'reason': 'unsupported shell operator', 'reads': []}
        else:
            current.append(token)
    segments.append(current)
    if not segments[-1] and separators and separators[-1] == ';':
        segments.pop(); separators.pop()
    parts = [_segment(t) for t in segments]
    if any(p is None for p in parts):
        bad = next(t for t, p in zip(segments, parts) if p is None)
        unsafe = bad and (bad[0] in ('rm', 'mv', 'cp', 'touch', 'tee', 'truncate')
                         or bad[0] == 'sed' and any('e ' in t or t.startswith('-i') for t in bad[1:])
                         or bad[0] in ('rg', 'find') and any(t.startswith(('--pre', '--hostname-bin', '-exec', '-delete', '-ok')) for t in bad[1:]))
        return {'status': 'rejected' if unsafe else 'unknown', 'reason': 'unrecognized or unsafe command segment', 'reads': []}
    for i, sep in enumerate(separators):
        if sep == '|' and not (parts[i]['command'] in ('find', 'ls', 'rg') and parts[i + 1]['command'] in ('head', 'tail') and not parts[i + 1]['reads']):
            return {'status': 'unknown', 'reason': 'unsupported pipeline', 'reads': []}
    return {'status': 'supported', 'reason': 'bounded read/display grammar',
            'reads': [p for part in parts for p in part['reads']],
            'digests': [p for part in parts for p in part['digests']]}


def result_texts(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for child in value:
            yield from result_texts(child)
    elif isinstance(value, dict):
        for key, child in value.items():
            if key in ('content', 'text', 'output', 'stdout', 'stderr', 'file', 'native'):
                yield from result_texts(child)


def terminal_result(result):
    """Require consistent explicit exit evidence; literal 'OK' cannot supply it."""
    if not isinstance(result, dict):
        return {'status': 'unknown', 'reason': 'missing correlated result', 'exit_code': None}
    codes = []
    for value in (result, result.get('native', {})):
        if not isinstance(value, dict):
            continue
        if 'exit_code' in value:
            if type(value['exit_code']) is not int:
                return {'status': 'unknown', 'reason': 'invalid exit representation', 'exit_code': None}
            codes.append(value['exit_code'])
    texts = list(result_texts(result))
    # Canonical exec envelope footer; not arbitrary mentions in program output.
    for text in texts:
        match = re.fullmatch(r'(?:Chunk ID: [^\n]+\n)?Wall time: [^\n]+\nProcess exited with code (-?\d+)\n(?:Final output:|Output:)\n[\s\S]*', text)
        if match:
            codes.append(int(match[1]))
    if len(set(codes)) > 1 or result.get('is_error') is True and codes and codes[0] == 0:
        return {'status': 'unknown', 'reason': 'conflicting terminal result', 'exit_code': None}
    if not codes:
        return {'status': 'unknown', 'reason': 'no verified exit code', 'exit_code': None}
    code = codes[0]
    return {'status': 'supported', 'reason': 'consistent terminal exit', 'exit_code': code}


def read_completed(result):
    if not isinstance(result, dict) or result.get('is_error') is True:
        return False
    terminal = terminal_result(result)
    if terminal['reason'] == 'conflicting terminal result' or terminal['status'] == 'supported' and terminal['exit_code'] != 0:
        return False
    native = result.get('native', {})
    if isinstance(native, dict) and (native.get('interrupted') is True or native.get('stderr') and not native.get('stdout')):
        return False
    text = '\n'.join(result_texts(result))
    return bool(text.strip()) and not any(s in text.lower() for s in ('no such file or directory', 'permission denied', 'error reading file'))


# Object grammar accepts JSON string cmd and bounded scalar options only.
_OBJECT = r'\{\s*(?:(?:cmd|"cmd")\s*:\s*"(?:\\.|[^"\\])*"|(?:[a-z_]+|"[a-z_]+")\s*:\s*(?:"(?:\\.|[^"\\])*"|\d+|true|false))(?:\s*,\s*(?:[a-z_]+|"[a-z_]+")\s*:\s*(?:"(?:\\.|[^"\\])*"|\d+|true|false))*\s*\}'
_CALL = r'tools\.exec_command\(\s*(' + _OBJECT + r')\s*\)'
_CALL_RE = re.compile(_CALL)


def literal_exec(raw):
    """Decode two fully matched wrappers without evaluating JavaScript."""
    if not isinstance(raw, str):
        return None
    body = re.sub(r'^// @exec: [^\n]*\n', '', raw).strip()
    single = re.fullmatch(r'text\(\s*await\s+' + _CALL + r'\s*\)\s*;?', body)
    many = re.fullmatch(r'const (\w+)\s*=\s*await Promise\.allSettled\(\s*\[([\s\S]*)\]\s*\)\s*;\s*\1\.forEach\(text\)\s*;?', body)
    if single:
        objects = [single[1]]
    elif many:
        middle = many[2]
        objects, pos = [], 0
        while pos < len(middle):
            match = _CALL_RE.match(middle, pos + len(middle[pos:]) - len(middle[pos:].lstrip()))
            if not match:
                return None
            objects.append(match[1]); pos = match.end()
            rest = middle[pos:].lstrip()
            if not rest:
                break
            if not rest.startswith(','):
                return None
            pos = len(middle) - len(rest) + 1
        if not objects or len(objects) > 16:
            return None
    else:
        return None
    values = []
    for obj in objects:
        # Quote object keys only outside string tokens (no regexp rewriting strings).
        tokens = re.findall(r'"(?:\\.|[^"\\])*"|[a-z_]+|\d+|[{}:,]', obj)
        converted = ''.join(json.dumps(t) if re.fullmatch(r'[a-z_]+', t) and t not in ('true', 'false') else t for t in tokens)
        try:
            value = json.loads(converted)
        except ValueError:
            return None
        if (not isinstance(value.get('cmd'), str) or set(value) - {'cmd', 'max_output_tokens', 'yield_time_ms', 'workdir', 'login', 'tty', 'sandbox_permissions'}):
            return None
        values.append(value)
    return values


def _outputs(raw):
    values = []
    blocks = raw if isinstance(raw, list) else [{'text': raw}]
    for block in blocks:
        if not isinstance(block, dict) or block.get('type', 'text') not in ('text', 'input_text'):
            continue
        try:
            value = json.loads(block.get('text', ''))
        except (ValueError, TypeError):
            continue
        if isinstance(value, dict) and value.get('status') == 'fulfilled':
            value = value.get('value')
        # Rejected allSettled results must occupy their original position.
        if isinstance(value, dict):
            values.append(value)
    return values


def native_tools(trace, actor='main'):
    """Preserve every owned tool call, including unresolved/unsupported execution."""
    calls, replies, issues = {}, {}, []
    for event in trace:
        if not isinstance(event, dict) or event.get('type') != 'response_item':
            continue
        value = event.get('payload', {})
        if not isinstance(value, dict):
            issues.append('unsupported owned payload'); continue
        kind, ident = value.get('type'), value.get('call_id')
        if kind in ('custom_tool_call', 'function_call'):
            if not isinstance(ident, str) or not ident:
                issues.append('missing owned call identity'); continue
            if ident in calls and calls[ident] != value:
                issues.append('conflicting owned call: ' + ident)
            calls[ident] = value
        elif kind in ('custom_tool_call_output', 'function_call_output'):
            if not isinstance(ident, str) or not ident:
                issues.append('missing owned result identity'); continue
            if ident in replies and replies[ident] != value.get('output'):
                issues.append('conflicting owned output: ' + ident)
            replies[ident] = value.get('output')
    tools = []
    for ident, value in calls.items():
        name, arguments = value.get('name'), None
        raw = value.get('input', value.get('arguments', ''))
        if name in ('exec', 'functions.exec'):
            arguments = literal_exec(raw)
        elif value.get('type') == 'function_call':
            try:
                arg = json.loads(raw)
                if isinstance(arg, dict):
                    arguments = [arg]
            except (ValueError, TypeError):
                pass
        outputs = _outputs(replies.get(ident))
        if arguments is None:
            issues.append('unsupported owned call: ' + ident)
            tools.append({'id': ident, 'name': 'UnsupportedNative', 'input': {'raw': raw}, 'actor': actor, 'result': None})
            continue
        if len(outputs) != len(arguments):
            issues.append('missing/ambiguous owned output: ' + ident)
        for n, arg in enumerate(arguments):
            result = outputs[n] if len(outputs) == len(arguments) else None
            execution = name in ('exec', 'functions.exec', 'exec_command', 'functions.exec_command')
            tool = {'id': ident if len(arguments) == 1 else ident + ':' + str(n),
                    'parent_call_id': ident, 'name': 'exec_command' if execution else name,
                    'input': arg, 'actor': actor, 'result': result, 'source': 'owned_native'}
            if execution and terminal_result(result)['status'] != 'supported':
                issues.append('unresolved owned execution: ' + tool['id'])
            tools.append(tool)
    for ident in set(replies) - set(calls):
        issues.append('orphan owned output: ' + ident)
    return tools, issues
