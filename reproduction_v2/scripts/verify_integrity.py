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
    changed = []
    for name, expected in MANIFEST["sha256"].items():
        if name == "README.md":
            continue
        file = ROOT / name
        actual = digest(file) if file.is_file() else None
        if actual != expected:
            changed.append({"path": name, "expected": expected, "actual": actual})
    status = git("status", "--short")
    untracked = [name for name in git("ls-files", "--others", "--exclude-standard").splitlines() if name]
    stat = git("diff", "--stat")
    readme_diff = git("diff", "--", "README.md")
    disallowed = []
    for line in status.splitlines():
        path = line[3:]
        if path != "README.md" and path.rstrip("/") != "reproduction_v2" and not path.startswith("reproduction_v2/"):
            disallowed.append(line)
    source_is_ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", MANIFEST["commit"], "HEAD"],
        cwd=ROOT, check=False,
    ).returncode == 0
    result = {"at": datetime.now(timezone.utc).isoformat(), "source_commit": MANIFEST["commit"],
              "head": git("rev-parse", "HEAD").strip(), "source_is_ancestor": source_is_ancestor,
              "checked_original_files": len(MANIFEST["sha256"])-1,
              "changed_original_files": changed, "disallowed_git_status": disallowed,
              "git_status_short": status, "git_diff_stat": stat, "git_diff_readme": readme_diff,
              "new_untracked_files": untracked,
              "pass": not changed and not disallowed and all(name.startswith("reproduction_v2/") for name in untracked)
                      and source_is_ancestor}
    (V2 / "reports" / "integrity_verification.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("head", "checked_original_files", "changed_original_files", "disallowed_git_status", "pass")}, indent=2))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
