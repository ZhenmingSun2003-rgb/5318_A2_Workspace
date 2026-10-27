"""Render verified post-run plots from numeric artifacts, outside source notebooks."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path("/workspace/repo") if Path("/workspace/repo").is_dir() else Path(__file__).resolve().parents[2]
RUNS = ROOT / "reproduction_v2" / "runs"


def csv_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main() -> None:
    for directory in sorted(RUNS.iterdir()):
        if not directory.is_dir():
            continue
        state_path = directory / "run_status.json"
        if not state_path.exists():
            continue
        state = json.loads(state_path.read_text(encoding="utf-8"))
        if state.get("status") != "PASS":
            continue
        for path in directory.glob("*_confusion_matrix_verified.csv"):
            matrix = np.loadtxt(path, delimiter=",", dtype=int)
            fig, ax = plt.subplots(figsize=(8, 7))
            ax.imshow(matrix, cmap="Blues")
            for i in range(9):
                for j in range(9):
                    ax.text(j, i, str(matrix[i, j]), ha="center", va="center", fontsize=6)
            ax.set(xticks=np.arange(9), yticks=np.arange(9), xlabel="Predicted class", ylabel="True class",
                   title=path.stem.replace("_confusion_matrix_verified", "") + " verified test confusion")
            fig.tight_layout()
            fig.savefig(directory / path.name.replace(".csv", ".png"), dpi=160)
            plt.close(fig)
        search = csv_rows(directory / "search_results.csv")
        if search:
            x_key = "var_smoothing" if "var_smoothing" in search[0] else "trial_id"
            x = [float(r.get(x_key, i+1)) for i, r in enumerate(search)]
            y = [float(r["validation_macro_f1"]) for r in search]
            fig, ax = plt.subplots(figsize=(7, 4))
            ax.plot(x, y, marker="o")
            if x_key == "var_smoothing":
                ax.set_xscale("log")
            ax.set(xlabel=x_key, ylabel="Validation Macro-F1", title=state["model"] + " actual V2 search")
            fig.tight_layout()
            fig.savefig(directory / "v2_actual_search_macro_f1.png", dpi=160)
            plt.close(fig)
        baseline = csv_rows(directory / "validation_results.csv")
        if baseline:
            fig, ax = plt.subplots(figsize=(7, 4))
            ax.bar([r["model"] for r in baseline], [float(r["macro_f1"]) for r in baseline])
            ax.set(ylabel="Validation Macro-F1", title="Actual V2 baseline validation")
            ax.tick_params(axis="x", labelrotation=15)
            fig.tight_layout()
            fig.savefig(directory / "v2_actual_baseline_validation.png", dpi=160)
            plt.close(fig)
        print("Rendered diagnostics:", directory)


if __name__ == "__main__":
    main()
