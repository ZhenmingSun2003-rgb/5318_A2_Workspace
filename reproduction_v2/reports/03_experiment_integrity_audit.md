# 03 实验完整性审计

- Canvas 文件路径：`/workspace/repo/Canvas Sources/Assignment2Data-1/Assignment2Data/X_train.npy`。
- 形状：训练 [32000, 28, 28, 3]；测试 [8000, 28, 28, 3]。
- 拆分：fit 25600，validation 6400，test 8000；索引指纹匹配 V1：True；fit/validation 不重叠：True。
- fit SHA-256 `191d1629061294ebe7e01fe7a79ac57739fced43795161a0c6b821241311c571`；validation SHA-256 `c07d9573b52ee95cb6bd73390fde64f9c2dccd1c2ab14c244a479b1aa0dd3718`。
- 精确图像字节哈希跨训练/测试重复数：0（若非零，需按源数据现状报告）。
- 容器网络模式 `none`；仓库挂载只读、`reproduction_v2/runs` 可写，挂载明细见 `reference/docker_runtime_limits.json`。
- 原 Notebook 源码执行顺序与实际执行副本见每个 `executed.ipynb`；末尾标记为 `reproduction_v2_audit_only` 的附加 Cell 只导出已生成的预测，不参与训练与调参。
- NumPy `float32`、训练范围决定的 255 固定缩放、MLP/NB 2352 维和 CNN RGB 结构来自原 Notebook 代码；V2 运行副本的输出核对见各执行日志。
- 模型选择用验证 Macro-F1。测试集仅用于冻结参数和 epoch 后的最终预测；未用于 Early Stopping。

- 独立指标公式：`f1_score(y_true, y_pred, labels=np.arange(9), average='macro', zero_division=0)`；Accuracy 和 Balanced Accuracy 同由 sklearn.metrics 对保存预测重算。
- Strict reproduction 完整执行原始 Cell；另做了标记为 `final_only` 的可选跳过搜索对照，结果见 `05_difference_analysis.md`。Compatibility-assisted execution 未使用、未运行。

## 发现

- **MEDIUM** mlp/cnn: Original plotting cells embed V1 search rows, and final-result CSV validation fields repeat V1 frozen-selection constants. V2 search comparison uses newly written search_results.csv only.
- **LOW** v1 records: V1 exact prediction arrays and numeric confusion matrices are not present in Git; V1 class reports are rounded saved output. V2 exports full predictions and numeric matrices.
- **INFO** mlp: Run interrupted by user-acknowledged manual Docker Desktop restart; excluded from model failure assessment. Partial logs preserved.
- **MEDIUM** mlp: Class 6 Normal colon mucosa f1 differs by 0.0742 (V1 0.1322, V2 0.0580); investigate class-level shift.
- **MEDIUM** cnn: Class 2 Debris recall differs by 0.1266 (V1 0.2645, V2 0.3911); investigate class-level shift.
- **MEDIUM** cnn: Class 2 Debris f1 differs by 0.1042 (V1 0.4024, V2 0.5066); investigate class-level shift.
- **MEDIUM** cnn: Class 7 Cancer-associated stroma recall differs by 0.0762 (V1 0.4330, V2 0.5092); investigate class-level shift.
- **MEDIUM** cnn: Class 7 Cancer-associated stroma f1 differs by 0.0588 (V1 0.4467, V2 0.5055); investigate class-level shift.
