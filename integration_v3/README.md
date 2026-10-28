# COMP5318 A2 — V3 Final Integration

## What is here

- **COMP5318_A2_Integrated.ipynb** — one English Notebook in the exact five-section Canvas-template order, with GaussianNB + MLP + CNN (required) and Dummy + Nearest Centroid (reference-only). Group number 163 and the four IDs from the GaussianNB owner file are included for team verification.
- **Dockerfile / compose.yaml** — image based on the same `python:3.11.11-slim-bookworm`, `linux/amd64`, TensorFlow 2.17.1 / Keras 3.6.0 CPU determinism and limited thread counts used by V2. Pip installs the V2 **complete resolved package version snapshot**, `reproduction_v2/reference/requirements-v2-resolved.txt`, not a floating new dependency tree.
- **scripts/run_v3.py** — static validation and fresh-kernel Notebook execution. All outputs write to `outputs/`; source data, original member Notebooks and V2 audit artifacts remain read-only.

The V3 notebook uses source code cells from `archive/v1/notebooks/Naive_Bayes.ipynb`, `MLP.ipynb`, and `CNN.ipynb`, retaining their model architectures and frozen choices. The common data loading, 25,600/6,400 validation split, fixed RGB scaling, final baseline comparison, independent metrics, provenance, and plots are integrated once.

## Reproduce from the repository root

```bash
docker compose -f integration_v3/compose.yaml build --pull
docker compose -f integration_v3/compose.yaml run --rm integrate --validate
docker compose -f integration_v3/compose.yaml run --rm integrate --execute
```

Default is **final-only**, using V2's actually executed search CSVs as *archived tuning evidence*. The current Notebook **always trains the three required final models afresh** and evaluates predictions; it never copies historical V2 test predictions or scores as its own. For an optional expensive controlled search first:

```bash
docker compose -f integration_v3/compose.yaml run --rm integrate --execute --tune
```

In Jupyter, open the Notebook from the repository root with the same image/kernel. Set `V3_OUTPUT_DIR` to a writable directory and `V3_RUN_TUNING=1` only if rerunning all search grids. Tuning is not a dependency of final-model cells. The Docker container has **no network access**, mounts the repository **read-only**, and writes to `integration_v3/outputs`. Avoid running two containers into one output folder at once. All generated weights, predictions and executed notebooks are ignored by Git.

## Experimental audit and provenance

| Model | V2 frozen Test Macro-F1 | V2 search best epoch | Frozen final epoch |
|---|---:|---:|---:|
| Dummy | 0.028438 | not tuned | n/a |
| Nearest Centroid | 0.410469 | not tuned | n/a |
| GaussianNB | 0.385748 | n/a | n/a |
| MLP | 0.438672 | **9** | **10** |
| CNN | 0.723255 | **12** | **11** |

V2 frozen final epochs are inherited from V1, **not** updated to V2 search winners. The V2 search best *configurations* were unchanged. This is deliberate: V3 preserves the controlled final protocol that was strictly reproduced in V2. Changing the epoch to a new search winner would be a distinct experiment requiring explicit annotation, not an invisible integration edit. Validation summaries clearly label whether they came from V2 archived CSVs or a fresh `--tune` execution. V1 hard-coded validation plotting records are **not** used as V2 evidence.

Each execution exports `summary.json`, `model_comparison.csv`, `per_class_scores.csv`, `v3_vs_v2_historical.csv`, `epoch_provenance.csv`, classification reports, confusion matrices, current-run predictions and charts, environment manifest and executed Notebook, alongside a `run_status.json`. If something fails, `executed_partial.ipynb` and the run status preserve available evidence.

**Interpretation cautions:** numerical equality across CPUs/OS is not guaranteed by Docker; V2 already observed material MLP/CNN differences from V1 and did not isolate one cause. CPU timing is machine-specific. Image-level split does not prove patient/slide independence. Original Canvas subset is not the entire public PathMNIST dataset, and model outputs are not clinical diagnoses.

## Submission checklist

The group should confirm the four SIDs, rerun the full notebook and inspect each chart, complete individual Reflection(s), and review the AI Acknowledgement. The original Canvas assignment PDF and Notebook template remain the authority for submission filenames, report and Notebook PDF requirements. This repository's V3 Docker package is a **reproduction/development deliverable**, not an assertion that the entire Canvas submission is already ready. Existing V1/V2 sources and evidence are not modified.
