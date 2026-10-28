# COMP5318 A2 — V3 Integration Workspace

The repository is in **V3 Final Integration**. The active complete English integrated notebook and reproducible V2-compatible Docker package are located in [integration_v3/](integration_v3/). The Canvas original data and instruction/template remain unchanged.

## Workspace

```text
Canvas Sources/                      Original Canvas PDF/template and four NPY files (read only)
archive/v1/notebooks/                Owner GaussianNB, MLP, CNN, plus reference baselines (immutable)
archive/v1/eda_lab/                  Archived Streamlit exploratory visualisation
reproduction_v2/                     Frozen V2 Docker logs, verified metrics, search outputs and audits
integration_v3/
  COMP5318_A2_Integrated.ipynb       Unified Canvas five-section Notebook
  Dockerfile                         V2-resolved Python 3.11.11 / TensorFlow 2.17.1 CPU
  compose.yaml                       Offline; read-only code/data; writable outputs
  scripts/run_v3.py                  Static structure check / isolated fresh-kernel execution
  README.md                          Full instructions and provenance
```

Three assessed models: Gaussian Naive Bayes, MLP and CNN. Two extra diagnostics: Dummy and Nearest Centroid. The original Canvas split remains 32,000 train and 8,000 test; within train, seed 5318 gives 25,600 fit / 6,400 validation. V2 frozen-model Test Macro-F1 evidence: GaussianNB 0.385748; MLP 0.438672; CNN 0.723255. New V3 Notebook scores are **fresh** outputs generated only by executing V3.

**Read first:** [V3 README](integration_v3/README.md), [V2 reproduction audit](reproduction_v2/reports/04_final_reproduction_summary.md), [V1–V2 difference analysis](reproduction_v2/reports/05_difference_analysis.md), [V1 archive](archive/v1/README.md).

## Docker

```bash
docker compose -f integration_v3/compose.yaml build --pull
docker compose -f integration_v3/compose.yaml run --rm integrate --validate
docker compose -f integration_v3/compose.yaml run --rm integrate --execute
# optional search rerun (8 GaussianNB + 8 MLP + 8 CNN trials)
docker compose -f integration_v3/compose.yaml run --rm integrate --execute --tune
```

Outputs are stored under the Git-ignored `integration_v3/outputs/` directory, including the executed Notebook and a verified five-model summary. The Docker image uses the full exact V2 *resolved* package list and the same CPU deterministic environment. Cross-platform floating-point differences can still change neural-network weights and scores.

## Provenance and submission

The V2 measured validation search optimum for the MLP/CNN occurred at epochs 9/12, whereas V2 strict final fits reproduced the original V1-frozen epochs 10/11. V3 deliberately preserves the frozen final protocol rather than silently tuning after inspecting test results. Every displayed table distinguishes current-run V3 numbers from archived V2 results. The report, Notebook PDF, AI Acknowledgement and individual reflections require final group review against the original Canvas PDF.
