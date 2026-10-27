# V2 executed results

Source commit: `0f2ffeaa118a82a39f4d2585ceca6e1d691e5036`. Docker image ID: `sha256:71253f48695fa0d9149b4f762b0dd242dfc332cc682eddaeaa2931d95831f11e`.

`strict_*` contains the four complete original Notebook executions (five models), including logs, executed copies, actual search records, final results, saved test predictions, independent metric JSON, numeric confusion matrices and selected plots. `final_only_*` contains the MLP/CNN controls that skipped only the search Cell. `interrupted_1` preserves the user-acknowledged Docker Desktop restart log.

Large model weights, probability arrays, temporary caches and duplicate Canvas data are excluded. `manifest.json` lists each copied evidence file with its SHA-256 and originating local run; `package_verification.json` checks that the copied predictions reproduce the recorded test metrics. See `../reports/04_final_reproduction_summary.md` and `../reports/05_difference_analysis.md` for conclusions.
