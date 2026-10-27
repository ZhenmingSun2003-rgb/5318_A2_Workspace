# V2 controlled reproduction

Source commit and original SHA-256 values are in `reference/notebook_checksums.json`.
The repository is mounted read-only inside the container. Each run writes to a new
directory under `runs/` and starts a fresh `python3` kernel.

```powershell
docker compose -f reproduction_v2/compose.yaml build --pull
docker compose -f reproduction_v2/compose.yaml run --rm reproduce --audit
docker compose -f reproduction_v2/compose.yaml run --rm reproduce --all
```

Run from the repository root. `--audit` checks environment and source data without
training. `--model baseline|naive_bayes|mlp|cnn` runs one Notebook. The run directory
contains a copy of the executed notebook, logs, predictions, and summaries. The
notebook source is never edited. A clearly marked audit-only cell can be added to
the *execution copy* after the original cells finish to export in-memory predictions.

The strict run uses all original code cells, including search cells. Model selection
constants in the final cells remain frozen to V1 choices. V2 search records are
reported separately from the main final-model comparison.

To check that the frozen final model can run without its search cell:

```powershell
docker compose -f reproduction_v2/compose.yaml run --rm reproduce --model mlp --final-only
docker compose -f reproduction_v2/compose.yaml run --rm reproduce --model cnn --final-only
python reproduction_v2/scripts/compare_results.py
python reproduction_v2/scripts/analyze_differences.py
```

The `final_only` runs are separately marked and excluded from the strict main
comparison. See `reports/05_difference_analysis.md` for the controlled check.
