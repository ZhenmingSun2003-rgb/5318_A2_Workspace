# COMP5318 A2 — V3 最终模型整合

本目录是 A2 项目的**正式 V3 代码整合工作区**，用于在不改写 V1 原始模型与 V2 历史证据的前提下，形成符合 Canvas Notebook 模板的统一实现、完整评估流程和可移植的 Docker CPU 复现环境。

**完成状态：** 统一 Notebook、五个模型的最终训练与评估、Docker 封装、自动化检查以及执行证据均已完成；正式报告及个人 Reflection 仍属于独立的提交前工作。

## 1. 本目录提供什么？

| 文件 / 目录 | 用途 |
|---|---|
| [`COMP5318_A2_Integrated.ipynb`](COMP5318_A2_Integrated.ipynb) | 按官方五章节模板整合的英文 Notebook |
| [`Dockerfile`](Dockerfile) | 构建固定版本的 Python 3.11.11 / TensorFlow CPU 环境 |
| [`compose.yaml`](compose.yaml) | 禁用容器网络、只读挂载仓库、为结果提供独立写入区域 |
| [`scripts/run_v3.py`](scripts/run_v3.py) | 检查结构与语法、从全新 Jupyter Kernel 执行 Notebook、验证输出 |
| [`reports/01_validation_and_submission_readiness.md`](reports/01_validation_and_submission_readiness.md) | 三次真实 CI 验证、V2/V3 数值对照、Canvas 要求与剩余事项 |
| `outputs/` | 运行时生成的执行记录、图表、预测、指标和模型文件；不会提交到 Git |

三个课程必做模型为 **GaussianNB、MLP、CNN**；**Dummy 和 Nearest Centroid** 是额外的辅助基线。Notebook 也包含课程模板规定的五个主要章节：

1. Data loading, exploration, and preprocessing（加载、探索与预处理）
2. Algorithm design and setup（算法设计与初始化）
3. Hyperparameter tuning（超参数搜索）
4. Final models（最终独立训练与评估）
5. AI Acknowledgement（AI 使用声明）

Notebook 本身保留英文结构和术语，以便用于课程代码提交；本 README 提供中文操作说明。

### 来源与整合原则

V3 复用了 `../archive/v1/notebooks/` 下三位模型负责人的已完成实现，保留原有模型架构、预处理假设、参数选择和最终训练轮次。共有的数据加载、验证集划分、统一指标、比较图表、实验来源记录不再各自重复实现。

- 原始数据目录：`../Canvas Sources/Assignment2Data-1/Assignment2Data/`。
- 训练 / 测试：`32,000 / 8,000` 张，九分类，`28 × 28 × 3` RGB。
- 从原训练集分层划分 `25,600` 张 fit / `6,400` 张 validation。
- 随机种子：`5318`；划分索引 SHA-256 与 V2 审计记录核对一致。
- 使用训练数据所确定的固定像素缩放；传统模型与 MLP 展平为 `2,352` 维，CNN 保留四维图像张量。
- 以 **Validation Macro-F1** 选参，禁止利用 Canvas Test 集进行调参。
- 最终模型使用**全部 32,000 张原训练图像**重新拟合，独立于调参代码单元。

## 2. V2 兼容环境

使用与 V2 相同的基本环境定义：

| 项目 | 固定设置 |
|---|---|
| 基础镜像 | `python:3.11.11-slim-bookworm` |
| 平台 | `linux/amd64` |
| Python | `3.11.11` |
| NumPy | `1.26.4` |
| pandas | `2.2.3` |
| scikit-learn | `1.5.2` |
| SciPy | `1.14.1` |
| TensorFlow | `2.17.1` |
| Keras | `3.6.0` |
| Matplotlib | `3.9.2` |
| 随机种子 | `5318` |
| 设备与线程 | 仅 CPU、4 CPU 配额、10 GB 内存限制、TensorFlow 确定性运算 |

镜像使用的依赖清单是 V2 运行后记录的**完整解析版本列表** `../reproduction_v2/reference/requirements-v2-resolved.txt`，而不是重新选择浮动依赖版本。

Docker 内部 `network_mode: none`；原始仓库挂载为**只读**，仅结果目录单独挂载可写。这样可以降低运行过程中意外修改源数据、Notebook 或历史审计证据的风险。

注意：**锁定软件版本不等于跨硬件逐位相同**。CPU 运算库、执行平台和底层数值差异仍可能改变神经网络训练轨迹；详见第 5 节。

## 3. 从仓库根目录启动

**以下全部命令都要在 `5318_A2_Workspace/` 仓库根目录执行。**

### 3.1 构建环境

```bash
docker compose -f integration_v3/compose.yaml build --pull
```

### 3.2 静态验证（不进行训练）

```bash
docker compose -f integration_v3/compose.yaml run --rm integrate --validate
```

主要检查 Notebook 格式、五个 Canvas 章节顺序、Python 代码编译、模型来源单元、Canvas NPY 文件以及必要的 V2 证据文件。

### 3.3 正常执行（推荐）

```bash
docker compose -f integration_v3/compose.yaml run --rm integrate --execute
```

默认执行的流程是：

1. 用全新 Kernel 加载 Canvas 数据并校验固定划分。
2. 展示预处理样例和统一开发数据统计。
3. 读取 V2 已经**真实执行过**的搜索记录，呈现参数与验证指标，但不重复进行耗时网格搜索。
4. 分别训练冻结参数的 GaussianNB、MLP、CNN，另外训练 Dummy 与 Nearest Centroid 基线。
5. 仅在模型冻结后对原始测试集进行预测，计算当前运行的 Accuracy、Macro-F1、Balanced Accuracy 及逐类指标。
6. 生成混淆矩阵、模型对比图、运行环境信息与历史 V2 指标对照。
7. 将实际执行的 Notebook（含图表输出）和结构化结果写入 `integration_v3/outputs/`。

**尤其注意：** 默认显示的 V2 网格搜索结果是**历史调参证据**；本次最终训练、预测及测试指标必须从当前执行重新产生，绝不把 V2 测试数字当成新实验成果。

### 3.4 需要重新搜索全部参数时（可选）

```bash
docker compose -f integration_v3/compose.yaml run --rm integrate --execute --tune
```

此模式会运行三种主要模型**每种 8 组候选参数**的搜索，并标明是本次新执行的结果。MLP 与 CNN 各搜索至少三个不同超参数。搜索会增加计算时间，但最终模型单元依旧使用原先冻结的参数，**不会自动根据新 Test 成绩更换配置**。

### 3.5 在 Jupyter 中运行

可以从仓库根目录使用相同版本的 Python Kernel 打开 `integration_v3/COMP5318_A2_Integrated.ipynb`。如果脱离仓库单独交给 Canvas，Notebook 也支持相邻的 `Assignment2Data/` 目录；必要时通过 `A2_DATA_DIR` 指定四个 NPY 文件的位置。

可用环境变量：

- `A2_DATA_DIR`：Canvas 原始 NPY 所在目录；
- `V3_OUTPUT_DIR`：Notebook 运行结果的可写目录；
- `V3_RUN_TUNING=1`：在交互执行时重新运行调参网格。

不要让两个并行容器同时写入相同的 `outputs/` 路径，以免相互覆盖实验输出。

## 4. 模型设置和参数证据

| 模型 | V2 严格复现 Test Macro-F1 | V2 验证搜索最优 epoch | 实际冻结的最终 epoch |
|---|---:|---:|---:|
| Dummy | 0.028438 | 不调参 | 不适用 |
| Nearest Centroid | 0.410469 | 不调参 | 不适用 |
| GaussianNB | 0.385748 | 不适用 | 不适用 |
| MLP | 0.438672 | **9** | **10** |
| CNN | 0.723255 | **12** | **11** |

主要模型冻结设置：

- **GaussianNB**：`var_smoothing = 1e-6`。
- **MLP**：`hidden_units = 256`、`learning_rate = 0.001`、`dropout_rate = 0.0`、`epochs = 10`。
- **CNN**：`base_filters = 16`、`learning_rate = 0.001`、`dropout_rate = 0.3`、`epochs = 11`。

MLP/CNN 的**最终 epoch 10/11 源自 V1 冻结设置**；V2 新搜索结果对应的 9/12 并未用来替换 V2 严格复现的最终模型轮次。V3 沿用该实验协议，以便和 V2 直接对照。任何变更都应作为**明确标注的新实验**，而不应在看过测试指标后悄悄更改。

## 5. 已完成的 Docker 实际验证

V3 已通过三次 GitHub Actions 全流程执行，包含 Docker 构建、Notebook 静态检查、五个模型独立训练和测试评估：

| 验证 | 状态 | 重要结论 |
|---|---|---|
| [CI 第 1 次](https://github.com/ZhenmingSun2003-rgb/5318_A2_Workspace/actions/runs/40624341311) | PASS | 全部模型执行成功；MLP/CNN 与 V2 存在数值差异 |
| [CI 第 2 次](https://github.com/ZhenmingSun2003-rgb/5318_A2_Workspace/actions/runs/40624494612) | PASS | 完成独立运行兼容性改进；模型指标与第 1 次一致 |
| [CI 第 3 次（最新）](https://github.com/ZhenmingSun2003-rgb/5318_A2_Workspace/actions/runs/40625793593) | PASS | 五模型测试指标与 V2 一致；执行 Notebook 成功保留 **7 张内嵌图表** |

最新一次验证实际得到：

| 模型 | V3 Test Accuracy | V3 Test Macro-F1 |
|---|---:|---:|
| Dummy | 0.146750 | 0.028438 |
| Nearest Centroid | 0.430250 | 0.410469 |
| GaussianNB | 0.415500 | 0.385748 |
| MLP | 0.489250 | 0.438672 |
| CNN | **0.739250** | **0.723255** |

**不要将第 3 次的数值一致理解为 Docker 可以保证在所有机器上绝对复现。** 第 1、2 次的 CNN Macro-F1 为 `0.683125`（V2 为 `0.723255`），MLP Macro-F1 为 `0.443158`（V2 为 `0.438672`）。在软件版本、数据拆分及参数记录一致的前提下，CPU 底层数值计算路径是可能原因之一，但目前没有充分证据隔离出唯一根因。

完整的逐次指标、差异及归因限制见 [V3 验证审计](reports/01_validation_and_submission_readiness.md) 和 [V1/V2 差异分析](../reproduction_v2/reports/05_difference_analysis.md)。

## 6. 运行产物和证据链

默认写入 `outputs/` 的典型文件：

| 文件 | 内容 |
|---|---|
| `executed.ipynb` | 当前真正运行过、保留单元格输出和内嵌图表的 Notebook |
| `run_status.json` | 执行状态；失败时记录错误信息 |
| `environment.json` | Python、库版本和运行设备信息 |
| `split_fingerprints.json` | 训练/验证索引 SHA-256 |
| `summary.json` | 当前五个模型的测试结果与证据来源 |
| `model_comparison.csv` / `model_comparison.png` | 五模型统一对照表与图 |
| `per_class_scores.csv` | 每一模型、每一类别的 Precision / Recall / F1 |
| `v3_vs_v2_historical.csv` | 当前 V3 与历史 V2 指标差异 |
| `epoch_provenance.csv` | V1 冻结 epoch 与 V2 搜索 epoch 的来源对照 |
| `validation_selection_summary.csv` | 调参结果摘要，并标明历史或新执行来源 |
| `confusion_*.csv`、`predictions_*.npy` | 混淆矩阵与模型的当次预测结果 |
| `mlp/`、`cnn/` | 模型训练历史、图表及其余具体输出 |

这些文件主要是**运行产物**，不应因方便而全部提交到 Git 仓库。历史可核验证据已通过 CI Artifacts 和相关审计文档保存。

## 7. Canvas 作业提交要求与注意事项

依照 `Canvas Sources/COMP5318-assignment2-Sem2-2026-2.pdf`，最终需提交：

1. **报告 PDF**：`A2-report-SID1-SID2-SID3-SID4.pdf`
2. **带执行输出的 Notebook**：`a2-code-SID1-SID2-SID3-SID4.ipynb`
3. **Notebook 的 PDF 导出版**：`a2-code-SID1-SID2-SID3-SID4.pdf`

每位组员需要在报告中写自己的 Reflection，并在 Notebook 和报告中如实声明 AI 工具的使用方式。Notebook 里的 Group Number `163` 和四位 SID 来源于先前成员文件，**最终提交前仍需组员核实**。

截止时间按 PDF 记录为 **2026 年 10 月 30 日（星期五）23:59**，如果 Canvas 有后续通知，以最新要求为准。

### 当前剩余的人工审查

- [x] 按 Canvas 模板整合三种必做模型和两个辅助基线
- [x] 同步数据读取、预处理、随机划分、统一评估与调参依据
- [x] 沿用 V2 固定软件版本并建立 Docker 运行入口
- [x] 三次完整 CI 执行成功，并保留指标差异历史
- [x] 在执行版 Notebook 中保留图表与实验输出
- [ ] 由全体组员核对学号、实验文字、结果表和引用
- [ ] 完成最终 Report、每人的 Reflection 与 AI Acknowledgement 审阅
- [ ] 核对正式 Notebook PDF 与 Canvas 提交内容

**范围声明：** V3 已完成的是模型整合和可复现代码封装，不能代替独立的最终报告撰写，也不意味着已在 Canvas 提交作业。V1 原始源码、V2 复现报告和 Canvas 数据均应继续作为只读历史证据保留。
