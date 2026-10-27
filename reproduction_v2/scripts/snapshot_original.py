"""Read-only V1 snapshot. Run before any V2 model training."""
from __future__ import annotations

import ast
import hashlib
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reproduction_v2"
NAMES = ["baseline.ipynb", "Naive_Bayes.ipynb", "MLP.ipynb", "CNN.ipynb"]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True, encoding="utf-8").strip()


def output_text(cell: dict) -> list[dict]:
    result = []
    for j, output in enumerate(cell.get("outputs", [])):
        parts = []
        if "text" in output:
            parts.append("".join(output["text"]))
        if "text/plain" in output.get("data", {}):
            parts.append("".join(output["data"]["text/plain"]))
        if output.get("output_type") == "error":
            parts.append("\n".join(output.get("traceback", [])))
        if parts:
            result.append({"output_index": j, "type": output.get("output_type"), "text": "\n".join(parts)})
    return result


def find_number(text: str, key: str) -> float | None:
    match = re.search(rf"{re.escape(key)}\s*[: ]\s*([0-9]+(?:\.[0-9]+)?)", text, re.I)
    return float(match.group(1)) if match else None


def table_number(text: str, key: str) -> float | None:
    match = re.search(rf"^{re.escape(key)}\s+([0-9]+(?:\.[0-9]+)?)\s*$", text, re.M)
    return float(match.group(1)) if match else None


def parse_classification_report(text: str) -> dict:
    parsed = {}
    pattern = re.compile(r"^\s*(.*?)\s+([0-9]+\.[0-9]+)\s+([0-9]+\.[0-9]+)\s+([0-9]+\.[0-9]+)\s+([0-9]+(?:\.0+)?)\s*$")
    for line in text.splitlines():
        match = pattern.match(line)
        if not match:
            continue
        name = match.group(1).strip()
        if not name or name in {"macro avg", "weighted avg", "accuracy"}:
            continue
        parsed[name] = {"precision": float(match.group(2)), "recall": float(match.group(3)),
                        "f1": float(match.group(4)), "support": int(float(match.group(5)))}
    return parsed


def literal_assignments(source: str, names: set[str]) -> dict:
    found = {}
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return found
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in names:
                    try:
                        found[target.id] = ast.literal_eval(node.value)
                    except (ValueError, TypeError):
                        pass
    return found


def main() -> None:
    (OUT / "reference").mkdir(parents=True, exist_ok=True)
    (OUT / "reports").mkdir(parents=True, exist_ok=True)
    manifest_path = OUT / "reference" / "notebook_checksums.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if "git_status_porcelain_before_v2" in manifest:
            manifest["git_status_porcelain_at_snapshot"] = manifest.pop("git_status_porcelain_before_v2")
        checksums = manifest["sha256"]
        relocated = {
            **{name: "archive/v1/notebooks/" + name for name in NAMES},
            "notebooks_zh/baseline_中文版.ipynb": "archive/v1/notebooks_zh/baseline_中文版.ipynb",
            "requirements.yaml": "archive/v1/requirements.yaml",
            "README.md": "archive/v1/README_legacy.md",
        }
        changed_helpers = {
            "eda_lab/app.py", "eda_lab/README.md",
            "scripts/execute_baseline.py", "scripts/smoke_eda.py",
            ".github/workflows/eda_smoke.yml", ".github/workflows/run_baseline.yml",
        }
        for name, expected in checksums.items():
            if name in changed_helpers:
                continue  # Intentionally adapted for archive relocation.
            path = ROOT / relocated.get(name, name)
            if not path.is_file() or sha256(path) != expected:
                raise RuntimeError(f"Historical V1 source checksum mismatch: {name} => {path}")
        print("Verified historical V1 source files after relocation; snapshot outputs left unchanged.")
        return
    else:
        raise FileNotFoundError("Historical V1 reference manifest missing; refusing to fabricate a new V1 snapshot.")
    manifest["clone_reflog_event"] = git("reflog", "show", "--date=iso", "--format=%gd %gs", "-1")
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    clone_time = manifest["snapshot_at"]

    all_results = {"commit": manifest["commit"], "snapshot_at": clone_time, "notebooks": {}}
    environments = {"commit": manifest["commit"], "notebooks": {}}
    report = [
        "# 00 复现前 V1 审计", "",
        f"- 读取时间：{clone_time}", f"- HEAD：`{manifest['commit']}`（`{manifest['branch']}`）",
        f"- Clone reflog：`{manifest['clone_reflog_event']}`。",
        f"- 远程：`{manifest['remote']}`", "- 仅解析克隆时保存的 Notebook；此阶段没有训练或重新执行。", "",
        "## 证据类别", "",
        "A = 代码 Cell 保存的实际输出；B = Markdown 叙述；C = 源码中硬编码的历史记录；D = 原文件无法核实。A 也只能证明历史执行记录，不证明 V2 执行。", "",
    ]
    for name in NAMES:
        nb = json.loads((ROOT / name).read_text(encoding="utf-8"))
        cells = nb["cells"]
        code_cells = [(i, c) for i, c in enumerate(cells) if c["cell_type"] == "code"]
        errors = [{"cell": i, "output": j, "ename": o.get("ename"), "evalue": o.get("evalue")}
                  for i, c in code_cells for j, o in enumerate(c.get("outputs", [])) if o.get("output_type") == "error"]
        saved = {str(i): output_text(c) for i, c in code_cells}
        source = {str(i): "".join(c.get("source", [])) for i, c in code_cells}
        row = {
            "sha256": checksums[name], "code_cells": len(code_cells),
            "executed_code_cells": sum(c.get("execution_count") is not None for _, c in code_cells),
            "error_outputs": errors, "saved_text_outputs_by_cell": saved,
            "saved_image_count_by_cell": {str(i): sum("image/png" in o.get("data", {}) for o in c.get("outputs", [])) for i, c in code_cells},
            "metrics": {}, "metric_evidence": {}, "missing_or_unverified": [],
        }
        def evidence(cell: int) -> str:
            return f"A: {name} Cell {cell} 保存输出"
        if name == "baseline.ipynb":
            val = "\n".join(x["text"] for x in saved["22"])
            final = "\n".join(x["text"] for x in saved["29"])
            val_first, val_times = val.split("fit_seconds", 1)
            final_first, final_rest = final.split("frozen_parameters", 1)
            final_scores, final_rest = final_rest.split("balanced_accuracy", 1)
            final_times, _ = final_rest.split("test_samples", 1)
            name_by_index = {}
            for match in re.finditer(r"(?m)^\s*([01])\s+(Nearest centroid \(RGB pixels\)|Most frequent)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s*$", val_first):
                index, model_name = int(match.group(1)), match.group(2)
                model_id = "nearest_centroid" if model_name.startswith("Nearest") else "dummy"
                name_by_index[index] = model_id
                row["metrics"][model_id] = {"validation_accuracy": float(match.group(3)),
                                            "validation_macro_f1": float(match.group(4)),
                                            "validation_balanced_accuracy": float(match.group(5))}
                row["metric_evidence"][model_id] = {"validation": evidence(22), "test": evidence(29)}
            if len(name_by_index) != 2:
                raise ValueError("Could not parse both saved baseline validation rows")
            final_name_by_index = {}
            for match in re.finditer(r"(?m)^\s*([01])\s+(Nearest centroid \(RGB pixels\)|Most frequent)\s*$", final_first):
                final_name_by_index[int(match.group(1))] = "nearest_centroid" if match.group(2).startswith("Nearest") else "dummy"
            for match in re.finditer(r"(?m)^\s*([01])\s+.+?\s+([0-9.]+)\s+([0-9.]+)\s*$", final_scores):
                model_id = final_name_by_index[int(match.group(1))]
                row["metrics"][model_id].update(test_accuracy=float(match.group(2)), test_macro_f1=float(match.group(3)))
            for match in re.finditer(r"(?m)^\s*([01])\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+32000\s*$", final_times):
                model_id = final_name_by_index[int(match.group(1))]
                row["metrics"][model_id].update(test_balanced_accuracy=float(match.group(2)),
                    fit_seconds=float(match.group(3)), prediction_seconds=float(match.group(4)))
            if any("test_balanced_accuracy" not in row["metrics"][mid] for mid in ("dummy", "nearest_centroid")):
                raise ValueError("Could not parse saved baseline final rows")
            row["metrics"]["nearest_centroid"]["per_class"] = parse_classification_report("\n".join(x["text"] for x in saved["30"]))
            row["metrics"]["dummy"]["per_class"] = None
            row["missing_or_unverified"] += ["baseline 各模型参数数量未打印", "Dummy 逐类报告未保存", "baseline 划分索引哈希未打印"]
            environments["notebooks"][name] = {"source": evidence(4), "saved_text": saved["4"][0]["text"]}
            report += [f"## {name}", "", f"SHA-256: `{checksums[name]}`；代码 Cell {len(code_cells)} 个，已执行 {row['executed_code_cells']} 个，错误输出 {len(errors)} 个。",
                       "", "历史环境见 Cell 4 (A)；数据形状见 Cell 6 (A)，归一化和 25,600/6,400 划分见 Cell 9 (A)。固定基线验证见 Cell 22 (A)，最终测试见 Cell 29 (A)；最近质心逐类报告见 Cell 30 (A)。", "",
                       "| 模型 | 验证 Accuracy / Macro-F1 / Balanced | 测试 Accuracy / Macro-F1 / Balanced | 最终训练 / 预测秒 | 来源 |",
                       "|---|---:|---:|---:|---|",
                       *[f"| {label} | {m['validation_accuracy']} / {m['validation_macro_f1']} / {m['validation_balanced_accuracy']} | {m['test_accuracy']} / {m['test_macro_f1']} / {m['test_balanced_accuracy']} | {m['fit_seconds']} / {m['prediction_seconds']} | A: Cell 22, 29，表格仅保留 4 位小数 |"
                         for label, m in (("Dummy", row['metrics']['dummy']), ("Nearest Centroid", row['metrics']['nearest_centroid']))], ""]
        elif name == "Naive_Bayes.ipynb":
            final = "\n".join(x["text"] for x in saved["22"])
            search_text = "\n".join(x["text"] for x in saved["15"])
            search_scores, search_balanced = search_text.split("validation_balanced_accuracy", 1)
            selected_match = re.search(r"(?m)^\s*3\s+1e-06\s+([0-9.]+)\s+([0-9.]+)\s*$", search_scores)
            balanced_match = re.search(r"(?m)^\s*3\s+([0-9.]+)\s+[0-9.]+\s+[0-9.]+\s*$", search_balanced)
            if not selected_match or not balanced_match:
                raise ValueError("Could not parse saved GaussianNB frozen-choice search row")
            row["metrics"]["gaussian_nb"] = {
                "validation_accuracy": float(selected_match.group(1)),
                "validation_macro_f1": float(selected_match.group(2)),
                "validation_balanced_accuracy": float(balanced_match.group(1)),
                "test_accuracy": find_number(final, "Test accuracy"), "test_macro_f1": find_number(final, "Test macro F1"),
                "test_balanced_accuracy": find_number(final, "Test balanced accuracy"),
                "fit_seconds": find_number(final, "Training time"), "prediction_seconds": find_number(final, "Test prediction time"),
                "selected_hyperparameters": {"var_smoothing": 1e-6}, "selected_epochs": None,
                "per_class": parse_classification_report(final),
            }
            row["metric_evidence"]["gaussian_nb"] = {"validation": evidence(15), "test": evidence(22), "selection": "C: Cell 22 BEST_VAR_SMOOTHING；B: Cell 18 tie-break 描述"}
            row["search_saved_display"] = saved["15"]
            row["missing_or_unverified"] += ["历史环境版本/硬件没有保存输出", "参数数量未保存", "训练/验证索引哈希未打印", "混淆矩阵数组仅以图像形式保存，无法可靠读取精确各格"]
            environments["notebooks"][name] = {"source": "D", "saved_text": None}
            report += [f"## {name}", "", f"SHA-256: `{checksums[name]}`；代码 Cell {len(code_cells)} 个，已执行 {row['executed_code_cells']} 个，错误输出 {len(errors)} 个。", "",
                       "Cell 5 (A) 保存数据形状与划分样本数；Cell 7 (A) 保存 255 缩放、2352 维和训练输入范围；Cell 15 (A) 保存 8 个 `var_smoothing` 搜索表，四位小数；Cell 18 (B) 描述 tie-break；Cell 22 (C 源码冻结 1e-6，A 输出) 保存完整训练/测试评价和逐类报告。", "",
                       "验证 0.4041 / 0.3749 / 0.4188；测试 0.4155 / 0.3857 / 0.4307（Accuracy / Macro-F1 / Balanced，A，四位小数）。训练 0.3792 秒，预测 0.9081 秒（A）。历史环境版本和精确混淆矩阵数据缺失 (D)。", ""]
        else:
            prefix = "mlp" if name == "MLP.ipynb" else "cnn"
            env_cell, split_cell, search_cell, hardcoded_cell, frozen_cell, final_cell = (4, 6, 18, 19, 25, 27) if prefix == "mlp" else (3, 5, 19, 20, 27, 29)
            envtxt = "\n".join(x["text"] for x in saved[str(env_cell)])
            try:
                start = envtxt.index("{")
                decoder = json.JSONDecoder()
                env, _ = decoder.raw_decode(envtxt[start:])
            except (ValueError, KeyError):
                env = {"parse_error": True, "raw": envtxt}
            environments["notebooks"][name] = {"source": evidence(env_cell), "values": env}
            final = "\n".join(x["text"] for x in saved[str(final_cell)])
            assigns = literal_assignments(source[str(frozen_cell)],
                {"MLP_BEST_PARAMS", "MLP_FINAL_EPOCHS", "CNN_BEST_PARAMS", "CNN_FINAL_EPOCHS"})
            row["metrics"][prefix] = {
                "validation_accuracy": table_number(final, "validation_accuracy"),
                "validation_macro_f1": table_number(final, "validation_macro_f1"),
                "validation_balanced_accuracy": None,
                "test_accuracy": table_number(final, "test_accuracy"),
                "test_macro_f1": table_number(final, "test_macro_f1"),
                "test_balanced_accuracy": table_number(final, "test_balanced_accuracy"),
                "fit_seconds": table_number(final, "fit_seconds"),
                "prediction_seconds": table_number(final, "prediction_seconds"),
                "parameters": table_number(final, "parameters"),
                "selected_hyperparameters": assigns.get(f"{prefix.upper()}_BEST_PARAMS"),
                "selected_epochs": assigns.get(f"{prefix.upper()}_FINAL_EPOCHS"),
                "per_class": parse_classification_report(final),
            }
            frozen = "\n".join(x["text"] for x in saved[str(frozen_cell)])
            bal = re.search(r"'balanced_accuracy':\s*([0-9.]+)", frozen)
            if bal:
                row["metrics"][prefix]["validation_balanced_accuracy"] = float(bal.group(1))
            valacc = re.search(r"'accuracy':\s*([0-9.]+)", frozen)
            if row["metrics"][prefix]["validation_accuracy"] is None and valacc:
                row["metrics"][prefix]["validation_accuracy"] = float(valacc.group(1))
            trial_text = [(x["output_index"], x["text"]) for x in saved[str(search_cell)]]
            trials = []
            current = None
            for output_index, txt in trial_text:
                m = re.search(r"Trial\s+(\d+)/8:\s*(\{[^}]+\})", txt)
                if m:
                    current = {"trial_id": int(m.group(1)), "hyperparameters": ast.literal_eval(m.group(2)), "evidence": evidence(search_cell), "output_index": output_index}
                    trials.append(current)
                f1 = re.search(r"Restored validation Macro-F1:\s*([0-9.]+)", txt)
                if f1 and current is not None:
                    current["validation_macro_f1_rounded"] = float(f1.group(1))
            row["search_trials_saved_output"] = trials
            row["hardcoded_history"] = {"source_type": "C", "cell": hardcoded_cell, "assignment_names":
                [line.strip()[:120] for line in source[str(hardcoded_cell)].splitlines() if "RECORDED" in line][:10]}
            row["metric_evidence"][prefix] = {"environment": evidence(env_cell), "split": evidence(split_cell),
                "search": evidence(search_cell), "selected": f"A: Cell {frozen_cell} 输出；C: Cell {frozen_cell} 常量",
                "test": evidence(final_cell)}
            row["missing_or_unverified"] += ["历史最终测试预测标签文件不在 Git 仓库，无法独立重算 V1 指标", "保存输出中的某些表格显示位数低于内部精度"]
            report += [f"## {name}", "", f"SHA-256: `{checksums[name]}`；代码 Cell {len(code_cells)} 个，已执行 {row['executed_code_cells']} 个，错误输出 {len(errors)} 个。", "",
                       f"环境 Cell {env_cell} (A)；数据与索引指纹 Cell {split_cell} (A)；8 次实际搜索日志 Cell {search_cell} (A)；硬编码的历史绘图数据 Cell {hardcoded_cell} (C)；冻结参数/epoch Cell {frozen_cell} (C 常量，A 打印)；最终模型/逐类结果 Cell {final_cell} (A)。",
                       "", f"搜索输出识别到 {len(trials)} 组 trial；逐组至少保存参数与恢复后的验证 Macro-F1。", "",
                       f"V1 验证 Accuracy / Macro-F1 / Balanced：{row['metrics'][prefix]['validation_accuracy']} / {row['metrics'][prefix]['validation_macro_f1']} / {row['metrics'][prefix]['validation_balanced_accuracy']}；V1 测试：{row['metrics'][prefix]['test_accuracy']} / {row['metrics'][prefix]['test_macro_f1']} / {row['metrics'][prefix]['test_balanced_accuracy']}。参数 {row['metrics'][prefix]['parameters']}，最终 {row['metrics'][prefix]['selected_epochs']} epochs。", ""]
            report += ["| Trial | 参数 | 验证 Macro-F1（历史运行输出，显示精度） | Cell / Output |",
                       "|---:|---|---:|---|"]
            for trial in trials:
                report.append(f"| {trial['trial_id']} | `{trial['hyperparameters']}` | {trial.get('validation_macro_f1_rounded', 'D')} | {search_cell} / {trial['output_index']} 起 |")
            report.append("")
        if name == "baseline.ipynb":
            evidence_cells = [22, 29, 30]
        elif name == "Naive_Bayes.ipynb":
            evidence_cells = [11, 15, 22]
        elif name == "MLP.ipynb":
            evidence_cells = [4, 6, 25, 27]
        else:
            evidence_cells = [3, 5, 20, 27, 29, 30]
        report += ["### 保存输出原文摘录", ""]
        for cell_number in evidence_cells:
            text_outputs = [x for x in saved[str(cell_number)] if not x["text"].lstrip().startswith("<Figure")]
            for output in text_outputs:
                snippet = output["text"]
                if len(snippet) > 7500:
                    snippet = snippet[:7500] + "\n[后文见 original_results.json 对应 Cell 的完整文本输出]"
                provenance = "A/C：该输出由硬编码历史记录生成" if name == "CNN.ipynb" and cell_number == 20 else "A：保存输出"
                report += [f"Cell {cell_number}, output {output['output_index']} ({output['type']}；{provenance}):", "", "```text", snippet.rstrip(), "```", ""]
        report += ["### D：缺失或无法核实", ""]
        report += [f"- {item}" for item in row["missing_or_unverified"]]
        report.append("")
        for model_name, model_result in row["metrics"].items():
            if model_result.get("per_class"):
                report += [f"### {model_name} 逐类指标（A：保存的分类报告）", "",
                           "| 类别 | Precision | Recall | F1 | Support |", "|---|---:|---:|---:|---:|"]
                for class_name, metrics in model_result["per_class"].items():
                    report.append(f"| {class_name} | {metrics['precision']} | {metrics['recall']} | {metrics['f1']} | {metrics['support']} |")
                report.append("")
        all_results["notebooks"][name] = row
    report += ["## 缺失与使用边界", "", "- 原始 Notebook 保存的图像输出可能显示混淆矩阵，但像素图不能可靠还原全部整数；V2 会保存数值 CSV。", "- 所有 V1 用时来自不同硬件/系统，不能当作控制变量后的算法速度比较。", "- 此文件仅为训练前快照。V2 成功与否必须由新运行日志和预测标签确认。", ""]
    (OUT / "reference" / "original_results.json").write_text(json.dumps(all_results, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "reference" / "original_environment.json").write_text(json.dumps(environments, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "reports" / "00_pre_reproduction_audit.md").write_text("\n".join(report), encoding="utf-8")
    print(f"Snapshot written at {clone_time}, commit {manifest['commit']}")


if __name__ == "__main__":
    main()
