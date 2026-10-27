"""Temporary, read-only notebook inventory for the V1 audit."""
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
for name in ("baseline.ipynb", "Naive_Bayes.ipynb", "MLP.ipynb", "CNN.ipynb"):
    if len(sys.argv) > 1 and name not in sys.argv[1:]:
        continue
    notebook = json.loads((root / "archive" / "v1" / "notebooks" / name).read_text(encoding="utf-8"))
    print(f"\n## {name}: {len(notebook['cells'])} cells")
    for i, cell in enumerate(notebook["cells"]):
        source = "".join(cell.get("source", []))
        outputs = cell.get("outputs", [])
        texts = []
        for output in outputs:
            if "text" in output:
                texts.append("".join(output["text"]))
            for key in ("text/plain", "text/html"):
                if key in output.get("data", {}):
                    texts.append("".join(output["data"][key]))
            if output.get("ename"):
                texts.append(f"ERROR {output['ename']}: {output.get('evalue')}")
        summary = " ".join(source.split())[:180]
        evidence = " | ".join(" ".join(x.split())[:220] for x in texts)[:350]
        print(f"{i:02d} {cell['cell_type'][:1]} count={cell.get('execution_count')} outputs={len(outputs)} {summary}")
        if evidence:
            print("    =>", evidence)
        if len(sys.argv) > 2 and str(i) in sys.argv[2:]:
            print("SOURCE:\n", source)
            for j, output in enumerate(outputs):
                print(f"OUTPUT {j} {output.get('output_type')}:")
                print("".join(output.get("text", [])))
                print("".join(output.get("data", {}).get("text/plain", [])))
