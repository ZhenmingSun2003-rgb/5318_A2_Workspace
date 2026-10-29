# COMP5318/4318 Assignment 2 — Group 163 code package

PathMNIST tissue classification with two reference baselines (Dummy, Nearest Centroid) and three
assessed models (Gaussian Naive Bayes, MLP, CNN), including hyperparameter searches and independent
final models.

```
a2-submission/
├── a2-code-530210074-540868894-550220550-550574604.ipynb   # submitted notebook, all outputs preserved
├── a2-code-530210074-540868894-550220550-550574604.pdf     # PDF export of the executed notebook
├── report/                     # A2 report draft (PDF + Word; editable original is the Claude doc)
├── Assignment2Data/            # X_train.npy, y_train.npy, X_test.npy, y_test.npy (read via relative path)
├── environment/
│   ├── Dockerfile              # python:3.11.11-slim-bookworm, linux/amd64, CPU-only TensorFlow
│   ├── compose.yaml            # no network, read-only package mount, 4 CPUs / 10 GB
│   ├── requirements.txt        # top-level pins
│   ├── requirements-lock.txt   # every transitive pin (used by the Dockerfile)
│   └── run_notebook.py         # fresh-kernel execution + template/syntax checks
├── results/                    # CSVs, figures, environment log and HTML export from the preserved run
└── tools/eda_dashboard/        # optional Streamlit dashboard used for initial exploration
```

## Running

**Jupyter (simplest).** Open the notebook from this folder with a Python 3.11 kernel that has the
packages from `environment/requirements-lock.txt`, then *Run All*. The hyperparameter-search cells
are skipped by default (their outputs are preserved in the notebook and in `results/search_*.csv`);
all other cells, including the final models, run in a few minutes on a laptop CPU.
Set the environment variable `A2_RUN_TUNING=1` before starting Jupyter to re-run the searches
(≈ 10–20 min on 4 cores).

**Docker (controlled environment).** From this folder:

```bash
docker compose -f environment/compose.yaml build
docker compose -f environment/compose.yaml run --rm a2          # final models only
docker compose -f environment/compose.yaml run --rm a2 --tune   # also re-run all searches
```

On a host with fewer than 4 cores, lower `cpus:` in `compose.yaml` (thread counts are fixed
separately, so this does not change the numerics). The executed copy is written to `results/`.

## Reproducibility

Data files are checked against SHA-256 hashes, the validation split is fingerprinted, all seeds are
fixed (`5318`), TensorFlow runs CPU-only with deterministic ops, and the full dependency tree is
pinned. Under these controls GaussianNB and both baselines give bit-identical results on every
machine we tried. **The MLP and CNN can still differ slightly across CPU models and OS platforms**,
because different processors execute the same floating-point reductions in different orders
(e.g. AVX2 vs AVX-512 vs ARM kernels) and gradient descent amplifies those last-bit differences.
The notebook logs the CPU model and SIMD flags of each run and documents the spread we observed.

## Preserved run

The outputs in the submitted notebook come from one fresh-kernel execution with tuning
(`run_notebook.py --tune`, 930 s) on a 2-core Intel Xeon (AVX-512), Python 3.11.11 with the lock file.
A second complete execution on the same machine reproduced every metric exactly, and a fresh run with
tuning skipped and an empty `results/` folder passed in 176 s with identical test metrics.

| Model | Test accuracy | Test Macro-F1 |
|---|---|---|
| Dummy | 0.1468 | 0.0284 |
| Nearest Centroid | 0.4303 | 0.4105 |
| GaussianNB | 0.4155 | 0.3857 |
| MLP | 0.4849 | 0.4432 |
| CNN | 0.7080 | 0.6831 |

Before submission: each member writes their own Reflection in the report, the group confirms the
AI acknowledgement, and the three Canvas files are the notebook (.ipynb), its PDF, and the report PDF.
