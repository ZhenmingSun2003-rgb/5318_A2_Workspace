"""Generate evidence-linked V1/V2 comparisons from completed strict runs."""
from __future__ import annotations

import csv
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / "reproduction_v2"
RUNS = V2 / "runs"
REPORTS = V2 / "reports"
REFERENCE = json.loads((V2 / "reference" / "original_results.json").read_text(encoding="utf-8"))
MODEL_NOTEBOOK = {"dummy": "baseline.ipynb", "nearest_centroid": "baseline.ipynb",
                  "gaussian_nb": "Naive_Bayes.ipynb", "mlp": "MLP.ipynb", "cnn": "CNN.ipynb"}
MODEL_RUN = {"dummy": "baseline", "nearest_centroid": "baseline", "gaussian_nb": "naive_bayes", "mlp": "mlp", "cnn": "cnn"}
METRICS = ["validation_accuracy", "validation_macro_f1", "validation_balanced_accuracy",
           "test_accuracy", "test_macro_f1", "test_balanced_accuracy", "fit_seconds",
           "prediction_seconds", "parameters", "selected_epochs"]


def read_json(path: Path, default=None):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def num(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def same_params(row: dict, selected: dict) -> bool:
    return all(num(row.get(k)) is not None and math.isclose(num(row.get(k)), float(v), rel_tol=0, abs_tol=1e-10)
               for k, v in selected.items())


def notebook_final(run_dir: Path, model: str) -> dict:
    if model in ("dummy", "nearest_centroid"):
        target = "Most frequent" if model == "dummy" else "Nearest centroid (RGB pixels)"
        row = next((r for r in rows(run_dir / "notebook_final_results.csv") if r.get("model") == target), {})
        return {"test_accuracy": num(row.get("accuracy")), "test_macro_f1": num(row.get("macro_f1")),
                "test_balanced_accuracy": num(row.get("balanced_accuracy")),
                "fit_seconds": num(row.get("fit_seconds")), "prediction_seconds": num(row.get("prediction_seconds"))}
    if model == "gaussian_nb":
        log = (run_dir / "execution.log").read_text(encoding="utf-8")
        inventory = read_json(run_dir / "parameter_inventory.json", {})
        smoothing = re.search(r"Final GaussianNB parameters:.*?'var_smoothing':\s*([0-9.eE+-]+)", log)
        def get(pattern):
            match = re.search(pattern, log)
            return float(match.group(1)) if match else None
        return {"test_accuracy": get(r"Test accuracy:\s*([0-9.]+)"),
                "test_macro_f1": get(r"Test macro F1:\s*([0-9.]+)"),
                "test_balanced_accuracy": get(r"Test balanced accuracy:\s*([0-9.]+)"),
                "fit_seconds": get(r"Training time:\s*([0-9.]+)"),
                "prediction_seconds": get(r"Test prediction time:\s*([0-9.]+)"),
                "parameters": inventory.get("stored_numeric_total"),
                "best_hyperparameters": {"var_smoothing": float(smoothing.group(1))} if smoothing else None}
    row = (rows(run_dir / f"{model}_final_results.csv") or [{}])[0]
    values = {k: num(row.get(k)) for k in ("test_accuracy", "test_macro_f1", "test_balanced_accuracy", "fit_seconds", "prediction_seconds", "parameters", "epochs", "search_fit_samples", "validation_samples", "train_samples", "test_samples")}
    try:
        values["best_hyperparameters"] = json.loads(row.get("best_hyperparameters", "{}"))
    except json.JSONDecodeError:
        values["best_hyperparameters"] = None
    return values


def validation(run_dir: Path, model: str, selected: dict) -> tuple[dict, dict | None, int]:
    if model in ("dummy", "nearest_centroid"):
        name = "Most frequent" if model == "dummy" else "Nearest centroid (RGB pixels)"
        row = next((r for r in rows(run_dir / "validation_results.csv") if r.get("model") == name), {})
        return ({"validation_accuracy": num(row.get("accuracy")), "validation_macro_f1": num(row.get("macro_f1")),
                 "validation_balanced_accuracy": num(row.get("balanced_accuracy"))}, None, 0)
    table = rows(run_dir / "search_results.csv")
    chosen = next((r for r in table if same_params(r, selected)), {})
    best = max(table, key=lambda r: num(r.get("validation_macro_f1")) or -1) if table else None
    return ({"validation_accuracy": num(chosen.get("validation_accuracy")),
             "validation_macro_f1": num(chosen.get("validation_macro_f1")),
             "validation_balanced_accuracy": num(chosen.get("validation_balanced_accuracy"))}, best, len(table))


def status_for(metric: str, a, b, model: str) -> str:
    if a is None or b is None:
        return "NOT AVAILABLE"
    if metric in ("selected_epochs", "parameters"):
        return "EXACT" if a == b else "DIFFERENT"
    delta = abs(a-b)
    if metric.endswith("seconds"):
        return "HARDWARE NOT CONTROLLED"
    if delta == 0:
        return "EXACT"
    if delta > .05:
        return "SIGNIFICANT RISK (>0.05)"
    if delta > .02:
        return "INVESTIGATE (>0.02)"
    if delta > .01:
        return "NOTICE (>0.01)"
    precision = .000051 if model in ("dummy", "nearest_centroid", "gaussian_nb") else .000001
    return "MATCHES PRINTED PRECISION" if delta <= precision else "SMALL DIFFERENCE"


def main() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    paths = {}
    for directory in sorted(RUNS.iterdir()):
        if not directory.is_dir():
            continue
        state = read_json(directory / "run_status.json", {})
        model_name = state.get("model")
        if not model_name or state.get("mode", "strict") != "strict":
            continue
        # Prefer the latest successful strict run; retain a failed run when no success exists.
        if model_name not in paths or state.get("status") == "PASS":
            paths[model_name] = directory
    audit = read_json(RUNS / "data_environment_audit.json", {})
    comparison = []
    per_class_comparison = []
    model_summaries = {}
    issues = []
    issues.append({"severity": "MEDIUM", "model": "mlp/cnn",
                   "issue": "Original plotting cells embed V1 search rows, and final-result CSV validation fields repeat V1 frozen-selection constants. V2 search comparison uses newly written search_results.csv only."})
    issues.append({"severity": "LOW", "model": "v1 records",
                   "issue": "V1 exact prediction arrays and numeric confusion matrices are not present in Git; V1 class reports are rounded saved output. V2 exports full predictions and numeric matrices."})
    for directory in sorted(RUNS.iterdir()):
        if directory.is_dir():
            previous = read_json(directory / "run_status.json", {})
            if previous.get("status") == "FAIL" and previous.get("cause_followup"):
                issues.append({"severity": "INFO", "model": previous.get("model"),
                               "issue": "Run interrupted by user-acknowledged manual Docker Desktop restart; excluded from model failure assessment. Partial logs preserved.",
                               "evidence": str(directory / "execution.log")})
    for model in MODEL_NOTEBOOK:
        ref_record = REFERENCE["notebooks"][MODEL_NOTEBOOK[model]]
        ref = ref_record["metrics"][model]
        ref_evidence = ref_record["metric_evidence"].get(model, {})
        run_dir = paths.get(MODEL_RUN[model])
        run_status = read_json(run_dir / "run_status.json", {}) if run_dir else {}
        verified = read_json(run_dir / "verified_metrics.json", {}) if run_dir else {}
        v2 = verified.get(model, {})
        notebook = notebook_final(run_dir, model) if run_dir and run_status.get("status") == "PASS" else {}
        selected = ref.get("selected_hyperparameters") or ({"var_smoothing": 1e-6} if model == "gaussian_nb" else {})
        val, best, search_count = validation(run_dir, model, selected) if run_dir and run_status.get("status") == "PASS" else ({}, None, 0)
        values = {**val, "test_accuracy": v2.get("accuracy"), "test_macro_f1": v2.get("macro_f1"),
                  "test_balanced_accuracy": v2.get("balanced_accuracy"),
                  "fit_seconds": notebook.get("fit_seconds"), "prediction_seconds": notebook.get("prediction_seconds"),
                  "parameters": notebook.get("parameters"), "selected_epochs": notebook.get("epochs")}
        row_status = run_status.get("status", "NOT RUN")
        expected_cells = REFERENCE["notebooks"][MODEL_NOTEBOOK[model]]["code_cells"]
        if row_status == "PASS" and run_status.get("completed_original_code_cells") != expected_cells:
            row_status = "FAIL"
            issues.append({"severity": "HIGH", "model": model,
                           "issue": f"Original code cell completion mismatch: expected {expected_cells}, got {run_status.get('completed_original_code_cells')}"})
        if model in ("mlp", "cnn") and row_status == "PASS":
            expected_sizes = {"search_fit_samples": 25600, "validation_samples": 6400,
                              "train_samples": 32000, "test_samples": 8000}
            if any(notebook.get(k) != v for k, v in expected_sizes.items()):
                row_status = "FAIL"
                issues.append({"severity": "HIGH", "model": model,
                               "issue": f"Final sample counts disagree with protocol: {notebook}"})
        if model in ("gaussian_nb", "mlp", "cnn") and row_status == "PASS" and search_count != 8:
            row_status = "FAIL"
            issues.append({"severity": "HIGH", "model": model, "issue": f"Expected 8 search trials, found {search_count}"})
        if model in ("mlp", "cnn") and row_status == "PASS":
            if notebook.get("best_hyperparameters") != selected or notebook.get("epochs") != ref.get("selected_epochs"):
                row_status = "FAIL"
                issues.append({"severity": "HIGH", "model": model,
                               "issue": "Final model no longer matches V1 frozen hyperparameters or epoch count"})
        for field, key in [("test_accuracy", "accuracy"), ("test_macro_f1", "macro_f1"), ("test_balanced_accuracy", "balanced_accuracy")]:
            n = notebook.get(field)
            calc = v2.get(key)
            tolerance = .000051 if model == "gaussian_nb" else (.000051 if model in ("dummy", "nearest_centroid") else 1e-8)
            if n is not None and calc is not None and abs(n-calc) > tolerance:
                row_status = "FAIL"
                issues.append({"severity": "HIGH", "model": model, "issue": f"Notebook {field}={n} but independent calculation={calc}"})
        if model in ("mlp", "cnn") and ref.get("selected_hyperparameters") and best:
            best_params = {k: num(best[k]) for k in selected}
            if not same_params(best, selected):
                issues.append({"severity": "LOW", "model": model, "issue": "V2 validation-best parameters differ from V1 frozen final parameters; final comparison still uses V1 frozen parameters", "v2_best": best_params})
        reproduction_status = row_status
        if row_status == "PASS":
            aggregate_warning = any(ref.get(field) is not None and values.get(field) is not None
                                    and abs(float(ref[field]) - float(values[field])) > .01
                                    for field in ("test_accuracy", "test_macro_f1", "test_balanced_accuracy"))
            class_warning = any(
                num(v2.get("classification_report", {}).get(str(i), {}).get(calc)) is not None
                and abs(float(class_metrics[old_key]) - float(v2["classification_report"][str(i)][calc])) > .05
                for i, class_metrics in enumerate((ref.get("per_class") or {}).values())
                for old_key, calc in (("recall", "recall"), ("f1", "f1-score"))
            )
            if aggregate_warning or class_warning:
                reproduction_status = "WARNING"
        model_summaries[model] = {"status": reproduction_status, "execution_status": row_status,
                                  "run_dir": str(run_dir) if run_dir else None,
                                  "source_notebook": MODEL_NOTEBOOK[model], "search_trial_count": search_count,
                                  "v1_frozen_parameters": selected, "v2_search_best": best,
                                  "v1": ref, "v2": values, "independent": v2, "notebook_reported": notebook}
        for class_id, (class_name, metrics) in enumerate((ref.get("per_class") or {}).items()):
            computed = v2.get("classification_report", {}).get(str(class_id), {})
            for field, calc_field in (("recall", "recall"), ("f1", "f1-score")):
                old = num(metrics.get(field))
                new = num(computed.get(calc_field))
                if old is not None and new is not None and abs(old-new) > .05:
                    issues.append({"severity": "MEDIUM", "model": model,
                                   "issue": f"Class {class_id} {class_name} {field} differs by {abs(old-new):.4f} (V1 {old:.4f}, V2 {new:.4f}); investigate class-level shift."})
                per_class_comparison.append({"model": model, "class_id": class_id, "class_name": class_name,
                                             "metric": field, "v1_value": old, "v2_value": new,
                                             "absolute_difference": abs(old-new) if old is not None and new is not None else None,
                                             "status": status_for(field, old, new, model) if row_status == "PASS" else row_status,
                                             "evidence": f"V1 {MODEL_NOTEBOOK[model]} classification report; V2 verified_metrics.json"})
        for metric in METRICS:
            a = num(ref.get(metric))
            b = num(values.get(metric))
            diff = abs(a-b) if a is not None and b is not None else None
            if metric.startswith("validation_"):
                v2_file = "validation_results.csv" if model in ("dummy", "nearest_centroid") else "search_results.csv"
                source_evidence = ref_evidence.get("validation") or ref_evidence.get("search") or ref_evidence.get("selected", "D")
            elif metric.startswith("test_"):
                v2_file = "verified_metrics.json"
                source_evidence = ref_evidence.get("test", "D")
            else:
                v2_file = "notebook_final_results.csv" if model in ("dummy", "nearest_centroid") else "execution.log" if model == "gaussian_nb" else f"{model}_final_results.csv"
                if model == "gaussian_nb" and metric == "parameters":
                    v2_file = "parameter_inventory.json"
                source_evidence = ref_evidence.get("test", "D")
            comparison.append({"model": model, "metric": metric, "v1_value": a, "v2_value": b,
                               "absolute_difference": diff, "relative_difference": diff/abs(a) if diff is not None and a and not metric.endswith("seconds") else None,
                               "status": status_for(metric, a, b, model) if row_status == "PASS" else row_status,
                               "evidence_source": f"V1 {source_evidence}; V2 runs/{run_dir.name if run_dir else 'none'}/{v2_file}",
                               "notes": "V1 rounded display precision" if model in ("dummy", "nearest_centroid", "gaussian_nb") else ""})
        if model in ("gaussian_nb", "mlp", "cnn"):
            v2_params = notebook.get("best_hyperparameters")
            comparison.append({"model": model, "metric": "selected_hyperparameters",
                               "v1_value": json.dumps(selected, sort_keys=True),
                               "v2_value": json.dumps(v2_params, sort_keys=True) if v2_params is not None else None,
                               "absolute_difference": None, "relative_difference": None,
                               "status": "EXACT" if selected == v2_params and row_status == "PASS" else row_status if row_status != "PASS" else "DIFFERENT",
                               "evidence_source": f"V1 {ref_evidence.get('selection','frozen source cell')}; V2 runs/{run_dir.name if run_dir else 'none'}/{'execution.log' if model == 'gaussian_nb' else model + '_final_results.csv'}",
                               "notes": "Final model uses V1 frozen choice, independent of V2 search winner"})
    with (REPORTS / "comparison.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(comparison[0]))
        writer.writeheader(); writer.writerows(comparison)
    with (REPORTS / "per_class_comparison.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(per_class_comparison[0]))
        writer.writeheader(); writer.writerows(per_class_comparison)
    (REPORTS / "comparison.json").write_text(json.dumps({"models": model_summaries, "issues": issues, "comparison": comparison,
                                                            "per_class_comparison": per_class_comparison}, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    env = ["# 01 环境比较", "", f"V1 源 Commit: `{REFERENCE['commit']}`；V2 运行目录见模型比较报告。", "",
           "| 项目 | V1 记录 | V2 实测 |", "|---|---|---|"]
    original_env = read_json(V2 / "reference" / "original_environment.json", {})["notebooks"]
    common_v2 = f"Python {audit.get('python','D')}, NumPy {audit.get('packages',{}).get('numpy','D')}, TensorFlow {audit.get('packages',{}).get('tensorflow','D')}, Keras {audit.get('packages',{}).get('keras','D')}, {audit.get('platform','D')}"
    for nb in ("baseline.ipynb", "Naive_Bayes.ipynb", "MLP.ipynb", "CNN.ipynb"):
        e = original_env.get(nb, {})
        vals = e.get("values", {})
        if vals:
            description = f"Python {vals.get('python')}, NumPy {vals.get('numpy')}, TensorFlow {vals.get('tensorflow')}, Keras {vals.get('keras')}, {vals.get('platform')}"
        elif e.get("saved_text"):
            description = e["saved_text"].replace("\n", "; ")[:220]
        else:
            description = "D: Notebook 未保存版本/硬件输出"
        env.append(f"| {nb} | {description.replace('|','/')} | {common_v2} |")
    packages = audit.get("packages", {})
    image = read_json(V2 / "reference" / "docker_image.json", {})
    cnn_samples = rows(RUNS / "docker_cnn_resource_samples.csv")
    observed_gib = [float(m.group(1)) for sample in cnn_samples
                    if (m := re.search(r"([0-9.]+)GiB", sample.get("mem_usage", "")))]
    env += ["", f"V2: Python {audit.get('python', 'NOT RUN')}; `{audit.get('platform','NOT RUN')}`; CPU 数 {audit.get('cpu_count','D')}。",
            f"Docker 镜像 `{image.get('image','D')}`；ID `{image.get('id','D')}`；架构 `{image.get('architecture','D')}`。",
            f"实际 TensorFlow 设备：`{audit.get('tensorflow',{}).get('physical_devices','D')}`；cgroup CPU 配额 `{audit.get('cgroup_cpu_max','D')}`；cgroup 内存配置 `{audit.get('cgroup_memory_max','D')}` 字节。",
            f"CNN 完整运行期间 Docker stats 采样 {len(observed_gib)} 次，观察到最高内存 {max(observed_gib) if observed_gib else 'D'} GiB；这是采样峰值，不是精确最大值。",
            f"固定包：{', '.join(f'{k}={v}' for k,v in packages.items()) if packages else 'NOT RUN'}。",
            f"`pip check` 退出码：{audit.get('pip_check',{}).get('returncode','NOT RUN')}；完整依赖见各运行的 `pip-freeze.txt`。",
            "V1 来自不同系统和 CPU，耗时差异不能解释为控制变量后的算法速度差异。", ""]
    (REPORTS / "01_environment_comparison.md").write_text("\n".join(env), encoding="utf-8")

    lines = ["# 02 模型复现对比", "", "主实验始终使用原 Notebook 冻结的 V1 最终参数；V2 搜索最佳项单独列出。差值阈值仅为工程调查触发条件，不代表统计显著性。", "",
             "| 模型 | 指标 | V1 | V2 | 绝对差 | 相对差 | 状态 | 证据 | 注释 |", "|---|---|---:|---:|---:|---:|---|---|---|"]
    for r in comparison:
        fmt = lambda x: "D" if x is None else (str(x).replace("|", "/") if isinstance(x, str) else f"{x:.6g}")
        lines.append(f"| {r['model']} | {r['metric']} | {fmt(r['v1_value'])} | {fmt(r['v2_value'])} | {fmt(r['absolute_difference'])} | {fmt(r['relative_difference'])} | {r['status']} | `{r['evidence_source']}` | {r['notes']} |")
    lines += ["", "## 搜索和最终模型隔离", ""]
    for model, entry in model_summaries.items():
        best = entry["v2_search_best"]
        if not best:
            best_text = "D"
        else:
            keys = ("var_smoothing",) if model == "gaussian_nb" else ("hidden_units", "learning_rate", "dropout_rate") if model == "mlp" else ("base_filters", "learning_rate", "dropout_rate")
            chosen = {k: best.get(k) for k in keys}
            best_text = f"trial {best.get('trial_id','D')}，参数 `{chosen}`，Macro-F1 {best.get('validation_macro_f1','D')}，best epoch {best.get('best_epoch','D')}"
        lines.append(f"- {model}: {entry['status']}（源 Cell 执行 {entry['execution_status']}）；实际搜索 {entry['search_trial_count']} 组；V1 冻结参数 `{entry['v1_frozen_parameters']}`，冻结 epoch `{entry['v1'].get('selected_epochs')}`；V2 搜索最佳 {best_text}；最终测试仍使用 V1 冻结配置。运行 `{entry['run_dir']}`。")
    lines += ["", "## 逐类 Recall 与 F1", "", "V1 为 Notebook 保存的分类报告显示精度；V2 从保存的预测标签独立计算。", "",
              "| 模型 | 类别 | 指标 | V1 | V2 | 绝对差 | 状态 |", "|---|---|---|---:|---:|---:|---|"]
    for r in per_class_comparison:
        fmt = lambda x: "D" if x is None else f"{x:.6f}"
        lines.append(f"| {r['model']} | {r['class_id']} {r['class_name']} | {r['metric']} | {fmt(r['v1_value'])} | {fmt(r['v2_value'])} | {fmt(r['absolute_difference'])} | {r['status']} |")
    lines += ["", "完整逐类表亦见 `per_class_comparison.csv`，混淆矩阵见每次运行的 `*_confusion_matrix_verified.csv`。", ""]
    (REPORTS / "02_model_reproduction_comparison.md").write_text("\n".join(lines), encoding="utf-8")

    split = audit.get("split", {})
    runtime = read_json(V2 / "reference" / "docker_runtime_limits.json", {})
    integrity = ["# 03 实验完整性审计", "",
                 f"- Canvas 文件路径：`{audit.get('data',{}).get('X_train',{}).get('path','NOT RUN')}`。",
                 f"- 形状：训练 {audit.get('data',{}).get('X_train',{}).get('shape','D')}；测试 {audit.get('data',{}).get('X_test',{}).get('shape','D')}。",
                 f"- 拆分：fit {split.get('fit_count','D')}，validation {split.get('validation_count','D')}，test {split.get('test_count','D')}；索引指纹匹配 V1：{split.get('fingerprints_match_v1','D')}；fit/validation 不重叠：{split.get('fit_validation_disjoint','D')}。",
                 f"- fit SHA-256 `{split.get('fit_indices_sha256','D')}`；validation SHA-256 `{split.get('validation_indices_sha256','D')}`。",
                 f"- 精确图像字节哈希跨训练/测试重复数：{audit.get('exact_image_duplicate_counts',{}).get('cross_partition_unique_image_hashes','D')}（若非零，需按源数据现状报告）。",
                 f"- 容器网络模式 `{runtime.get('network_mode','D')}`；仓库挂载只读、`reproduction_v2/runs` 可写，挂载明细见 `reference/docker_runtime_limits.json`。",
                 "- 原 Notebook 源码执行顺序与实际执行副本见每个 `executed.ipynb`；末尾标记为 `reproduction_v2_audit_only` 的附加 Cell 只导出已生成的预测，不参与训练与调参。",
                 "- NumPy `float32`、训练范围决定的 255 固定缩放、MLP/NB 2352 维和 CNN RGB 结构来自原 Notebook 代码；V2 运行副本的输出核对见各执行日志。",
                 "- 模型选择用验证 Macro-F1。测试集仅用于冻结参数和 epoch 后的最终预测；未用于 Early Stopping。", ""]
    integrity += ["- 独立指标公式：`f1_score(y_true, y_pred, labels=np.arange(9), average='macro', zero_division=0)`；Accuracy 和 Balanced Accuracy 同由 sklearn.metrics 对保存预测重算。",
                  "- Strict reproduction 完整执行原始 Cell；另做了标记为 `final_only` 的可选跳过搜索对照，结果见 `05_difference_analysis.md`。Compatibility-assisted execution 未使用、未运行。", ""]
    if issues:
        integrity += ["## 发现", ""] + [f"- **{x['severity']}** {x['model']}: {x['issue']}" for x in issues] + [""]
    (REPORTS / "03_experiment_integrity_audit.md").write_text("\n".join(integrity), encoding="utf-8")

    executed = [m for m, e in model_summaries.items() if e["execution_status"] == "PASS"]
    matched = [m for m, e in model_summaries.items() if e["status"] == "PASS"]
    summary = ["# 04 最终复现摘要", "", f"源 Commit：`{REFERENCE['commit']}`。", "",
               f"严格执行完成 {len(executed)}/5：{', '.join(executed) if executed else '无'}。无指标提示模型 {len(matched)}/5。", "",
               "| 模型 | 执行状态 | V1 Test Accuracy / Macro-F1 | V2 Test Accuracy / Macro-F1 | 搜索次数 |", "|---|---|---:|---:|---:|"]
    for model, entry in model_summaries.items():
        a, b = entry["v1"], entry["v2"]
        p = lambda x: "D" if x is None else f"{x:.6f}"
        summary.append(f"| {model} | {entry['status']} | {p(a.get('test_accuracy'))} / {p(a.get('test_macro_f1'))} | {p(b.get('test_accuracy'))} / {p(b.get('test_macro_f1'))} | {entry['search_trial_count']} |")
    summary += ["", "## 结论与后续 A2 建议", "",
                "- 神经网络差异的训练轨迹、逐类贡献和跳过搜索对照见 `05_difference_analysis.md`。两个最终模型在 V2 中跳过搜索后的预测与严格运行逐字节一致。",
                "- 必须在提交说明中区分 V1 历史绘图/冻结验证常量与 V2 新搜索结果；原 Notebook 的历史绘图 Cell 不是 V2 搜索证据。",
                "- 对任何超过 0.02 的最终指标差值，结合逐类结果调查并如实披露；这些阈值是工程触发条件，不是统计显著性结论。",
                "- 可选保存这次 V2 的预测标签、数值混淆矩阵与运行环境记录，方便后续核对；大模型文件保留在 Git 忽略的 `runs/`。",
                "", "任何失败及 traceback 均留在对应 `runs/<run-id>/execution.log` 与 `run_status.json`。时间比较受 V1/V2 硬件与系统差异限制。", ""]
    (REPORTS / "04_final_reproduction_summary.md").write_text("\n".join(summary), encoding="utf-8")
    print(f"Wrote comparison for {len(executed)}/5 completed models; {len(matched)}/5 without warnings")


if __name__ == "__main__":
    main()
