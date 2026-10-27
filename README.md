# COMP5318 A2 — V3 Integration Workspace

当前仓库进入 **V3 · Integration（最终整合）** 阶段。V1 原始 Notebook、EDA 和开发辅助资料已归档，V2 Docker 复现证据保持不变；根目录继续保存学校提供的共享数据。**V3 最终 Notebook 尚未创建/完成。**

## Repository structure

```text
5318_A2_Workspace/
├── Canvas Sources/              # 学校提供的原始 NPY 与要求；各阶段共享、不修改
├── archive/v1/
│   ├── notebooks/              # V1: baseline、Naive_Bayes、MLP、CNN
│   ├── notebooks_zh/           # 中文 Baseline
│   ├── eda_lab/                # 原有 Streamlit EDA
│   ├── scripts/                # V1 工具脚本
│   ├── requirements.yaml       # V1 Conda 环境
│   ├── README_legacy.md       # 迁移前 README 原文快照
│   └── README.md              # V1 归档索引
├── reproduction_v2/            # Docker 统一环境、审计脚本、报告与已上传实验结果
│   ├── reference/
│   ├── results/
│   ├── reports/
│   └── scripts/
├── integration_v3/             # 活跃 V3 整合区（当前为准备工作区）
└── README.md
```

## V3 integration rules

- 统一从 `Canvas Sources/Assignment2Data-1/Assignment2Data/` 读取原始图像及标签，不覆盖训练集/测试集。
- 参考 [V1 Notebook 源码](archive/v1/notebooks/) 和 [EDA 工具](archive/v1/eda_lab/)，最终要求模型为 Gaussian Naive Bayes、MLP 和 CNN；Dummy 和 Nearest Centroid 只作为辅助基线。
- 固定 Seed `5318`，从原训练集创建分层 80/20 开发划分，以 Validation Macro-F1 选参，参数冻结后再评估课程 Test 集。
- 以 [V2 最终复现摘要](reproduction_v2/reports/04_final_reproduction_summary.md)、[V1/V2 对比](reproduction_v2/reports/02_model_reproduction_comparison.md) 和 [差异分析](reproduction_v2/reports/05_difference_analysis.md) 作为可审计结果来源。特别注意：V1 冻结的 Validation 常量不等于 V2 实测验证结果。
- 在 `integration_v3/` 开展最终英文 Notebook、报告、模型比较图表与声明的整合。不要直接覆写封存的 V1/V2 成果。

## Reuse the V1 EDA

```bash
conda env create -f archive/v1/requirements.yaml
conda activate comp5318-a2
streamlit run archive/v1/eda_lab/app.py
```

## Docker V2 reproduction

从仓库根目录运行以下命令；脚本现已适配 `archive/v1/notebooks/` 中的原始 Notebook：

```bash
docker compose -f reproduction_v2/compose.yaml build
docker compose -f reproduction_v2/compose.yaml run --rm reproduce --audit
docker compose -f reproduction_v2/compose.yaml run --rm reproduce --model baseline
# 可选完整复跑：--model naive_bayes / mlp / cnn，或 --all
```

详细说明：[V1 归档](archive/v1/README.md) · [V2 Docker 使用说明](reproduction_v2/README.md) · [V3 整合入口](integration_v3/README.md)。

历史 V2 Test Macro-F1：GaussianNB `0.385748`、MLP `0.438672`、CNN `0.723255`。既有实验的跨平台数值差异应如实披露，不能把这些记录当作所有硬件上必然相同的输出。

**保护原则**：`Canvas Sources/`、`archive/v1/notebooks/`、`reproduction_v2/reference/`、`reproduction_v2/results/` 和 `reproduction_v2/reports/` 都视为历史或输入证据，V3 新工作单独保存在 `integration_v3/`。
