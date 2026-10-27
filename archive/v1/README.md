# V1 archived development material

The existing V1 notebooks and their saved execution outputs were moved without
changing their bytes, so the repository root can serve V3 integration.

| Item | New location |
|---|---|
| Original English notebooks | [notebooks/](notebooks/) |
| Chinese Baseline | [notebooks_zh/](notebooks_zh/) |
| EDA tool | [eda_lab/](eda_lab/) |
| Original V1 Conda environment | [requirements.yaml](requirements.yaml) |
| EDA / Baseline helpers | [scripts/](scripts/) |
| Pre-migration root README, preserved unchanged | [README_legacy.md](README_legacy.md) |

The Canvas source arrays **stay at repository root**. V1 Notebook data loaders
resolve them through parent directories. EDA and helper script paths have been
adapted for the archive layout.

From the repository root:

```bash
conda env create -f archive/v1/requirements.yaml
conda activate comp5318-a2
streamlit run archive/v1/eda_lab/app.py
python archive/v1/scripts/smoke_eda.py
python archive/v1/scripts/execute_baseline.py
```

Archived Baseline validation writes new executed notebooks to a temporary
directory (or `V1_BASELINE_OUTPUT_DIR`); it does not overwrite archived notebooks.
The archival GitHub Actions workflows stay under `.github/workflows/`.

**V2 historical integrity:** `reproduction_v2/reference/notebook_checksums.json`
preserves file keys at their original locations. The V2 runner maps new Notebook
paths back to those historical checksum keys; V2 snapshots, reports and results
are not modified to conceal their original run provenance.

Return to the [V3 landing page](../../README.md).
