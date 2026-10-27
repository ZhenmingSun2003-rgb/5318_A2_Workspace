"""Execute the English reference baseline and synchronise output cells to Chinese."""
import copy
import os
import tempfile
from pathlib import Path
import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[3]
V1 = ROOT / "archive" / "v1"
ENGLISH = V1 / "notebooks" / "baseline.ipynb"
CHINESE = V1 / "notebooks_zh" / "baseline_中文版.ipynb"

def main():
    en = nbformat.read(ENGLISH, as_version=4)
    zh = nbformat.read(CHINESE, as_version=4)
    en_codes = [c for c in en.cells if c.cell_type == "code"]
    zh_codes = [c for c in zh.cells if c.cell_type == "code"]
    if len(en_codes) != len(zh_codes):
        raise RuntimeError("English/Chinese notebook code-cell counts differ.")
    for left, right in zip(en_codes, zh_codes):
        if left.source != right.source:
            raise RuntimeError("Bilingual code differs; refusing to paste mismatched results.")

    client = NotebookClient(
        en, timeout=900, kernel_name="python3",
        resources={"metadata": {"path": str(ROOT)}},
        allow_errors=False,
    )
    executed = client.execute()
    result_codes = [c for c in executed.cells if c.cell_type == "code"]
    if len(result_codes) != len(zh_codes):
        raise RuntimeError("Unexpected executed code-cell count.")
    for source_cell, target_cell in zip(result_codes, zh_codes):
        target_cell.outputs = copy.deepcopy(source_cell.outputs)
        target_cell.execution_count = source_cell.execution_count

    nbformat.validate(executed)
    nbformat.validate(zh)
    output = Path(os.environ.get("V1_BASELINE_OUTPUT_DIR") or tempfile.mkdtemp(prefix="comp5318-v1-baseline-"))
    output.mkdir(parents=True, exist_ok=True)
    nbformat.write(executed, output / ENGLISH.name)
    nbformat.write(zh, output / CHINESE.name)
    print(f"Executed V1 baseline to {output}; archived source notebooks were not modified.")

if __name__ == "__main__":
    main()
