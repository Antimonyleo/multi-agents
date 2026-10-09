#!/usr/bin/env python3
"""Benchmark harness for the scientific-workflow skill. See protocol.md (frozen before runs).

    bench.py build --out DIR      build fixtures W and B and the ground-truth files
    bench.py selftest --out DIR   check the scorers on good and bad synthetic answers
    bench.py run --out DIR        run all scored runs (resumable), then write summary
    bench.py summarize --out DIR  recompute the summary from stored runs
"""
import argparse, collections, concurrent.futures as cf, hashlib, json, os, pathlib, re
import shutil, statistics, subprocess, sys, time

HERE = pathlib.Path(__file__).resolve().parent
REPO = pathlib.Path("/home/hao/folding/origamifolder7")
AGENTS = ["scientific_explorer", "scientific_researcher", "scientific_worker",
          "scientific_analyst", "scientific_reviewer"]
TOOLS = "Read,Grep,Glob,Bash,Edit,Write,Agent,Skill"
TIMEOUT_S = 1500
PLAN = [("T1", 3, 0.8), ("T2", 3, 1.5), ("T3", 2, 3.0)]  # task, repeats, USD cap per run

PROMPTS = {
    "T1": ("What are the default values of --trap-stiffness and --max-force in "
           "scripts/run_design_controller.py? Answer in one line in the form: "
           "trap-stiffness=<value>, max-force=<value>"),
    "T2": ("List every Python file under scripts/ (recursive) that defines a module-level "
           "function named main. For each file give the first line of its module docstring, "
           "or the word none if it has no docstring. Reply with one line per file in the form "
           "`<path relative to the working directory> | <first docstring line>`, sorted by "
           "path, and nothing else."),
    "T3": ("I will use your answer to decide whether a full MD campaign can start, so treat "
           "this as a pre-launch check. Audit whether the CLI defaults in "
           "scripts/run_design_controller.py match the defaults of the ControllerConfig fields "
           "in origami_folding/controller.py. For every CLI option that feeds a "
           "ControllerConfig field directly, report the option, the CLI default, the config "
           "default, and whether they match. Treat fields that are computed from other "
           "arguments separately, and say what each resolves to when the option is omitted. "
           "Write the full table to audit.md in the working directory. Do not create or edit "
           "any other file, and do not run anything that takes longer than a minute. In your "
           "reply, give a short summary, say explicitly what you did not verify, and end with "
           "one line in the form `MISMATCHES: --option-one, --option-two` listing the CLI "
           "options whose defaults do not match (or `MISMATCHES: none`)."),
}

PROMPTS["T3b"] = PROMPTS["T3"]
PROMPTS["T5"] = ("I made the uncommitted changes shown by `git diff` in this repository. We will "
                 "start a full MD campaign from this code next. Review the change set before launch. "
                 "Reply with a short summary, then end with one line starting with `FINDINGS:` "
                 "followed by a JSON array in which each item is {\"file\": ..., \"symbol\": ..., "
                 "\"severity\": \"blocking\" or \"minor\", \"why\": ...}. Mark as blocking only issues "
                 "that should stop the launch and that you can support from the code. Do not modify any file.")
PREFIX_X = "Use the scientific-workflow skill. "
PREFIX_R = ("Use the scientific-workflow skill. Have the scientific_reviewer agent review the change set. "
            "Then give me the result in the format below. ")
PROMPTS["T5v3"] = PROMPTS["T5"].replace(
    "Do not modify any file.",
    "Do not modify any tracked file; you may write scratch files named review_*.patch or review_*.md in the working directory.")
PLAN3 = [("T5v3", 5, 3.0)]
PLAN4 = [("T1", 3, 1.5), ("T2", 3, 3.0), ("T3b", 3, 4.0), ("T5v3", 3, 4.0)]
PLANTED_V3 = {"A": ["nucleation_fraction"], "C": ["reopen_max_attempts", "test_default_config_leaves_reopen_off"]}
NEUTRAL_V3 = ["adaptive_coupled_release", "adaptive coupled release", "adaptive-coupled-release"]
PLAN2 = [("T3b", 3, 3.0), ("T5", 3, 3.0)]
PLANTED = {"A": ["nucleation_fraction"],
           "B": ["adaptive_coupled_release", "adaptive-coupled-release", "adaptive coupled release"],
           "C": ["reopen_max_attempts"]}
V2_REQUIRED = {"--final-hold-steps", "--max-events", "--max-retries", "--relax-max-chunks",
               "--trap-steps", "--temperatures", "--eligibility-mode"}
V2_OPTIONAL = {"--trap-release-steps"}


def sh(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def manifest(root):
    out = {}
    for p in sorted(pathlib.Path(root).rglob("*")):
        if p.is_file() and not ({"__pycache__", ".pytest_cache", ".git"} & set(p.parts)):
            out[str(p.relative_to(root))] = hashlib.sha1(p.read_bytes()).hexdigest()
    return out


# ---------------------------------------------------------------- build
def build(out):
    out = pathlib.Path(out)
    fx = out / "fixtures"
    if fx.exists():
        shutil.rmtree(fx)
    (fx / "B").mkdir(parents=True)
    arch = subprocess.run(["git", "archive", "HEAD"], cwd=REPO, check=True, capture_output=True).stdout
    sh(["tar", "-x", "-C", str(fx / "B")], input=arch)
    shutil.copytree(fx / "B", fx / "W")
    shutil.copy(REPO / "AGENTS.md", fx / "W" / "AGENTS.md")
    shutil.copy(REPO / "docs/agent_guidance/delegation.md", fx / "W" / "docs/agent_guidance/delegation.md")
    for name, script in (("truth_t2.json", "truth_t2.py"), ("truth_t3.json", "truth_t3.py")):
        res = subprocess.run([sys.executable, str(HERE / script), str(fx / "B")],
                             check=True, capture_output=True, text=True)
        (out / name).write_text(res.stdout)
    for arm in "WB":
        (out / f"manifest_{arm}.json").write_text(json.dumps(manifest(fx / arm)))
    t2 = json.loads((out / "truth_t2.json").read_text())
    t3 = json.loads((out / "truth_t3.json").read_text())
    print(f"fixtures built: T2 truth {len(t2)} files; T3 truth {t3['n_direct_args']} direct, "
          f"{len(t3['mismatches'])} mismatches, {len(t3['non_direct'])} indirect")


# ---------------------------------------------------------------- scoring
def norm(s):
    return re.sub(r"\s+", " ", s.strip().strip("`").strip())


def score_t1(text, workdir, out, arm=None):
    ts = re.search(r"trap-stiffness\s*=\s*([0-9.]+)", text)
    mf = re.search(r"max-force\s*=\s*([0-9.]+)", text)
    ok = bool(ts and mf and float(ts.group(1)) == 0.7 and float(mf.group(1)) == 20.0)
    return {"correct": ok}


def score_t2(text, workdir, out, arm=None):
    truth = json.loads((pathlib.Path(out) / "truth_t2.json").read_text())
    got = {}
    for line in text.splitlines():
        line = line.strip().lstrip("-*• ").strip()
        if " | " in line and not line.startswith("```"):
            path, doc = line.split(" | ", 1)
            got[norm(path)] = norm(doc)
    tp = set(got) & set(truth)
    prec = len(tp) / len(got) if got else 0.0
    rec = len(tp) / len(truth)
    exact = sum(norm(got[p]) == norm(truth[p]) for p in tp) / len(tp) if tp else 0.0
    ok = set(got) == set(truth) and exact >= 0.95
    return {"correct": ok, "path_precision": round(prec, 3), "path_recall": round(rec, 3),
            "doc_exact": round(exact, 3), "n_lines": len(got)}


def score_t3(text, workdir, out, arm="W", v2=False):
    out = pathlib.Path(out)
    truth = json.loads((out / "truth_t3.json").read_text())
    true_opts = {r["cli_option"] for r in truth["mismatches"]}
    lines = [l for l in text.splitlines() if re.search(r"MISMATCHES:", l)]
    got = set()
    if lines:
        got = set(re.findall(r"--[a-z0-9][a-z0-9-]*", lines[-1]))
    if v2:
        true_opts = set(V2_REQUIRED)
        allowed = true_opts | V2_OPTIONAL
        rec = len(got & true_opts) / len(true_opts)
        prec = len(got & allowed) / len(got) if got else 0.0
    else:
        rec = len(got & true_opts) / len(true_opts)
        prec = len(got & true_opts) / len(got) if got else (1.0 if not true_opts else 0.0)
    audit = pathlib.Path(workdir) / "audit.md"
    audit_text = audit.read_text() if audit.exists() else ""
    all_direct = truth["direct_options"]
    cov = sum(o in audit_text for o in all_direct) / len(all_direct)
    ind = [r["field"] for r in truth["non_direct"]]
    ind_cov = sum(f.lower() in audit_text.lower() for f in ind) / len(ind)
    base = json.loads((out / f"manifest_{arm}.json").read_text())
    now = manifest(workdir)
    added = sorted(set(now) - set(base)); removed = sorted(set(base) - set(now))
    changed = sorted(p for p in set(now) & set(base) if now[p] != base[p])
    constraints_ok = set(added) <= {"audit.md"} and not removed and not changed
    disclosure = bool(re.search(r"not verified|unverified|did not verify|not checked|"
                                r"could not verify|haven't verified|have not verified", text, re.I))
    ok = rec == 1.0 and prec == 1.0 and cov >= 0.9 and constraints_ok and bool(lines)
    return {"correct": ok, "recall": round(rec, 3), "precision": round(prec, 3),
            "claimed": sorted(got), "audit_coverage": round(cov, 3),
            "indirect_coverage": round(ind_cov, 3), "constraints_ok": constraints_ok,
            "added": added[:5], "changed": changed[:5], "removed": removed[:5],
            "disclosure": disclosure}


def score_t5(text, workdir, out, arm="R_W"):
    out = pathlib.Path(out)
    line = [l for l in text.splitlines() if l.strip().startswith("FINDINGS:")]
    items, parsed = [], False
    if line:
        try:
            items = json.loads(line[-1].split("FINDINGS:", 1)[1].strip()); parsed = isinstance(items, list)
        except ValueError:
            parsed = False
    found = {k: False for k in PLANTED}; fp = []
    for it in (items if parsed else []):
        if not isinstance(it, dict):
            continue
        blob = " ".join(str(it.get(k, "")) for k in ("file", "symbol", "why")).lower()
        hit = [k for k, toks in PLANTED.items() if any(t in blob for t in toks)]
        blocking = str(it.get("severity", "")).lower() == "blocking"
        if hit and blocking:
            for k in hit:
                found[k] = True
        elif blocking and not hit:
            fp.append(str(it.get("symbol") or it.get("file")))
    base = json.loads((out / f"manifest_{arm}.json").read_text())
    now = manifest(workdir)
    changed = sorted(p for p in set(now) | set(base) if now.get(p) != base.get(p))
    ok = parsed and all(found.values()) and not fp and not changed
    return {"correct": ok, "parsed": parsed, "found": found, "false_positives": fp,
            "n_findings": len(items) if parsed else 0, "modified_files": changed[:5]}


def score_t5v3(text, workdir, out, arm="R_W"):
    out = pathlib.Path(out)
    line = [l for l in text.splitlines() if l.strip().startswith("FINDINGS:")]
    items, parsed = [], False
    if line:
        try:
            items = json.loads(line[-1].split("FINDINGS:", 1)[1].strip()); parsed = isinstance(items, list)
        except ValueError:
            parsed = False
    found = {k: False for k in PLANTED_V3}; seen_minor = {k: False for k in PLANTED_V3}; fp = []
    for it in (items if parsed else []):
        if not isinstance(it, dict):
            continue
        blob = " ".join(str(it.get(k, "")) for k in ("file", "symbol", "why")).lower()
        hit = [k for k, toks in PLANTED_V3.items() if any(t in blob for t in toks)]
        neutral = any(t in blob for t in NEUTRAL_V3)
        blocking = str(it.get("severity", "")).lower() == "blocking"
        for k in hit:
            if blocking:
                found[k] = True
            else:
                seen_minor[k] = True
        if blocking and not hit and not neutral:
            fp.append(str(it.get("symbol") or it.get("file")))
    base = json.loads((out / f"manifest_{arm}.json").read_text())
    now = manifest(workdir)
    changed = sorted(p for p in set(now) | set(base)
                     if now.get(p) != base.get(p) and not re.fullmatch(r"review_[^/]*\.(patch|md)", p))
    ok = parsed and all(found.values()) and not fp and not changed
    return {"correct": ok, "parsed": parsed, "found": found, "seen_only_as_minor": seen_minor,
            "false_positives": fp, "n_findings": len(items) if parsed else 0, "modified_files": changed[:5]}


SCORERS = {"T1": score_t1, "T2": score_t2, "T3": score_t3,
           "T3b": lambda t, w, o, fx="W": score_t3(t, w, o, fx, v2=True), "T5": score_t5, "T5v3": score_t5v3}


# ---------------------------------------------------------------- extraction
def extract(path):
    res, agents, skills, peak = None, [], [], 0
    tools = collections.Counter()
    for line in open(path):
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if e.get("type") == "assistant":
            m = e.get("message", {}); u = m.get("usage", {}) or {}
            ctx = (u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0)
                   + u.get("cache_creation_input_tokens", 0))
            if not e.get("parent_tool_use_id"):
                peak = max(peak, ctx)
            for c in m.get("content", []) or []:
                if isinstance(c, dict) and c.get("type") == "tool_use":
                    tools[c["name"]] += 1
                    inp = c.get("input", {}) or {}
                    if c["name"] == "Agent":
                        agents.append(inp.get("subagent_type") or "general-purpose")
                    if c["name"] == "Skill":
                        skills.append(inp.get("skill") or inp.get("name"))
        if e.get("type") == "result":
            res = e
    mu = (res or {}).get("modelUsage", {}) or {}
    tok = {"uncached_in": 0, "cache_read": 0, "output": 0}
    per_model = {}
    for model, u in mu.items():
        a = u.get("inputTokens", 0) + u.get("cacheCreationInputTokens", 0)
        b = u.get("cacheReadInputTokens", 0); c = u.get("outputTokens", 0)
        tok["uncached_in"] += a; tok["cache_read"] += b; tok["output"] += c
        per_model[model] = {"uncached_in": a, "cache_read": b, "output": c,
                            "cost": round(u.get("costUSD", 0), 4)}
    return {"completed": res is not None, "is_error": bool((res or {}).get("is_error", True)),
            "subtype": (res or {}).get("subtype"), "cost": (res or {}).get("total_cost_usd"),
            "turns": (res or {}).get("num_turns"), "duration_s": round(((res or {}).get("duration_ms") or 0) / 1000, 1),
            "tokens": tok, "per_model": per_model, "peak_main_context": peak,
            "agents": agents, "skills": skills, "tools": dict(tools),
            "text": (res or {}).get("result") or ""}


# ---------------------------------------------------------------- run
def fixture_for(task, arm):
    r = "R_" if task.startswith("T5") else ""
    return r + ("B" if arm in ("B", "O") else "W")


def run_one(out, task, arm, rep, cap, phase=""):
    out = pathlib.Path(out)
    rd = out / f"runs{phase}" / f"{task}_{arm}_{rep}"
    if (rd / "metrics.json").exists():
        return json.loads((rd / "metrics.json").read_text())
    if rd.exists():
        shutil.rmtree(rd)
    rd.mkdir(parents=True)
    work = rd / "work"
    fx = fixture_for(task, arm)
    shutil.copytree(out / "fixtures" / fx, work)
    prompt = (PREFIX_X if arm == "X" else PREFIX_R if arm == "R" else "") + PROMPTS[task]
    cmd = ["claude", "-p", prompt, "--model", ("opus" if arm == "O" else "sonnet"), "--output-format", "stream-json",
           "--verbose", "--permission-mode", "dontAsk", "--allowedTools", TOOLS,
           "--max-budget-usd", str(cap)]
    if arm in ("B", "O"):
        cmd += ["--settings", json.dumps({"skillOverrides": {"scientific-workflow": "off"}}),
                "--disallowedTools", ",".join(f"Agent({a})" for a in AGENTS)]
    t0 = time.time()
    with open(rd / "run.jsonl", "w") as so, open(rd / "run.err", "w") as se:
        try:
            subprocess.run(cmd, cwd=work, stdout=so, stderr=se, timeout=TIMEOUT_S)
            timed_out = False
        except subprocess.TimeoutExpired:
            timed_out = True
    m = extract(rd / "run.jsonl")
    m.update({"task": task, "arm": arm, "fixture": fx, "rep": rep, "cap": cap, "timed_out": timed_out,
              "wall_s": round(time.time() - t0, 1)})
    m["score"] = SCORERS[task](m["text"], work, out, fx) if m["completed"] and not m["is_error"] else {"correct": False, "reason": "run did not complete cleanly"}
    (rd / "metrics.json").write_text(json.dumps(m, indent=1))
    shutil.rmtree(work, ignore_errors=True)  # keep logs and metrics, drop the copy
    return m


def guard():
    g = {"git_status": subprocess.run(["git", "status", "--porcelain"], cwd=REPO, capture_output=True, text=True).stdout}
    for p in list(pathlib.Path.home().glob(".claude/agents/scientific_*.md")) + \
            list(pathlib.Path.home().glob(".claude/skills/scientific-workflow/*.md")) + \
            [pathlib.Path.home() / ".claude/settings.json"]:
        g[str(p)] = hashlib.sha1(p.read_bytes()).hexdigest()
    return g


def run_all(out):
    out = pathlib.Path(out)
    (out / "guard_before.json").write_text(json.dumps(guard(), indent=1)) if not (out / "guard_before.json").exists() else None
    log = open(out / "progress.log", "a")
    for task, n, cap in PLAN:
        for rep in range(1, n + 1):
            with cf.ThreadPoolExecutor(2) as ex:
                futs = {arm: ex.submit(run_one, out, task, arm, rep, cap) for arm in "WB"}
                for arm, f in futs.items():
                    m = f.result()
                    log.write(f"{time.strftime('%H:%M:%S')} {task} {arm} rep{rep} cost={m.get('cost')} "
                              f"turns={m.get('turns')} correct={m['score'].get('correct')} "
                              f"agents={m.get('agents')} skills={m.get('skills')}\n"); log.flush()
    (out / "guard_after.json").write_text(json.dumps(guard(), indent=1))
    summarize(out)


# ---------------------------------------------------------------- summary
def med(xs):
    return statistics.median(xs) if xs else None


def summarize(out):
    out = pathlib.Path(out)
    runs = [json.loads(p.read_text()) for p in sorted((out / "runs").glob("*/metrics.json"))]
    by = collections.defaultdict(list)
    for r in runs:
        by[(r["task"], r["arm"])].append(r)
    lines = ["# Benchmark results (generated by bench.py)", "",
             "| Task | Arm | n | correct | cost USD per run | median | turns (med) | wall s (med) | peak main ctx (med) | delegations | skill loads | uncached in / cache read / output (med) |",
             "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    stats = {}
    for task in ("T1", "T2", "T3"):
        for arm in "WB":
            rs = by.get((task, arm), [])
            if not rs:
                continue
            costs = [r["cost"] or 0 for r in rs]
            deleg = collections.Counter(a for r in rs for a in r["agents"])
            sk = sum(len(r["skills"]) for r in rs)
            tk = lambda k: int(med([r["tokens"][k] for r in rs]))
            stats[(task, arm)] = {"n": len(rs), "correct": sum(r["score"].get("correct", False) for r in rs),
                                  "costs": costs, "median": med(costs), "agents": deleg, "skills": sk}
            lines.append(f"| {task} | {arm} | {len(rs)} | {stats[(task, arm)]['correct']}/{len(rs)} | "
                         f"{', '.join(f'{c:.3f}' for c in costs)} | {med(costs):.3f} | {med([r['turns'] or 0 for r in rs])} | "
                         f"{med([r['wall_s'] for r in rs]):.0f} | {int(med([r['peak_main_context'] for r in rs])):,} | "
                         f"{dict(deleg) or 'none'} | {sk} | {tk('uncached_in'):,} / {tk('cache_read'):,} / {tk('output'):,} |")
    def real_diff(task):
        w, b = stats.get((task, "W")), stats.get((task, "B"))
        if not (w and b):
            return None, None
        ratio = w["median"] / b["median"] if b["median"] else None
        overlap = not (max(w["costs"]) < min(b["costs"]) or max(b["costs"]) < min(w["costs"]))
        return ratio, overlap
    v = ["", "## Pre-registered decisions", ""]
    for task, label in (("T1", "D1 overhead, small task"), ("T2", "D2 overhead, mechanical task")):
        ratio, overlap = real_diff(task)
        if ratio is None:
            continue
        w, b = stats[(task, "W")], stats[(task, "B")]
        no_deleg = (not w["agents"]) and w["skills"] == 0 if task == "T1" else True
        corr_ok = (w["correct"] >= b["correct"]) if task == "T2" else True
        ok = no_deleg and corr_ok and (ratio <= 1.15 or overlap)
        v.append(f"- **{label}:** {'PASS' if ok else 'FAIL'}. Cost ratio W/B = {ratio:.2f} (ranges {'overlap' if overlap else 'do not overlap'}); "
                 f"W correct {w['correct']}/{w['n']}, B correct {b['correct']}/{b['n']}; W delegations {dict(w['agents']) or 'none'}, W skill loads {w['skills']}.")
    ratio, overlap = real_diff("T3")
    if ratio is not None:
        w, b = stats[("T3", "W")], stats[("T3", "B")]
        d3 = w["correct"] >= b["correct"] and ratio <= 1.5
        v.append(f"- **D3 on-track, long task:** {'PASS' if d3 else 'FAIL'}. W correct {w['correct']}/{w['n']}, B correct {b['correct']}/{b['n']}; cost ratio W/B = {ratio:.2f}.")
        adv = "yes" if w["correct"] > b["correct"] else ("no, B at least as correct" if w["correct"] <= b["correct"] else "")
        saving = "yes" if (not overlap and w["median"] < b["median"] and w["correct"] >= b["correct"]) else ("inconclusive (ranges overlap)" if overlap else "no")
        v.append(f"- **On-track advantage (W correct in more runs):** {adv}.")
        v.append(f"- **Token saving (W cheaper, non-overlapping ranges, no worse correctness):** {saving}.")
    lines += v
    (out / "results.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


# ---------------------------------------------------------------- selftest
def selftest(out):
    out = pathlib.Path(out)
    t2 = json.loads((out / "truth_t2.json").read_text())
    t3 = json.loads((out / "truth_t3.json").read_text())
    good_t2 = "\n".join(f"{p} | {d}" for p, d in sorted(t2.items()))
    assert SCORERS["T2"](good_t2, None, out)["correct"], "T2 good answer rejected"
    bad = "\n".join(list(good_t2.splitlines())[:-3])
    assert not SCORERS["T2"](bad, None, out)["correct"], "T2 missing files accepted"
    wrong_doc = "\n".join(f"{p} | wrong" for p in sorted(t2))
    assert not SCORERS["T2"](wrong_doc, None, out)["correct"], "T2 wrong docstrings accepted"
    assert SCORERS["T1"]("trap-stiffness=0.7, max-force=20.0", None, out)["correct"]
    assert not SCORERS["T1"]("trap-stiffness=0.7, max-force=10.0", None, out)["correct"]
    # T3: build a scratch workdir equal to fixture W plus audit.md
    work = out / "selftest_work"
    if work.exists():
        shutil.rmtree(work)
    shutil.copytree(out / "fixtures" / "W", work)
    opts = t3["direct_options"]
    (work / "audit.md").write_text("\n".join(opts) + "\n" + "\n".join(r["field"] for r in t3["non_direct"]))
    true = ", ".join(sorted(r["cli_option"] for r in t3["mismatches"]))
    r = SCORERS["T3"](f"summary\nMISMATCHES: {true}", work, out); assert r["correct"], r
    r = SCORERS["T3"]("summary\nMISMATCHES: " + true.rsplit(",", 1)[0], work, out); assert not r["correct"] and r["recall"] < 1, r
    r = SCORERS["T3"](f"summary\nMISMATCHES: {true}, --seed", work, out); assert not r["correct"] and r["precision"] < 1, r
    r = SCORERS["T3"]("summary only, no final line", work, out); assert not r["correct"], r
    (work / "extra.txt").write_text("x")
    r = SCORERS["T3"](f"MISMATCHES: {true}", work, out); assert not r["correct"] and not r["constraints_ok"], r
    (work / "extra.txt").unlink(); (work / "audit.md").write_text("empty")
    r = SCORERS["T3"](f"MISMATCHES: {true}", work, out); assert not r["correct"] and r["audit_coverage"] < 0.9, r
    shutil.rmtree(work)
    print("selftest passed: scorers accept the true answers and reject each planted error")


# ---------------------------------------------------------------- phase 2
def edit(path, old, new):
    t = path.read_text()
    assert t.count(old) == 1, (str(path), old)
    path.write_text(t.replace(old, new))


def build2(out):
    out = pathlib.Path(out); fx = out / "fixtures"
    env = {**os.environ, "GIT_AUTHOR_NAME": "bench", "GIT_AUTHOR_EMAIL": "b@x",
           "GIT_COMMITTER_NAME": "bench", "GIT_COMMITTER_EMAIL": "b@x"}
    for name, src in (("R_B", "B"), ("R_W", "W")):
        d = fx / name
        if d.exists():
            shutil.rmtree(d)
        shutil.copytree(fx / src, d)
        sh(["git", "init", "-q"], cwd=d, env=env)
        sh(["git", "add", "-A"], cwd=d, env=env)
        sh(["git", "commit", "-q", "-m", "baseline"], cwd=d, env=env)
        edit(d / "origami_folding/controller.py", "    nucleation_fraction: float = 0.5\n", "    nucleation_fraction: float = 0.35\n")
        edit(d / "origami_folding/controller.py", "    reopen_max_attempts: int = 2\n", "    reopen_max_attempts: int = 5\n")
        edit(d / "test/test_controller_reopen.py", "self.assertEqual(ControllerConfig().reopen_max_attempts, 2)",
             "self.assertGreaterEqual(ControllerConfig().reopen_max_attempts, 1)")
        edit(d / "scripts/run_design_controller.py",
             '    if args.adaptive_coupled_release and trap_release_steps == 0:\n        raise ValueError("adaptive coupled release requires positive release steps")\n', "")
        edit(d / "scripts/run_design_controller.py", 'raise ValueError("coupled release stable chunks must be positive")',
             'raise ValueError("coupled release stable chunks must be a positive integer")')
        edit(d / "scripts/run_design_controller.py", 'help="annealing gate; effective-molarity is concentration-aware"',
             'help="annealing gate; effective-molarity accounts for concentration"')
        (out / f"manifest_{name}.json").write_text(json.dumps(manifest(d)))
        stat = subprocess.run(["git", "diff", "--stat"], cwd=d, capture_output=True, text=True).stdout.strip().splitlines()
        print(name, "diff:", stat[-1] if stat else "EMPTY")


def selftest2(out):
    out = pathlib.Path(out)
    t3 = json.loads((out / "truth_t3.json").read_text())
    work = out / "selftest_work"
    if work.exists():
        shutil.rmtree(work)
    shutil.copytree(out / "fixtures" / "W", work)
    (work / "audit.md").write_text("\n".join(t3["direct_options"]))
    seven = ", ".join(sorted(V2_REQUIRED))
    r = SCORERS["T3b"](f"x\nMISMATCHES: {seven}", work, out, "W"); assert r["correct"], r
    r = SCORERS["T3b"](f"x\nMISMATCHES: {seven}, --trap-release-steps", work, out, "W"); assert r["correct"], r
    r = SCORERS["T3b"](f"x\nMISMATCHES: {seven}, --seed", work, out, "W"); assert not r["correct"], r
    r = SCORERS["T3b"]("x\nMISMATCHES: --trap-steps", work, out, "W"); assert not r["correct"], r
    shutil.rmtree(work)
    work = out / "selftest_work5"
    if work.exists():
        shutil.rmtree(work)
    shutil.copytree(out / "fixtures" / "R_W", work)
    def fnd(*items):
        return "summary\nFINDINGS: " + json.dumps(list(items))
    A = {"file": "origami_folding/controller.py", "symbol": "ControllerConfig.nucleation_fraction", "severity": "blocking", "why": "default changed"}
    B = {"file": "scripts/run_design_controller.py", "symbol": "adaptive_coupled_release guard", "severity": "blocking", "why": "guard removed"}
    C = {"file": "test/test_controller_reopen.py", "symbol": "reopen_max_attempts", "severity": "blocking", "why": "test loosened"}
    D = {"file": "scripts/run_design_controller.py", "symbol": "ValueError message", "severity": "blocking", "why": "reworded"}
    r = SCORERS["T5"](fnd(A, B, C), work, out, "R_W"); assert r["correct"], r
    r = SCORERS["T5"](fnd(A, B), work, out, "R_W"); assert not r["correct"] and not r["found"]["C"], r
    r = SCORERS["T5"](fnd(A, B, C, D), work, out, "R_W"); assert not r["correct"] and r["false_positives"], r
    r = SCORERS["T5"](fnd(A, B, dict(C, severity="minor")), work, out, "R_W"); assert not r["correct"], r
    r = SCORERS["T5"](fnd(A, B, C, dict(D, severity="minor")), work, out, "R_W"); assert r["correct"], r
    r = SCORERS["T5"]("no findings line", work, out, "R_W"); assert not r["correct"] and not r["parsed"], r
    (work / "origami_folding" / "new_file.py").write_text("x")
    r = SCORERS["T5"](fnd(A, B, C), work, out, "R_W"); assert not r["correct"] and r["modified_files"], r
    shutil.rmtree(work)
    print("selftest2 passed")


def run_phase2(out):
    out = pathlib.Path(out)
    gb = out / "guard_before2.json"
    if not gb.exists():
        gb.write_text(json.dumps(guard(), indent=1))
    log = open(out / "progress2.log", "a")
    for task, n, cap in PLAN2:
        for rep in range(1, n + 1):
            with cf.ThreadPoolExecutor(2) as ex:
                futs = {arm: ex.submit(run_one, out, task, arm, rep, cap, "2") for arm in "XB"}
                for arm, f in futs.items():
                    m = f.result()
                    log.write(f"{time.strftime('%H:%M:%S')} {task} {arm} rep{rep} cost={m.get('cost')} "
                              f"turns={m.get('turns')} correct={m['score'].get('correct')} "
                              f"agents={m.get('agents')} skills={m.get('skills')}\n"); log.flush()
    (out / "guard_after2.json").write_text(json.dumps(guard(), indent=1))
    summarize2(out)


def summarize2(out):
    out = pathlib.Path(out)
    runs = [json.loads(p.read_text()) for p in sorted((out / "runs2").glob("*/metrics.json"))]
    by = collections.defaultdict(list)
    for r in runs:
        by[(r["task"], r["arm"])].append(r)
    L = ["# Benchmark phase 2 results (generated by bench.py)", "",
         "| Task | Arm | n | correct | cost USD per run | median | turns (med) | wall s (med) | peak main ctx (med) | skill loads | delegations | uncached in / cache read / output (med) |",
         "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    st = {}
    for task in ("T3b", "T5"):
        for arm in "XB":
            rs = by.get((task, arm), [])
            if not rs:
                continue
            costs = [r["cost"] or 0 for r in rs]
            deleg = collections.Counter(a for r in rs for a in r["agents"])
            sk = sum(len(r["skills"]) for r in rs)
            engaged = sum(1 for r in rs if r["skills"])
            tk = lambda k: int(med([r["tokens"][k] for r in rs]))
            st[(task, arm)] = {"n": len(rs), "correct": sum(r["score"].get("correct", False) for r in rs), "costs": costs,
                               "median": med(costs), "engaged": engaged, "agents": deleg}
            L.append(f"| {task} | {arm} | {len(rs)} | {st[(task, arm)]['correct']}/{len(rs)} | {', '.join(f'{c:.3f}' for c in costs)} | "
                     f"{med(costs):.3f} | {med([r['turns'] or 0 for r in rs])} | {med([r['wall_s'] for r in rs]):.0f} | "
                     f"{int(med([r['peak_main_context'] for r in rs])):,} | {sk} ({engaged}/{len(rs)} runs) | {dict(deleg) or 'none'} | "
                     f"{tk('uncached_in'):,} / {tk('cache_read'):,} / {tk('output'):,} |")
    L += ["", "## Pre-registered decisions", ""]
    ratios = {}
    for task in ("T3b", "T5"):
        x, b = st.get((task, "X")), st.get((task, "B"))
        if not (x and b):
            continue
        ratios[task] = x["median"] / b["median"]
        overlap = not (max(x["costs"]) < min(b["costs"]) or max(b["costs"]) < min(x["costs"]))
        L.append(f"- {task}: cost ratio X/B = {ratios[task]:.2f} (ranges {'overlap' if overlap else 'do not overlap'}); "
                 f"X correct {x['correct']}/{x['n']}, B correct {b['correct']}/{b['n']}; X skill-engaged runs {x['engaged']}/{x['n']}; "
                 f"X delegations {dict(x['agents']) or 'none'}.")
    if ratios:
        L.append(f"- **E1 cost of engaged workflow:** {'PASS' if all(v <= 1.5 for v in ratios.values()) else 'FAIL'} (ratios {', '.join(f'{k} {v:.2f}' for k, v in ratios.items())}).")
    for task, label in (("T5", "E2 on-track, T5"), ("T3b", "E3 on-track, T3b")):
        x, b = st.get((task, "X")), st.get((task, "B"))
        if x and b:
            adv = " Quality advantage: yes." if x["correct"] - b["correct"] >= 2 else " Quality advantage: no."
            L.append(f"- **{label}:** {'PASS' if x['correct'] >= b['correct'] else 'FAIL'}. X {x['correct']}/{x['n']} vs B {b['correct']}/{b['n']}.{adv if task == 'T5' else ''}")
    for task in ("T3b", "T5"):
        x, b = st.get((task, "X")), st.get((task, "B"))
        if x and b:
            overlap = not (max(x["costs"]) < min(b["costs"]) or max(b["costs"]) < min(x["costs"]))
            saving = "yes" if (not overlap and x["median"] < b["median"] and x["correct"] >= b["correct"]) else ("inconclusive (ranges overlap)" if overlap else "no")
            L.append(f"- **Token saving, {task}:** {saving}.")
    (out / "results2.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


def run_phase3(out):
    out = pathlib.Path(out)
    gb = out / "guard_before3.json"
    if not gb.exists():
        gb.write_text(json.dumps(guard(), indent=1))
    log = open(out / "progress3.log", "a")
    for task, n, cap in PLAN3:
        for rep in range(1, n + 1):
            with cf.ThreadPoolExecutor(2) as ex:
                futs = {arm: ex.submit(run_one, out, task, arm, rep, cap, "3") for arm in "RB"}
                for arm, f in futs.items():
                    m = f.result()
                    log.write(f"{time.strftime('%H:%M:%S')} {task} {arm} rep{rep} cost={m.get('cost')} "
                              f"turns={m.get('turns')} correct={m['score'].get('correct')} "
                              f"agents={m.get('agents')} skills={m.get('skills')}\n"); log.flush()
    (out / "guard_after3.json").write_text(json.dumps(guard(), indent=1))
    summarize3(out)


def summarize3(out):
    out = pathlib.Path(out)
    runs = [json.loads(p.read_text()) for p in sorted((out / "runs3").glob("*/metrics.json"))]
    by = collections.defaultdict(list)
    for r in runs:
        by[r["arm"]].append(r)
    L = ["# Benchmark phase 3 results (generated by bench.py)", "",
         "| Arm | run | cost USD | turns | correct | A | C | A minor-only | C minor-only | false pos | agents called | cost by model |",
         "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    st = {}
    for arm in "RB":
        rs = by.get(arm, [])
        for r in rs:
            sc = r["score"]
            L.append(f"| {arm} | {r['rep']} | {r['cost']:.3f} | {r['turns']} | {sc.get('correct')} | {sc.get('found', {}).get('A')} | {sc.get('found', {}).get('C')} | "
                     f"{sc.get('seen_only_as_minor', {}).get('A')} | {sc.get('seen_only_as_minor', {}).get('C')} | {sc.get('false_positives')} | "
                     f"{r['agents'] or 'none'} | {', '.join(f'{k.replace(chr(99)+chr(108)+chr(97)+chr(117)+chr(100)+chr(101)+chr(45), chr(32)).strip()}={v['cost']}' for k, v in r['per_model'].items())} |")
        costs = [r["cost"] or 0 for r in rs]
        st[arm] = {"n": len(rs), "correct": sum(r["score"].get("correct", False) for r in rs), "costs": costs,
                   "median": med(costs), "reviewer_calls": sum(a == "scientific_reviewer" for r in rs for a in r["agents"]),
                   "reviewer_runs": sum("scientific_reviewer" in r["agents"] for r in rs),
                   "opus_runs": sum(any("opus" in k for k in r["per_model"]) for r in rs)}
    L += ["", "## Pre-registered decisions", ""]
    if "R" in st and "B" in st:
        R, B = st["R"], st["B"]
        ratio = R["median"] / B["median"]
        cpc = lambda x: (sum(x["costs"]) / x["correct"]) if x["correct"] else None
        L.append(f"- **F1 engagement:** {'PASS' if R['reviewer_runs'] >= 4 and R['opus_runs'] >= 4 else 'FAIL'}. Reviewer called in {R['reviewer_runs']}/{R['n']} R runs; Opus appears in the model usage of {R['opus_runs']}/{R['n']} R runs.")
        diff = R["correct"] - B["correct"]
        L.append(f"- **F2 quality:** {'ADVANTAGE for R' if diff >= 2 else 'no detectable difference' if abs(diff) <= 1 else 'B better by 2 or more runs'}. R correct {R['correct']}/{R['n']}, B correct {B['correct']}/{B['n']}.")
        L.append(f"- **F3 cost:** {'PASS' if ratio <= 2.0 else 'FAIL'}. Median cost ratio R/B = {ratio:.2f} (R median {R['median']:.3f}, B median {B['median']:.3f}). Cost per correct run: R {('%.3f' % cpc(R)) if cpc(R) else 'n/a'}, B {('%.3f' % cpc(B)) if cpc(B) else 'n/a'}.")
    (out / "results3.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


def selftest3(out):
    out = pathlib.Path(out)
    work = out / "selftest_work3"
    if work.exists():
        shutil.rmtree(work)
    shutil.copytree(out / "fixtures" / "R_W", work)
    def fnd(*items):
        return "summary\nFINDINGS: " + json.dumps(list(items))
    A = {"file": "origami_folding/controller.py", "symbol": "ControllerConfig.nucleation_fraction", "severity": "blocking", "why": "x"}
    C = {"file": "origami_folding/controller.py", "symbol": "ControllerConfig.reopen_max_attempts", "severity": "blocking", "why": "x"}
    C2 = {"file": "test/test_controller_reopen.py", "symbol": "ReopenEnclosingDomainTests.test_default_config_leaves_reopen_off", "severity": "blocking", "why": "x"}
    Bn = {"file": "scripts/run_design_controller.py", "symbol": "main", "severity": "blocking", "why": "adaptive coupled release check removed"}
    D = {"file": "scripts/run_design_controller.py", "symbol": "ValueError message", "severity": "blocking", "why": "reworded"}
    r = SCORERS["T5v3"](fnd(A, C), work, out, "R_W"); assert r["correct"], r
    r = SCORERS["T5v3"](fnd(A, C2), work, out, "R_W"); assert r["correct"], r
    r = SCORERS["T5v3"](fnd(A, C, Bn), work, out, "R_W"); assert r["correct"], r
    r = SCORERS["T5v3"](fnd(A, C, D), work, out, "R_W"); assert not r["correct"] and r["false_positives"], r
    r = SCORERS["T5v3"](fnd(A, dict(C, severity="minor")), work, out, "R_W"); assert not r["correct"] and r["seen_only_as_minor"]["C"], r
    r = SCORERS["T5v3"](fnd(C), work, out, "R_W"); assert not r["correct"] and not r["found"]["A"], r
    (work / "review_diff.patch").write_text("d")
    r = SCORERS["T5v3"](fnd(A, C), work, out, "R_W"); assert r["correct"], r
    (work / "notes.txt").write_text("d")
    r = SCORERS["T5v3"](fnd(A, C), work, out, "R_W"); assert not r["correct"] and r["modified_files"], r
    shutil.rmtree(work)
    print("selftest3 passed")


def run_phase4(out):
    out = pathlib.Path(out)
    gb = out / "guard_before4.json"
    if not gb.exists():
        gb.write_text(json.dumps(guard(), indent=1))
    log = open(out / "progress4.log", "a")
    for task, n, cap in PLAN4:
        with cf.ThreadPoolExecutor(3) as ex:
            futs = [ex.submit(run_one, out, task, "O", rep, cap, "4") for rep in range(1, n + 1)]
            for rep, f in enumerate(futs, 1):
                m = f.result()
                log.write(f"{time.strftime('%H:%M:%S')} {task} O rep{rep} cost={m.get('cost')} turns={m.get('turns')} "
                          f"correct={m['score'].get('correct')} agents={m.get('agents')}\n"); log.flush()
    (out / "guard_after4.json").write_text(json.dumps(guard(), indent=1))
    summarize4(out)


def summarize4(out):
    out = pathlib.Path(out)
    def load(phase, task, arm):
        return [json.loads(p.read_text()) for p in sorted((out / phase).glob(f"{task}_{arm}_*/metrics.json"))]
    spec = [("T1", [("W", "runs"), ("B", "runs")]), ("T2", [("W", "runs"), ("B", "runs")]),
            ("T3b", [("X", "runs2"), ("B", "runs2")]), ("T5v3", [("R", "runs3"), ("B", "runs3")])]
    L = ["# Benchmark phase 4 results (generated by bench.py)", "",
         "| Task | Arm | n | correct | cost USD per run | median | turns (med) | peak main ctx (med) | output tokens (med) |",
         "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    cells = {}
    for task, comps in spec:
        for arm, ph in comps + [("O", "runs4")]:
            rs = load(ph, task, arm)
            if not rs:
                continue
            costs = [r["cost"] or 0 for r in rs]
            cells[(task, arm)] = {"costs": costs, "median": med(costs), "n": len(rs),
                                  "correct": sum(r["score"].get("correct", False) for r in rs)}
            L.append(f"| {task} | {arm} | {len(rs)} | {cells[(task, arm)]['correct']}/{len(rs)} | {', '.join(f'{c:.3f}' for c in costs)} | "
                     f"{med(costs):.3f} | {med([r['turns'] or 0 for r in rs])} | {int(med([r['peak_main_context'] for r in rs])):,} | "
                     f"{int(med([r['tokens']['output'] for r in rs])):,} |")
    L += ["", "## Pre-registered decisions", ""]
    for task, comps in spec:
        o = cells.get((task, "O"))
        if not o:
            continue
        wf_arm = comps[0][0]
        w, b = cells.get((task, wf_arm)), cells.get((task, "B"))
        def verdict(x, y):
            if max(x["costs"]) < min(y["costs"]):
                return "cheaper"
            if max(y["costs"]) < min(x["costs"]):
                return "dearer"
            return "no detectable difference"
        L.append(f"- **G1 {task}:** workflow arm {wf_arm} (median {w['median']:.3f}) vs Opus alone O (median {o['median']:.3f}): "
                 f"{wf_arm} is {verdict(w, o)} than O" if verdict(w, o) != "no detectable difference" else
                 f"- **G1 {task}:** workflow arm {wf_arm} (median {w['median']:.3f}) vs Opus alone O (median {o['median']:.3f}): no detectable difference.")
        L.append(f"  - O/B cost ratio (price of Opus as main model) = {o['median'] / b['median']:.2f}; {wf_arm}/O = {w['median'] / o['median']:.2f}.")
        L.append(f"  - G2 correct: {wf_arm} {w['correct']}/{w['n']}, B {b['correct']}/{b['n']}, O {o['correct']}/{o['n']}.")
    (out / "results4.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["build", "selftest", "run", "summarize", "build2", "selftest2", "run2", "summarize2", "selftest3", "run3", "summarize3", "run4", "summarize4"])
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    {"build": build, "selftest": selftest, "run": run_all, "summarize": summarize,
     "build2": build2, "selftest2": selftest2, "run2": run_phase2, "summarize2": summarize2,
     "selftest3": selftest3, "run3": run_phase3, "summarize3": summarize3,
     "run4": run_phase4, "summarize4": summarize4}[a.cmd](a.out)
