import ast, sys, json
root = sys.argv[1]
cli = ast.parse(open(f"{root}/scripts/run_design_controller.py").read())
ctl = ast.parse(open(f"{root}/origami_folding/controller.py").read())

def lit(node):
    try: return ast.literal_eval(node)
    except Exception: return "<expr:" + ast.unparse(node) + ">"

# CLI: dest -> default
cli_def = {}
for n in ast.walk(cli):
    if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "add_argument":
        opts = [a.value for a in n.args if isinstance(a, ast.Constant) and isinstance(a.value, str)]
        kw = {k.arg: k.value for k in n.keywords}
        long = [o for o in opts if o.startswith("--")]
        dest = lit(kw["dest"]) if "dest" in kw else (long[0][2:].replace("-", "_") if long else opts[0])
        action = lit(kw["action"]) if "action" in kw else None
        default = lit(kw["default"]) if "default" in kw else (False if action == "store_true" else (True if action == "store_false" else None))
        cli_def[dest] = {"option": long[0] if long else opts[0], "default": default, "required": bool(lit(kw["required"])) if "required" in kw else False}

# ControllerConfig field defaults
cfg_def = {}
for n in ctl.body:
    if isinstance(n, ast.ClassDef) and n.name == "ControllerConfig":
        for s in n.body:
            if isinstance(s, ast.AnnAssign) and isinstance(s.target, ast.Name):
                cfg_def[s.target.id] = lit(s.value) if s.value is not None else "<no default>"

# mapping in CLI: ControllerConfig(field=args.dest ...)
mapping = {}
for n in ast.walk(cli):
    if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "ControllerConfig":
        for k in n.keywords:
            v = k.value
            if isinstance(v, ast.Attribute) and isinstance(v.value, ast.Name) and v.value.id == "args":
                mapping[k.arg] = ("args", v.attr)
            else:
                mapping[k.arg] = ("expr", ast.unparse(v))

rows = []
for field, (kind, src) in sorted(mapping.items()):
    if kind == "args":
        c = cli_def.get(src, {})
        cd = cfg_def.get(field, "<missing field>")
        same = (c.get("default") == cd) or (c.get("default") is None and cd is None)
        rows.append({"field": field, "cli_dest": src, "cli_option": c.get("option"), "cli_default": c.get("default"), "config_default": cd, "match": bool(same)})
    else:
        rows.append({"field": field, "cli_dest": None, "expr": src, "config_default": cfg_def.get(field, "<missing field>"), "match": None})
out = {"n_fields_in_config": len(cfg_def), "n_cli_options": len(cli_def), "n_mapped": len(mapping),
       "n_direct_args": sum(1 for r in rows if r["match"] is not None),
       "direct_options": sorted(r["cli_option"] for r in rows if r["match"] is not None),
       "mismatches": [r for r in rows if r["match"] is False],
       "non_direct": [r for r in rows if r["match"] is None]}
json.dump(out, sys.stdout, indent=1, default=str)
