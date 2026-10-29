#!/usr/bin/env python3
"""Execute the A2 notebook top-to-bottom in a fresh Jupyter kernel.

Usage (inside the pinned container, or any environment with the pinned packages):
    python environment/run_notebook.py            # tuning cells skipped, final models trained
    python environment/run_notebook.py --tune     # also re-run every hyperparameter search

The executed copy (with all outputs and figures) is written to the results
directory; the submitted notebook itself is never modified.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
from pathlib import Path

import nbformat
from nbclient import NotebookClient

EXPECTED_SECTIONS = (
    "## Setup and dependencies",
    "## 1. Data loading, exploration, and preprocessing",
    "## 2. Algorithm design and setup",
    "## 3. Hyperparameter tuning",
    "## 4. Final models",
    "## 5. AI Acknowledgement",
)


def find_package_root() -> Path:
    for candidate in (Path.cwd(), Path(__file__).resolve().parents[1], Path("/workspace/a2")):
        if (candidate / "Assignment2Data" / "X_train.npy").is_file():
            return candidate
    raise FileNotFoundError("Run from the package root that contains Assignment2Data/.")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tune", action="store_true", help="re-run all hyperparameter searches")
    parser.add_argument("--notebook", default=None, help="notebook to execute (default: the a2-code-*.ipynb)")
    parser.add_argument("--timeout", type=int, default=7200, help="per-cell timeout in seconds")
    args = parser.parse_args()

    root = find_package_root()
    notebook_path = Path(args.notebook) if args.notebook else sorted(root.glob("a2-code-*.ipynb"))[0]
    results = Path(os.environ.get("A2_RESULTS_DIR", root / "results"))
    results.mkdir(parents=True, exist_ok=True)

    notebook = nbformat.read(notebook_path, as_version=4)
    nbformat.validate(notebook)
    headings = [c.source.splitlines()[0] for c in notebook.cells
                if c.cell_type == "markdown" and c.source.startswith("## ")]
    assert tuple(headings) == EXPECTED_SECTIONS, f"Template section mismatch: {headings}"
    for i, cell in enumerate(notebook.cells):
        if cell.cell_type == "code":
            compile(cell.source, f"{notebook_path.name}:cell{i}", "exec")
    print(f"Template structure and code syntax OK ({notebook_path.name}).", flush=True)

    os.environ["A2_RUN_TUNING"] = "1" if args.tune else "0"
    os.environ["A2_RESULTS_DIR"] = str(results)
    status = {"notebook": notebook_path.name, "tuning": args.tune, "status": "RUNNING"}
    started = time.time()
    try:
        client = NotebookClient(notebook, timeout=args.timeout, kernel_name="python3",
                                resources={"metadata": {"path": str(root)}},
                                allow_errors=False, record_timing=True)
        executed = client.execute()
        out_name = notebook_path.stem + ("_executed_with_tuning" if args.tune else "_executed") + ".ipynb"
        nbformat.write(executed, results / out_name)
        status.update(status="PASS", executed_notebook=out_name,
                      wall_seconds=round(time.time() - started, 1))
        print(f"PASS in {status['wall_seconds']} s -> {results / out_name}", flush=True)
        code = 0
    except Exception as exc:  # keep the traceback for auditing
        status.update(status="FAIL", error=repr(exc), traceback=traceback.format_exc())
        print(status["traceback"], file=sys.stderr)
        code = 1
    (results / "run_status.json").write_text(json.dumps(status, indent=2), encoding="utf-8")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
