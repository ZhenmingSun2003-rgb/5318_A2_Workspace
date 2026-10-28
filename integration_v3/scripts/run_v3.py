#!/usr/bin/env python3
"""Run the integrated A2 notebook in the pinned V2-compatible Docker CPU image.

Validate: no training, Python syntax & template audit.
Execute: fresh Jupyter kernel from the repository root; train frozen models;
         preserve executed Notebook and independently recomputed outputs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import traceback

import nbformat
from nbclient import NotebookClient


ROOT = Path(__file__).resolve().parents[2] if Path(__file__).resolve().parents[2].joinpath("Canvas Sources").exists() else Path("/workspace/repo")
NOTEBOOK = ROOT / "integration_v3" / "COMP5318_A2_Integrated.ipynb"
EXPECTED_SECTIONS = (
    "## Setup and dependencies",
    "## 1. Data loading, exploration, and preprocessing",
    "## 2. Algorithm design and setup",
    "## 3. Hyperparameter tuning",
    "## 4. Final models",
    "## 5. AI Acknowledgement",
)
REQUIRED_MODELS = {"Dummy", "Nearest Centroid", "GaussianNB", "MLP", "CNN"}


def validate_notebook():
    notebook = nbformat.read(NOTEBOOK, as_version=4)
    nbformat.validate(notebook)
    headings = [cell.source.splitlines()[0] for cell in notebook.cells
                if cell.cell_type == "markdown" and cell.source.startswith("## ")]
    if tuple(headings) != EXPECTED_SECTIONS:
        raise AssertionError(f"Canvas section structure mismatch: {headings}")
    code_cells = [cell for cell in notebook.cells if cell.cell_type == "code"]
    if len(code_cells) < 20:
        raise AssertionError("A source model section appears missing")
    seen = set()
    for i, cell in enumerate(notebook.cells):
        if cell.id in seen:
            raise AssertionError(f"Duplicate cell id: {cell.id}")
        seen.add(cell.id)
        if cell.cell_type == "code":
            compile(cell.source, f"{NOTEBOOK.name}:cell_{i:03d}", "exec")
    provenance = [cell.metadata.get("source_provenance", "") for cell in code_cells]
    for source in ("Naive_Bayes", "MLP", "CNN"):
        if not any(text.startswith(source + ":") for text in provenance):
            raise AssertionError(f"Missing integrated source cells for {source}")
    for filename in ("X_train.npy", "y_train.npy", "X_test.npy", "y_test.npy"):
        if not (ROOT / "Canvas Sources" / "Assignment2Data-1" / "Assignment2Data" / filename).is_file():
            raise FileNotFoundError(filename)
    for model in ("strict_baseline", "strict_naive_bayes", "strict_mlp", "strict_cnn"):
        if not (ROOT / "reproduction_v2" / "results" / model / "verified_metrics.json").is_file():
            raise FileNotFoundError(model)
    print(f"PASS: Notebook valid; {len(notebook.cells)} cells; "
          f"{len(code_cells)} Python code cells; original Canvas data and V2 evidence present.",
          flush=True)
    return notebook


def main():
    parser = argparse.ArgumentParser()
    choice = parser.add_mutually_exclusive_group()
    choice.add_argument("--validate", action="store_true",
                        help="static template, provenance, source and code syntax checks")
    choice.add_argument("--execute", action="store_true",
                        help="execute fresh kernel, fit all five final models")
    parser.add_argument("--tune", action="store_true",
                        help="also run 8-trial grids for each required model")
    parser.add_argument("--timeout", type=int, default=5400, help="per-cell timeout seconds")
    args = parser.parse_args()
    notebook = validate_notebook()
    if args.validate:
        return 0
    output = Path(os.environ.get("V3_OUTPUT_DIR", ROOT / "integration_v3" / "outputs"))
    output.mkdir(parents=True, exist_ok=True)
    os.environ["V3_RUN_TUNING"] = "1" if args.tune else "0"
    os.environ.setdefault("A2_DATA_DIR", str(ROOT / "Canvas Sources" / "Assignment2Data-1" / "Assignment2Data"))
    os.environ.setdefault("TF_DETERMINISTIC_OPS", "1")
    os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
    os.environ.setdefault("PYTHONHASHSEED", "5318")
    status = {"status": "RUNNING", "tune": args.tune,
              "notebook_sha256": hashlib.sha256(NOTEBOOK.read_bytes()).hexdigest()}
    status_path = output / "run_status.json"
    status_path.write_text(json.dumps(status, indent=2), encoding="utf-8")
    try:
        client = NotebookClient(
            notebook, timeout=args.timeout, kernel_name="python3",
            resources={"metadata": {"path": str(ROOT)}},
            allow_errors=False, record_timing=True,
        )
        executed = client.execute()
        nbformat.write(executed, output / "executed.ipynb")
        summary = json.loads((output / "summary.json").read_text(encoding="utf-8"))
        models = {item["model"] for item in summary["scores"]}
        assert models == REQUIRED_MODELS, (models, REQUIRED_MODELS)
        assert summary["n_train"] == 32000 and summary["n_test"] == 8000
        for row in summary["scores"]:
            assert row["source"] == "V3_CURRENT_RUN"
            for metric in ("accuracy", "macro_f1", "balanced_accuracy"):
                assert 0 <= row[metric] <= 1
        status["status"] = "PASS"
        status["metrics"] = {r["model"]: r["macro_f1"] for r in summary["scores"]}
        print("PASS: five frozen final models executed and verified.", flush=True)
    except Exception as exc:
        nbformat.write(notebook, output / "executed_partial.ipynb")
        status["status"] = "FAIL"
        status["error"] = repr(exc)
        status["traceback"] = traceback.format_exc()
        raise
    finally:
        status_path.write_text(json.dumps(status, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
