from __future__ import annotations

"""Static notebook gate: parse code cells and reject persisted exceptions."""

import ast
import json
from pathlib import Path

failed = False
for path in sorted(Path("Notebooks").glob("*.ipynb")):
    notebook = json.loads(path.read_text(encoding="utf-8"))
    for index, cell in enumerate(notebook["cells"]):
        if cell["cell_type"] != "code":
            continue
        source = "".join(cell["source"])
        source = "\n".join(line for line in source.splitlines() if not line.lstrip().startswith("%"))
        try:
            ast.parse(source)
        except SyntaxError as exc:
            print(f"{path}: cell {index}: {exc}")
            failed = True
        if any(output.get("output_type") == "error" for output in cell.get("outputs", [])):
            print(f"{path}: cell {index}: contains a saved error")
            failed = True
if failed:
    raise SystemExit(1)
print("Notebook static checks passed")

