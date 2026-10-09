"""Ground truth for T2: scripts/*.py files with a module-level def main, and the first docstring line."""
import ast, sys, json, pathlib
root = pathlib.Path(sys.argv[1])
out = {}
for p in sorted((root / "scripts").rglob("*.py")):
    try:
        tree = ast.parse(p.read_text())
    except SyntaxError:
        continue
    if any(isinstance(n, ast.FunctionDef) and n.name == "main" for n in tree.body):
        doc = ast.get_docstring(tree)
        out[str(p.relative_to(root))] = doc.strip().splitlines()[0].strip() if doc else "none"
json.dump(out, sys.stdout, indent=0)
