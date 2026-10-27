"""Read-only environment, raw data, split, and exact-duplicate audit."""
from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

import numpy as np
from sklearn.model_selection import train_test_split

ROOT = Path("/workspace/repo") if Path("/workspace/repo").exists() else Path(__file__).resolve().parents[2]
OUT = ROOT / "reproduction_v2" / "runs"
DATA = ROOT / "Canvas Sources" / "Assignment2Data-1" / "Assignment2Data"
EXPECTED = {
    "numpy": "1.26.4", "pandas": "2.2.3", "scikit-learn": "1.5.2", "scipy": "1.14.1",
    "matplotlib": "3.9.2", "tensorflow": "2.17.1", "keras": "3.6.0",
    "ipykernel": "6.29.5", "nbclient": "0.10.2", "nbformat": "5.10.4",
    "ipython": "8.30.0", "pillow": "10.4.0",
}
INDEX_HASHES = {
    "fit": "191d1629061294ebe7e01fe7a79ac57739fced43795161a0c6b821241311c571",
    "validation": "c07d9573b52ee95cb6bd73390fde64f9c2dccd1c2ab14c244a479b1aa0dd3718",
}


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sample_hashes(array: np.ndarray) -> set[bytes]:
    return {hashlib.sha256(array[i].tobytes()).digest() for i in range(len(array))}


def cgroup_value(name: str) -> str | None:
    path = Path("/sys/fs/cgroup") / name
    return path.read_text(encoding="utf-8").strip() if path.is_file() else None


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    arrays = {name: np.load(DATA / f"{name}.npy", mmap_mode="r", allow_pickle=False)
              for name in ("X_train", "X_test", "y_train", "y_test")}
    y_train = arrays["y_train"].reshape(-1).astype(int)
    y_test = arrays["y_test"].reshape(-1).astype(int)
    fit, val = train_test_split(np.arange(len(y_train)), test_size=.20, stratify=y_train, random_state=5318)
    fit_hash = hashlib.sha256(fit.astype("<i8").tobytes()).hexdigest()
    val_hash = hashlib.sha256(val.astype("<i8").tobytes()).hexdigest()
    train_samples = sample_hashes(arrays["X_train"])
    test_samples = sample_hashes(arrays["X_test"])
    packages = {name: version(name) for name in EXPECTED}
    pip = subprocess.run([sys.executable, "-m", "pip", "check"], capture_output=True, text=True)
    try:
        import tensorflow as tf
        tf_info = {"version": tf.__version__, "physical_devices": [x.name for x in tf.config.list_physical_devices()],
                   "build_info": tf.sysconfig.get_build_info()}
    except Exception as exc:
        tf_info = {"error": repr(exc)}
    report = {
        "at": datetime.now(timezone.utc).isoformat(), "platform": platform.platform(),
        "machine": platform.machine(), "python": platform.python_version(), "cpu_count": os.cpu_count(),
        "cgroup_cpu_max": cgroup_value("cpu.max"), "cgroup_memory_max": cgroup_value("memory.max"),
        "packages": packages, "expected_packages_match": all(packages[k] == v for k, v in EXPECTED.items()),
        "pip_check": {"returncode": pip.returncode, "stdout": pip.stdout, "stderr": pip.stderr},
        "tensorflow": tf_info,
        "environment_variables": {k: os.environ.get(k) for k in ("PYTHONHASHSEED", "TF_DETERMINISTIC_OPS", "CUDA_VISIBLE_DEVICES", "OMP_NUM_THREADS", "TF_NUM_INTRAOP_THREADS", "TF_NUM_INTEROP_THREADS", "KERAS_BACKEND", "MPLBACKEND")},
        "data": {name: {"path": str(DATA / f"{name}.npy"), "sha256": file_hash(DATA / f"{name}.npy"),
                        "shape": list(value.shape), "dtype": str(value.dtype), "min": int(np.min(value)),
                        "max": int(np.max(value))}
                 for name, value in arrays.items()},
        "classes_train": np.unique(y_train).tolist(), "classes_test": np.unique(y_test).tolist(),
        "split": {"fit_count": len(fit), "validation_count": len(val), "test_count": len(y_test),
                  "fit_indices_sha256": fit_hash, "validation_indices_sha256": val_hash,
                  "fingerprints_match_v1": fit_hash == INDEX_HASHES["fit"] and val_hash == INDEX_HASHES["validation"],
                  "fit_validation_disjoint": len(set(fit).intersection(val)) == 0},
        "exact_image_duplicate_counts": {"train_unique": len(train_samples), "test_unique": len(test_samples),
                                         "cross_partition_unique_image_hashes": len(train_samples & test_samples)},
    }
    output = OUT / "data_environment_audit.json"
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(json.dumps({"audit_path": str(output), "expected_packages_match": report["expected_packages_match"],
                      "pip_check": pip.returncode, "split": report["split"],
                      "exact_duplicates": report["exact_image_duplicate_counts"]}, indent=2))
    return 0 if report["expected_packages_match"] and pip.returncode == 0 and report["split"]["fingerprints_match_v1"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
