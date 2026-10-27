"""Verify every originally tracked file except README against the clone snapshot."""
from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / "reproduction_v2"
MANIFEST = json.loads((V2 / "reference" / "notebook_checksums.json").read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True, encoding="utf-8")


def main() -> int:
    # Historical immutable sources are verified at relocated paths.
    archived = {
        **{name: "archive/v1/notebooks/" + name for name in
           ("baseline.ipynb", "Naive_Bayes.ipynb", "MLP.ipynb", "CNN.ipynb")},
        "notebooks_zh/baseline_中文版.ipynb": "archive/v1/notebooks_zh/baseline_中文版.ipynb",
        "requirements.yaml": "archive/v1/requirements.yaml",
        "README.md": "archive/v1/README_legacy.md",
    }
    adapted_helpers = {
        "eda_lab/app.py", "eda_lab/README.md",
        "scripts/execute_baseline.py", "scripts/smoke_eda.py",
        ".github/workflows/eda_smoke.yml", ".github/workflows/run_baseline.yml",
    }
    changed = []
    for original, expected in MANIFEST["sha256"].items():
        if original in adapted_helpers:
            continue
        path = ROOT / archived.get(original, original)
        actual = digest(path) if path.is_file() else None
        if actual != expected:
            changed.append({"original": original, "current": str(path),
                            "expected": expected, "actual": actual})
    status = git("status", "--short")
    source_is_ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", MANIFEST["commit"], "HEAD"],
        cwd=ROOT, check=False,
    ).returncode == 0
    result = {
        "at": datetime.now(timezone.utc).isoformat(),
        "source_commit": MANIFEST["commit"],
        "head": git("rev-parse", "HEAD").strip(),
        "source_is_ancestor": source_is_ancestor,
        "checked_immutable_original_files": len(MANIFEST["sha256"]) - len(adapted_helpers),
        "changed_immutable_original_files": changed,
        "intentionally_adapted_helpers": sorted(adapted_helpers),
        "git_status_short": status,
        "pass": not changed and source_is_ancestor and not status.strip(),
    }
    path = V2 / "runs" / "relocation_integrity_verification.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("head", "checked_immutable_original_files",
                                            "changed_immutable_original_files", "pass")}, indent=2))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
