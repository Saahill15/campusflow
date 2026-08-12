import ast
from pathlib import Path
import sys
root = Path('backend')
py_files = list(root.rglob('*.py'))
imports = set()
for path in py_files:
    try:
        src = path.read_text()
        tree = ast.parse(src)
    except Exception:
        continue
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split('.')[0])
root_names = {p.name for p in root.iterdir() if p.is_dir()}
stdlib = set(sys.stdlib_module_names)
local = root_names | {'backend','dependencies','api','services','schemas','repos','models','core','app','middleware','scripts','tests'}
third_party = sorted([m for m in imports if m not in stdlib and m not in local])
print('\n'.join(third_party))
