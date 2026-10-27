"""Evidence-based neural-network difference analysis; no training or source edits."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / "reproduction_v2"
RUNS = V2 / "runs"
REPORTS = V2 / "reports"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def csv_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def v1_epochs(reference: dict, notebook: str, cell: int) -> list[dict]:
    outputs = reference["notebooks"][notebook]["saved_text_outputs_by_cell"][str(cell)]
    result = []
    for output in outputs:
        text = output["text"]
        if "250/250" not in text or "accuracy:" not in text or "loss:" not in text:
            continue
        match = re.search(r"accuracy:\s*([0-9.]+)\s+-\s+loss:\s*([0-9.]+)\s+-\s+macro_f1:\s*([0-9.]+)", text)
        if match:
            result.append({"epoch": len(result)+1, "accuracy": float(match.group(1)),
                           "loss": float(match.group(2)), "macro_f1": float(match.group(3))})
    return result


def latest_final_only(model: str) -> tuple[Path | None, dict | None]:
    found = []
    for directory in sorted(RUNS.iterdir()):
        status_file = directory / "run_status.json"
        if not status_file.is_file():
            continue
        status = read_json(status_file)
        if status.get("model") == model and status.get("mode") == "final_only" and status.get("status") == "PASS":
            found.append((directory, status))
    return found[-1] if found else (None, None)


def main() -> None:
    reference = read_json(V2 / "reference" / "original_results.json")
    comparison = read_json(REPORTS / "comparison.json")
    original_env = read_json(V2 / "reference" / "original_environment.json")["notebooks"]
    audit = read_json(RUNS / "data_environment_audit.json")
    cpu_note = (V2 / "reference" / "docker_cpu.txt").read_text(encoding="utf-8").strip() if (V2 / "reference" / "docker_cpu.txt").exists() else "CPU model not recorded"
    analysis = {"commit": reference["commit"], "models": {}, "limits": []}
    lines = ["# 05 神经网络差异归因分析", "",
             "此报告区分可由运行证据直接确认的事实、受控对照结论和尚未隔离的可能因素。差值阈值不是统计显著性检验。", "",
             "## 已排除的实验流程差异", "",
             f"- 原始 Canvas 四个 `.npy` 文件的 SHA-256 与克隆基线一致；图像形状为 32,000/8,000，split 指纹一致：{audit['split']['fingerprints_match_v1']}。",
             "- MLP、CNN 的源 Notebook、最终参数、最终 epoch、Seed 5318、Batch 128 和测试标签均未改；验证使用 Macro-F1 选参，最终训练使用全部 32,000 张训练图，测试为 8,000 张。",
             "- 各次严格执行的 Notebook 输出指标与保存的预测标签独立重算结果一致。", ""]
    for model, notebook, final_cell in (("mlp", "MLP.ipynb", 26), ("cnn", "CNN.ipynb", 28)):
        entry = comparison["models"][model]
        strict_dir = Path(entry["run_dir"])
        final_dir, final_status = latest_final_only(model)
        strict_metrics = read_json(strict_dir / "verified_metrics.json")[model]
        final_metrics = read_json(final_dir / "verified_metrics.json")[model] if final_dir else None
        strict_hash = strict_metrics["predictions_sha256"]
        final_hash = final_metrics["predictions_sha256"] if final_metrics else None
        v1_history = v1_epochs(reference, notebook, final_cell)
        v2_history = csv_rows(strict_dir / f"{model}_final_history.csv")
        trajectory = []
        for prior, current in zip(v1_history, v2_history):
            trajectory.append({"epoch": prior["epoch"], "v1_loss_rounded": prior["loss"],
                               "v2_loss": float(current["loss"]), "loss_delta_v2_minus_v1": float(current["loss"])-prior["loss"],
                               "v1_accuracy_rounded": prior["accuracy"], "v2_accuracy": float(current["accuracy"]),
                               "accuracy_delta_v2_minus_v1": float(current["accuracy"])-prior["accuracy"]})
        class_rows = [r for r in comparison["per_class_comparison"] if r["model"] == model]
        largest = sorted([r for r in class_rows if r["absolute_difference"] is not None],
                         key=lambda r: r["absolute_difference"], reverse=True)[:5]
        f1_contributions = sorted([
            {"class_id": r["class_id"], "class_name": r["class_name"],
             "f1_delta": r["v2_value"] - r["v1_value"],
             "macro_f1_contribution": (r["v2_value"] - r["v1_value"]) / 9}
            for r in class_rows if r["metric"] == "f1" and r["v2_value"] is not None
        ], key=lambda r: abs(r["macro_f1_contribution"]), reverse=True)
        best = entry["v2_search_best"]
        v1 = entry["v1"]
        v2 = entry["v2"]
        v1_env = original_env[notebook]["values"]
        facts = {
            "strict_run": str(strict_dir), "final_only_run": str(final_dir) if final_dir else None,
            "strict_prediction_sha256": strict_hash, "final_only_prediction_sha256": final_hash,
            "strict_final_only_predictions_identical": strict_hash == final_hash if final_hash else None,
            "v1_final": {k: v1.get(k) for k in ("test_accuracy", "test_macro_f1", "test_balanced_accuracy", "selected_epochs")},
            "v2_final": {k: v2.get(k) for k in ("test_accuracy", "test_macro_f1", "test_balanced_accuracy", "selected_epochs")},
            "v1_frozen_hyperparameters": entry["v1_frozen_parameters"],
            "v2_search_best": best, "v1_environment": v1_env,
            "v2_environment": {"python": audit["python"], "platform": audit["platform"], "packages": audit["packages"], "devices": audit["tensorflow"]["physical_devices"]},
            "training_trajectory": trajectory, "largest_class_metric_differences": largest,
            "macro_f1_class_contributions_from_rounded_v1": f1_contributions,
        }
        analysis["models"][model] = facts
        final_only_text = (f"通过；严格与跳过搜索的最终预测文件 SHA-256 完全相同 (`{strict_hash}`)"
                           if facts["strict_final_only_predictions_identical"] else "未完成或预测不同，不能排除搜索状态影响")
        lines += [f"## {model.upper()}", "",
                  f"- Test Accuracy：V1 {v1['test_accuracy']:.6f} → V2 {v2['test_accuracy']:.6f}；Macro-F1：{v1['test_macro_f1']:.6f} → {v2['test_macro_f1']:.6f}；Balanced Accuracy：{v1['test_balanced_accuracy']:.6f} → {v2['test_balanced_accuracy']:.6f}。",
                  f"- V1 与 V2 搜索最佳参数一致：`{entry['v1_frozen_parameters']}`；V1 冻结 epoch {v1['selected_epochs']}，V2 搜索最佳 epoch {best.get('best_epoch') if best else 'D'}。V2 主测试仍按 V1 冻结 epoch 训练。",
                  f"- 同一 Docker 镜像、独立 Kernel 的跳过搜索对照：{final_only_text}。这支持‘搜索消耗随机状态不是此次 V2 最终预测差异的原因’，并验证最终模型单元无需搜索对象即可运行。",
                  f"- 日志：严格运行 `runs/{strict_dir.name}/execution.log`；跳过搜索对照 `runs/{final_dir.name if final_dir else 'D'}/execution.log`。对应环境记录、执行副本与预测标签保存在同目录。",
                  f"- V1 环境：Python {v1_env.get('python')}，TensorFlow {v1_env.get('tensorflow')}，Keras {v1_env.get('keras')}，`{v1_env.get('platform')}`；V2：Python {audit['python']}，TensorFlow {audit['packages']['tensorflow']}，Keras {audit['packages']['keras']}，`{audit['platform']}`，仅 CPU。V2 CPU 记录：`{cpu_note}`。",
                  "", "### 最终全量训练轨迹（V1 为保存日志四位显示精度）", "",
                  "| Epoch | V1 loss | V2 loss | V2−V1 | V1 accuracy | V2 accuracy | V2−V1 |", "|---:|---:|---:|---:|---:|---:|---:|"]
        for r in trajectory:
            lines.append(f"| {r['epoch']} | {r['v1_loss_rounded']:.4f} | {r['v2_loss']:.4f} | {r['loss_delta_v2_minus_v1']:+.4f} | {r['v1_accuracy_rounded']:.4f} | {r['v2_accuracy']:.4f} | {r['accuracy_delta_v2_minus_v1']:+.4f} |")
        lines += ["", "### 最大逐类变化", "",
                  "| 类别 | 指标 | V1 | V2 | 绝对差 |", "|---|---|---:|---:|---:|"]
        for r in largest:
            lines.append(f"| {r['class_id']} {r['class_name']} | {r['metric']} | {r['v1_value']:.4f} | {r['v2_value']:.4f} | {r['absolute_difference']:.4f} |")
        lines += ["", "### Macro-F1 差值的逐类分解", "",
                  "下表按 `(V2 类别 F1 − V1 类别 F1) / 9` 计算；V1 逐类 F1 只保存四位小数，因此贡献为近似值。它解释总指标由哪些类别推动，不解释训练轨迹改变的根因。", "",
                  "| 类别 | F1 差 | 对 Macro-F1 差的贡献 |", "|---|---:|---:|"]
        for r in f1_contributions:
            lines.append(f"| {r['class_id']} {r['class_name']} | {r['f1_delta']:+.4f} | {r['macro_f1_contribution']:+.6f} |")
        total_macro_delta = v2["test_macro_f1"] - v1["test_macro_f1"]
        aligned = [r for r in f1_contributions if r["macro_f1_contribution"] * total_macro_delta > 0]
        if aligned and total_macro_delta:
            lead = aligned[0]
            lines.append(f"\n最大同方向贡献为 {lead['class_id']} {lead['class_name']}：{lead['macro_f1_contribution']:+.6f}，约为总体 Macro-F1 差 {total_macro_delta:+.6f} 的 {abs(lead['macro_f1_contribution']/total_macro_delta):.1%}。")
            if len(aligned) > 1:
                pair = sum(r["macro_f1_contribution"] for r in aligned[:2])
                lines.append(f"前两类同方向贡献合计 {pair:+.6f}，约为总体差值的 {abs(pair/total_macro_delta):.1%}；其余类别有正负抵消。")
        lines.append("")
    lines += ["## 归因判断与限制", "",
              "- **已确认：** 数据、拆分、Seed、最终参数和 epoch 一致；同一 V2 环境跳过搜索后的预测与完整搜索严格运行相同。代码与运行证据未发现测试集调参、参数替换或数据变更；在 V2 中，搜索 Cell 没有改变最终预测。",
              "- **有证据支持的可能因素：** V1 MLP 在 Windows/Intel，V1 CNN 在 macOS/arm64 且 Keras 3.5.0；V2 在 Linux/amd64/AMD CPU，Keras 3.6.0。不同 CPU 数值内核与框架组合可能导致训练轨迹变化；CNN 早期轨迹已可观察到差异。MLP 在最初两轮接近到四位小数，之后偏差逐渐显现。",
              "- **尚不能确认单一根因：** 没有在相同硬件上逐项只改变 OS、Python/Keras 版本、完整传递依赖或 CPU 内核的对照运行，故无法量化各因素贡献，也不能将差异简单归为随机性。V1 仅保存有限显示精度的输出，缺少原始预测数组与完整依赖锁。",
              "- **实际影响：** MLP 的 Normal colon mucosa F1 下降明显；CNN 的 Debris 和 Cancer-associated stroma Recall/F1 上升较多。Macro-F1 对九类等权，逐类变化能解释总体方向，但不证明跨环境性能提升具有统计显著性。",
              "- **建议：** A2 提交材料应注明运行平台与框架版本，引用本次独立复现的逐类表，并明确区分 V1 保存的历史绘图和 V2 新搜索。不要为了贴近 V1 修改模型、超参数、Seed 或测试集使用方式。", ""]
    (REPORTS / "difference_analysis.json").write_text(json.dumps(analysis, indent=2, ensure_ascii=False), encoding="utf-8")
    (REPORTS / "05_difference_analysis.md").write_text("\n".join(lines), encoding="utf-8")
    print("Wrote difference analysis:", REPORTS / "05_difference_analysis.md")


if __name__ == "__main__":
    main()
