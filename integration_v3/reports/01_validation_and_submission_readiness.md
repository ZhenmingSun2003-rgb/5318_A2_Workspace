# V3 Integration — executed validation and Canvas compliance audit
**Date:** 2026-10-28. **Source:** GitHub Actions Docker CPU fresh-kernel executions. 
The repository's V1 original Notebook sources, V2 evidence and Canvas data were not modified.

## Controlled implementation check
- Environment: `linux/amd64` `python:3.11.11-slim-bookworm`, full pinned V2 package resolution, TensorFlow 2.17.1, Keras 3.6.0, NumPy 1.26.4, sklearn 1.5.2; deterministic TensorFlow operations, CPU-only, 4 CPU quota, 10 GB memory, network disabled.
- Exact V2 split SHA-256 checks passed (fit `191d1629061294ebe7e01fe7a79ac57739fced43795161a0c6b821241311c571`; validation `c07d9573b52ee95cb6bd73390fde64f9c2dccd1c2ab14c244a479b1aa0dd3718`), and train 32,000 / fit 25,600 / validation 6,400 / test 8,000.
- The original V1 selected hyperparameter combinations and epoch budgets are frozen. GaussianNB: `var_smoothing=1e-6`; MLP: `hidden_units=256, learning_rate=0.001, dropout_rate=0, epochs=10`; CNN: `base_filters=16, learning_rate=0.001, dropout_rate=0.3, epochs=11`. Original architectures and training code from owners used.
- V3 search grid output defaults to archived **V2 actual search results** clearly marked historical; optional searches can be run with `--tune`; final models run independently of the search.
- `summary.json`, actual test prediction metrics, per-class scores, confusion matrices, new prediction files and plots computed in the V3 run. Historical test metrics displayed only as separately identified comparison evidence.

## Real Docker executions (success)
- [CI 1: complete build and all models trained — 2026-10-28](https://github.com/ZhenmingSun2003-rgb/5318_A2_Workspace/actions/runs/40624341311) — PASS, evidence uploaded.
- [CI 2: improved standalone fallback source — 2026-10-28](https://github.com/ZhenmingSun2003-rgb/5318_A2_Workspace/actions/runs/40624494612) — PASS, evidence uploaded.
- CI 1/2 model predictions and scores were **identical**, but were not universally stable across **all** CI runs. Runtime seconds differed.
- [CI 3: final embedded-figure Notebook on the same pinned container](https://github.com/ZhenmingSun2003-rgb/5318_A2_Workspace/actions/runs/40625793593) — **PASS**; preserved 7 newly generated PNG figures in the Notebook outputs and checked this in CI. All **five final metrics exactly matched V2** at available precision (CNN Macro-F1 0.723255; MLP 0.438672). The original V1/V2 model source and frozen parameters are unchanged.
- CI runner platform in `summary.json`: `Linux-7.0.0-1017-azure-x86_64-with-glibc2.36` (GitHub Actions virtual CPU), which differs from the V2 machine.

| Model | V2 strict Test Accuracy | V3 CI runs #1/#2 Accuracy | V2 strict Macro-F1 | V3 CI runs #1/#2 Macro-F1 | #1/#2 minus V2 |
|---|---:|---:|---:|---:|---:|
| Dummy | 0.146750 | 0.146750 | 0.028438 | 0.028438 | 0.000000 |
| Nearest Centroid | 0.430250 | 0.430250 | 0.410469 | 0.410469 | 0.000000 |
| GaussianNB | 0.415500 | 0.415500 | 0.385748 | 0.385748 | 0.000000 |
| MLP | 0.489250 | 0.484875 | 0.438672 | 0.443158 | +0.004485 |
| CNN | 0.739250 | 0.708000 | 0.723255 | 0.683125 | −0.040131 |

**Evidence interpretation:** runs #1/#2 were stable and consistently differed from V2 on neural-network results, while run #3 gave exactly V2 metrics. All three had the **same declared pinned library versions**, seed, split fingerprints and generic platform string, but significantly different CPU fitting times (CNN 15.6s / 22.7s / 71.3s respectively). No per-run microarchitecture/instruction-set manifest was captured, so the exact source of the observed differences is **not proven**. Hardware-specific CPU/oneDNN numerical paths are one plausible explanation. Do not claim identical metrics are guaranteed on other machines and do not force agreement by tuning on the held-out test set.

**Most recent verified V3 run #3** (fresh fit and test prediction; *not* the V2 archival values substituted for current results):

| Model | V3 CI #3 Accuracy | V3 CI #3 Macro-F1 | Difference to V2 Macro-F1 |
|---|---:|---:|---:|
| Dummy | 0.146750 | 0.028438 | 0.000000 |
| Nearest Centroid | 0.430250 | 0.410469 | 0.000000 |
| GaussianNB | 0.415500 | 0.385748 | 0.000000 |
| MLP | 0.489250 | 0.438672 | 0.000000 |
| CNN | 0.739250 | 0.723255 | 0.000000 |

## Canvas PDF checklist
Reviewed `Canvas Sources/COMP5318-assignment2-Sem2-2026-2.pdf` (12 pages) and `COMP5318-assignment2-template-notebook-1.ipynb`.
- Task 1: data exploration, preprocessing, one first-six-weeks algorithm, MLP and CNN; all present.
- Task 2: genuine parameter search and runtime evidence, at least **3 different hyperparameters** each for MLP and CNN; eight-trial full-factorial search implementations and archived true V2 measured tables present.
- Final models trained independently of search; running fresh kernel without parameter search succeeded in CI.
- Canvas Notebook five-section order preserved, AI declaration present and should be group-reviewed.
- The **assignment submission** further requires a report PDF, `.ipynb` with preserved code outputs and its PDF export, plus each member's reflection in the report. The current V3 package is **code integration + reproducibility deliverable**, not the complete report submission.
- Canvas deadline: Friday **2026-10-30 23:59** (check Canvas for any updates).

## Release acceptance
- [x] Valid Canvas five-section integrated Notebook
- [x] GaussianNB / MLP / CNN final frozen fits and both fixed reference baselines
- [x] V2 pinned complete dependency list and reproducible offline CPU build
- [x] Five current-run test predictions and independent metrics validated
- [x] No errors in executed Notebook; all 7 plot images embedded directly into the executed Notebook and uploaded with CI evidence
- [x] Baseline and GaussianNB match V2 on all three runs; neural-network drift in runs #1/#2 and perfect V2 agreement in run #3 both transparently documented
- [ ] Group final review of SID identities, original model interpretations, AI declaration and individual reflections
- [ ] Formal report PDF finalisation and submission via Canvas
