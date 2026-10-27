"""Execute unmodified source cells in isolated kernels and export audit evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
import traceback
import uuid
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

import nbformat
import numpy as np
from nbclient import NotebookClient
from sklearn.metrics import accuracy_score, balanced_accuracy_score, classification_report, confusion_matrix, f1_score

ROOT = Path("/workspace/repo") if Path("/workspace/repo").is_dir() else Path(__file__).resolve().parents[2]
V2 = ROOT / "reproduction_v2"
RUNS = V2 / "runs"
SOURCES = {"baseline": "archive/v1/notebooks/baseline.ipynb", "naive_bayes": "archive/v1/notebooks/Naive_Bayes.ipynb", "mlp": "archive/v1/notebooks/MLP.ipynb", "cnn": "archive/v1/notebooks/CNN.ipynb"}
PACKAGES = ["numpy", "pandas", "scikit-learn", "scipy", "matplotlib", "tensorflow", "keras", "ipykernel", "nbclient", "nbformat", "ipython", "pillow"]


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_json(path: Path, obj: object) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str), encoding="utf-8")


def environment() -> dict:
    expected = {"PYTHONHASHSEED": "5318", "TF_DETERMINISTIC_OPS": "1", "CUDA_VISIBLE_DEVICES": "-1",
                "OMP_NUM_THREADS": "4", "TF_NUM_INTRAOP_THREADS": "4", "TF_NUM_INTEROP_THREADS": "2",
                "KERAS_BACKEND": "tensorflow", "MPLBACKEND": "Agg"}
    return {
        "at": now(), "python": sys.version, "platform": platform.platform(), "machine": platform.machine(),
        "processor": platform.processor(), "cpu_count": os.cpu_count(),
        "packages": {p: version(p) for p in PACKAGES},
        "variables": {k: os.environ.get(k) for k in expected},
        "expected_variables_match": all(os.environ.get(k) == v for k, v in expected.items()),
        "pip_check": subprocess.run([sys.executable, "-m", "pip", "check"], capture_output=True, text=True).stdout,
        "pip_freeze": subprocess.check_output([sys.executable, "-m", "pip", "freeze"], text=True).splitlines(),
    }


def audit_cell(model: str) -> str:
    # Runs only after every original code cell. It reads existing variables and exports evidence.
    prefix = "from pathlib import Path\nimport os, json\nimport numpy as np\nfrom sklearn.metrics import *\n"
    prefix += "_v2_dir = Path(os.environ['V2_RUN_DIR'])\nnp.save(_v2_dir / 'y_test.npy', np.asarray(y_test).reshape(-1))\n"
    if model == "baseline":
        prefix += "\n".join([
            "for _v2_name, _v2_pred in final_predictions.items():",
            "    _v2_file = 'dummy_predictions.npy' if _v2_name == 'Most frequent' else 'nearest_centroid_predictions.npy'",
            "    np.save(_v2_dir / _v2_file, np.asarray(_v2_pred).reshape(-1))",
            "validation_results.to_csv(_v2_dir / 'validation_results.csv', index=False)",
            "baseline_test_results.to_csv(_v2_dir / 'notebook_final_results.csv', index=False)",
        ])
    elif model == "naive_bayes":
        prefix += "np.save(_v2_dir / 'gaussian_nb_predictions.npy', np.asarray(final_predictions).reshape(-1))\n"
        prefix += "search_results.to_csv(_v2_dir / 'search_results.csv', index=False)\n"
        prefix += "(_v2_dir / 'parameter_inventory.json').write_text(json.dumps({'theta': int(final_model.theta_.size), 'variance': int(final_model.var_.size), 'class_prior': int(final_model.class_prior_.size), 'stored_numeric_total': int(final_model.theta_.size + final_model.var_.size + final_model.class_prior_.size)}, indent=2), encoding='utf-8')\n"
    elif model == "mlp":
        prefix += "np.save(_v2_dir / 'mlp_predictions.npy', np.asarray(mlp_test_predictions).reshape(-1))\n"
        prefix += "if 'mlp_search_records' in globals(): pd.DataFrame(mlp_search_records).to_csv(_v2_dir / 'search_results.csv', index=False)\n"
    elif model == "cnn":
        prefix += "np.save(_v2_dir / 'cnn_predictions.npy', np.asarray(cnn_test_predictions).reshape(-1))\n"
        prefix += "if 'cnn_search_records' in globals(): pd.DataFrame(cnn_search_records).to_csv(_v2_dir / 'search_results.csv', index=False)\n"
    prefix += "\nprint('V2 audit export complete:', _v2_dir)\n"
    return prefix


def output_text(cell: dict) -> str:
    texts = []
    for output in cell.get("outputs", []):
        if "text" in output:
            texts.append("".join(output["text"]))
        if output.get("output_type") == "error":
            texts.append("\n".join(output.get("traceback", [])))
        data = output.get("data", {})
        if "text/plain" in data:
            texts.append("".join(data["text/plain"]))
    return "\n".join(texts)


def numeric_summary(run_dir: Path, model: str) -> dict:
    y_true_path = run_dir / "y_test.npy"
    if not y_true_path.exists():
        return {"status": "FAIL", "reason": "Audit export did not produce y_test.npy"}
    y_true = np.load(y_true_path, allow_pickle=False).reshape(-1)
    names = ["dummy", "nearest_centroid"] if model == "baseline" else ["gaussian_nb" if model == "naive_bayes" else model]
    results = {}
    for name in names:
        pred_path = run_dir / f"{name}_predictions.npy"
        if not pred_path.exists():
            results[name] = {"status": "FAIL", "reason": f"Missing {pred_path.name}"}
            continue
        pred = np.load(pred_path, allow_pickle=False).reshape(-1)
        if len(pred) != len(y_true):
            results[name] = {"status": "FAIL", "reason": "Prediction length differs from y_test"}
            continue
        labels = np.arange(9)
        results[name] = {
            "status": "PASS", "n_test": len(y_true), "predictions_sha256": sha256(pred_path),
            "accuracy": accuracy_score(y_true, pred),
            "macro_f1": f1_score(y_true, pred, labels=labels, average="macro", zero_division=0),
            "balanced_accuracy": balanced_accuracy_score(y_true, pred),
            "classification_report": classification_report(y_true, pred, labels=labels, output_dict=True, zero_division=0),
            "confusion_matrix": confusion_matrix(y_true, pred, labels=labels).tolist(),
        }
        np.savetxt(run_dir / f"{name}_confusion_matrix_verified.csv", results[name]["confusion_matrix"], delimiter=",", fmt="%d")
    return results


def run_one(model: str, final_only: bool = False) -> dict:
    source = ROOT / SOURCES[model]
    checks = json.loads((V2 / "reference" / "notebook_checksums.json").read_text(encoding="utf-8"))
    actual_hash = sha256(source)
    if actual_hash != checks["sha256"][Path(SOURCES[model]).name]:  # immutable historical key
        raise RuntimeError(f"Source notebook checksum changed: {source}")
    mode = "final_only" if final_only else "strict"
    run_dir = RUNS / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + model + "_" + mode + "_" + uuid.uuid4().hex[:8])
    run_dir.mkdir(parents=True, exist_ok=False)
    os.environ["V2_RUN_DIR"] = str(run_dir)
    os.environ["MLP_OUTPUT_DIR"] = str(run_dir)
    os.environ["CNN_OUTPUT_DIR"] = str(run_dir)
    env = environment()
    env.update({"model": model, "mode": mode, "source_notebook": SOURCES[model], "source_sha256": actual_hash,
                "source_commit": checks["commit"], "run_dir": str(run_dir)})
    write_json(run_dir / "environment_manifest.json", env)
    (run_dir / "pip-freeze.txt").write_text("\n".join(env["pip_freeze"]) + "\n", encoding="utf-8")
    nb = nbformat.read(source, as_version=4)
    for cell in nb.cells:
        if cell.cell_type == "code":
            cell.outputs = []
            cell.execution_count = None
    nb.metadata.kernelspec = {"name": "python3", "display_name": "Python 3 (V2 CPU)", "language": "python"}
    nb.metadata.reproduction_v2 = {"source": SOURCES[model], "source_sha256": actual_hash,
                                   "source_commit": checks["commit"], "mode": mode, "started_at": now(),
                                   "note": "Original source cells unchanged; final optional export cell is audit instrumentation."}
    copy = run_dir / "executed.ipynb"
    nbformat.write(nb, copy)
    started = time.monotonic()
    skip_cells = {"mlp": {18}, "cnn": {19}}.get(model, set()) if final_only else set()
    progress = {"model": model, "mode": mode, "started_at": now(), "source_sha256": actual_hash, "original_cells": len(nb.cells),
                "completed_original_code_cells": 0, "skipped_source_cells": sorted(skip_cells),
                "audit_cell_executed": False, "status": "RUNNING"}
    write_json(run_dir / "run_status.json", progress)
    with (run_dir / "execution.log").open("w", encoding="utf-8", buffering=1) as log:
        def record(message: str) -> None:
            line = f"[{now()}] {message}"
            print(line, flush=True)
            log.write(line + "\n")
        record(f"START {model}; source={source}; sha256={actual_hash}; original_cells={len(nb.cells)}")
        try:
            client = NotebookClient(nb, timeout=14400, kernel_name="python3", allow_errors=False,
                                    resources={"metadata": {"path": str(ROOT)}})
            with client.setup_kernel():
                for i, cell in enumerate(nb.cells):
                    if cell.cell_type != "code":
                        continue
                    if i in skip_cells:
                        record(f"SKIP source_cell={i} final_only mode")
                        continue
                    record(f"BEGIN source_cell={i}")
                    cell_start = time.monotonic()
                    client.execute_cell(cell, i)
                    record(f"END source_cell={i} seconds={time.monotonic()-cell_start:.3f} outputs={len(cell.outputs)}")
                    text = output_text(cell)
                    if text:
                        log.write(f"--- source cell {i} outputs ---\n{text}\n--- end cell {i} ---\n")
                    progress["completed_original_code_cells"] += 1
                    write_json(run_dir / "run_status.json", progress)
                    nbformat.write(nb, copy)
                audit = nbformat.v4.new_code_cell(audit_cell(model))
                audit.metadata["reproduction_v2_audit_only"] = True
                nb.cells.append(audit)
                record(f"BEGIN audit_export_cell={len(nb.cells)-1}")
                client.execute_cell(audit, len(nb.cells)-1)
                record(f"END audit_export_cell outputs={len(audit.outputs)}")
                progress["audit_cell_executed"] = True
                nbformat.write(nb, copy)
            progress["status"] = "PASS"
        except Exception as exc:
            progress["status"] = "FAIL"
            progress["error"] = {"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()}
            record(f"FAIL {type(exc).__name__}: {exc}\n{traceback.format_exc()}")
            nbformat.write(nb, copy)
        finally:
            progress["ended_at"] = now()
            progress["wall_seconds"] = time.monotonic() - started
            write_json(run_dir / "run_status.json", progress)
            if progress["status"] == "PASS":
                verified = numeric_summary(run_dir, model)
                write_json(run_dir / "verified_metrics.json", verified)
                if any(v.get("status") != "PASS" for v in verified.values()):
                    progress["status"] = "FAIL"
                    progress["error"] = {"message": "Independent prediction export or verification failed"}
                    write_json(run_dir / "run_status.json", progress)
            record(f"COMPLETE {model}: {progress['status']}; wall_seconds={progress['wall_seconds']:.3f}")
    return {"model": model, "run_dir": str(run_dir), "status": progress["status"]}


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true")
    group.add_argument("--model", choices=SOURCES)
    group.add_argument("--audit", action="store_true")
    parser.add_argument("--final-only", action="store_true", help="Skip only the expensive MLP/CNN search cell")
    args = parser.parse_args()
    if args.final_only and (not args.model or args.model not in ("mlp", "cnn")):
        parser.error("--final-only requires --model mlp or --model cnn")
    RUNS.mkdir(parents=True, exist_ok=True)
    if args.audit:
        from environment_audit import main as audit_main
        return audit_main()
    models = list(SOURCES) if args.all else [args.model]
    completed = []
    for model in models:
        try:
            completed.append(run_one(model, final_only=args.final_only))
        except Exception as exc:
            completed.append({"model": model, "status": "FAIL", "error": str(exc)})
            print(traceback.format_exc(), flush=True)
    write_json(RUNS / "latest_batch.json", {"at": now(), "runs": completed})
    return 0 if all(r["status"] == "PASS" for r in completed) else 1


if __name__ == "__main__":
    raise SystemExit(main())
