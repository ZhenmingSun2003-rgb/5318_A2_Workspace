# COMP5318 A2 — V3 模型整合与可复现工作仓库

本仓库用于悉尼大学 **COMP5318 / COMP4318 Assignment 2：PathMNIST 图像分类**项目的团队协作、模型实验、结果核查和最终代码整合。

**当前状态：V3 模型整合与 Docker 封装已完成，并通过三次 GitHub Actions 全流程验证；正式作业报告及个人 Reflection 仍需小组最终确认。**

V3 主工作区位于 [`integration_v3/`](integration_v3/)，其中包含按照 Canvas 官方模板整合的英文 Notebook、Docker 运行环境、验证脚本和实验审计报告。原始数据、V1 成员模型和 V2 复现证据均保留，没有因整合而被覆盖。

## 一、仓库结构

```text
5318_A2_Workspace/
├── Canvas Sources/                         # 学校提供的作业 PDF、Notebook 模板、四个 NPY 原始数据
├── archive/
│   └── v1/
│       ├── notebooks/                     # 原始成员 Notebook：GaussianNB、MLP、CNN、Baseline
│       ├── notebooks_zh/                  # 历史中文版参考资料
│       ├── eda_lab/                       # Streamlit EDA 可视化工具
│       ├── scripts/                       # V1 辅助脚本
│       └── README.md                      # V1 归档说明
├── reproduction_v2/
│   ├── reference/                         # 已记录的环境、版本与源文件校验信息
│   ├── reports/                           # V1/V2 对照、实验完整性与差异归因审计
│   ├── results/                           # 历史真实运行结果、预测与指标
│   └── scripts/                           # V2 独立复现工具
├── integration_v3/
│   ├── COMP5318_A2_Integrated.ipynb       # V3 英文整合 Notebook（Canvas 五章节结构）
│   ├── Dockerfile                         # 基于 V2 固定版本构建的 CPU 环境
│   ├── compose.yaml                       # 禁用网络、只读挂载仓库、隔离输出
│   ├── scripts/run_v3.py                  # 静态检查 / 全新 Kernel 执行
│   ├── reports/                            # V3 实际验证与提交前审计
│   ├── outputs/                           # 执行时生成；已被 Git 忽略
│   └── README.md                          # V3 详细运行说明（中文版）
└── README.md
```

仓库目前研究的是 **Canvas 提供的 PathMNIST 病理组织图像子集**，并非 A1 的大米图像数据，也不等于完整的公开 PathMNIST 数据集。

## 二、实验内容与数据协议

课程要求的三个主要模型为：

1. **Gaussian Naive Bayes（高斯朴素贝叶斯）**：前六周课程算法。
2. **MLP（多层感知机）**：全连接神经网络。
3. **CNN（卷积神经网络）**：保留图像空间结构的卷积分类器。

另外加入 **Dummy Classifier（多数类预测）** 和 **Nearest Centroid（最近质心）** 两个辅助基线，用于解释模型的相对提升；它们不替代课程要求的三个模型。

- 原始 Canvas 数据：**32,000 张训练图像 + 8,000 张独立测试图像**，每张为 `28 × 28 × 3` RGB 图像，共九类。
- 固定随机种子：`5318`。
- 开发阶段：仅从原训练集中分层划分 **25,600 张训练 / 6,400 张验证**；测试集不参与调参。
- 统一预处理：根据训练数据像素范围进行 `float32` 固定缩放；GaussianNB/MLP 使用 2,352 维展平特征，CNN 使用原始 RGB 空间结构。
- 主要调参依据：**Validation Macro-F1**；模型最终在全部 32,000 张原训练图像上独立重新训练。

## 三、V3 最新验证结果

V3 已在与 V2 固定软件版本一致的 Docker CPU 配置下，通过三次完整 CI 检查。**最近一次验证**（[GitHub Actions 执行记录](https://github.com/ZhenmingSun2003-rgb/5318_A2_Workspace/actions/runs/40625793593)）的独立训练结果如下：

| 模型 | 最新 V3 Test Accuracy | 最新 V3 Test Macro-F1 |
|---|---:|---:|
| Dummy | 0.146750 | 0.028438 |
| Nearest Centroid | 0.430250 | 0.410469 |
| GaussianNB | 0.415500 | 0.385748 |
| MLP | 0.489250 | 0.438672 |
| CNN | **0.739250** | **0.723255** |

本次五个模型的测试指标与 V2 严格复现结果一致，且成功在执行版 Notebook 中嵌入 **7 张当次生成的图表**。

**可复现性说明：** 前两次 CI 中，MLP/CNN 的数值结果与 V2 存在差异。Docker 能固定操作系统基础镜像、依赖版本、运行限制和执行流程，但无法保证不同 CPU 数值运算路径下神经网络训练结果逐位相同。三次结果及分析均已如实记录，不能只展示最后一次一致的结果。

详见 [V3 验证与提交准备审计](integration_v3/reports/01_validation_and_submission_readiness.md)。

## 四、使用 Docker 运行 V3

在**仓库根目录**执行：

```bash
# 1. 构建与 V2 兼容的固定版本 Docker 环境
docker compose -f integration_v3/compose.yaml build --pull

# 2. 检查 Canvas 章节结构、代码语法及必要文件
docker compose -f integration_v3/compose.yaml run --rm integrate --validate

# 3. 从全新 Kernel 重新训练五个最终模型并保存结果
docker compose -f integration_v3/compose.yaml run --rm integrate --execute

# 可选：额外重新运行三种主要模型各 8 组的调参搜索
docker compose -f integration_v3/compose.yaml run --rm integrate --execute --tune
```

默认 `--execute` **不会重新运行耗时的超参数网格搜索**：Notebook 使用经过 V2 实际执行的调参记录作为*历史选择证据*，但仍会重新训练所有最终模型、重新预测并计算当前运行指标。最终模型代码独立于调参单元。

结果默认输出到被 Git 忽略的 `integration_v3/outputs/`，包含执行后的 Notebook、指标表、分类报告、混淆矩阵、预测标签、图表与环境信息。镜像固定 Python 3.11.11、TensorFlow 2.17.1、Keras 3.6.0 等版本，并使用 V2 实际解析的完整依赖清单。

## 五、研究证据与版本说明

| 阶段 | 作用 | 保留原则 |
|---|---|---|
| V1 · Development | 各成员原始模型、EDA 与早期实验 | 只读归档，不覆盖 |
| V2 · Reproduction | 统一 Docker 环境、严格复现、差异审计 | 保留历史结果与来源 |
| V3 · Integration | 官方模板整合、统一评估、最终代码验证 | 活跃开发与交付区域 |

需要特别注意：V2 的新搜索结果显示 MLP 最优验证 epoch 为 **9**、CNN 为 **12**；V2 严格复现的最终模型仍沿用 V1 已冻结的 **10 / 11** 个 epoch。V3 继续保留这一冻结协议，避免事后利用 Test 成绩修改实验设置。Notebook 已区分历史搜索记录与当前执行结果。

相关资料：[V3 详细 README](integration_v3/README.md) · [V2 最终复现摘要](reproduction_v2/reports/04_final_reproduction_summary.md) · [V1/V2 差异分析](reproduction_v2/reports/05_difference_analysis.md) · [V1 归档说明](archive/v1/README.md)。

## 六、提交前仍需完成的工作

根据 Canvas 原始任务 PDF，最终需要**三个文件**：正式 Report PDF、保留执行输出的 `.ipynb` Notebook，以及对应的 Notebook PDF。文件名应按四位组员 SID 命名。

当前 V3 已交付的是**整合代码及可复现环境**，并不代表最终 Report 已完成。提交前请组员共同核对学号、报告中的实验数值、个人 Reflection、AI Acknowledgement 和引用来源。

**Canvas 任务文件所列截止时间：2026 年 10 月 30 日（星期五）23:59；如 Canvas 页面后续更新，以课程最新通知为准。**
