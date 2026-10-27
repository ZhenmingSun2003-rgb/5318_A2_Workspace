# COMP5318 Assignment 2 · 小组协作工作区

欢迎大家使用这个工作仓库。本仓库主要服务于 **COMP5318/COMP4318 Assignment 2：PathMNIST 图像分类**的组内开发、数据探索与结果交流，并不等同于最终交给 Canvas 的文件包。我们在这里保留各自工作的完整过程，最后再整理成统一的 Notebook 与 PDF 报告。

> **研究对象提醒：** A2 使用的是 Canvas 提供的 **PathMNIST 结直肠组织病理 RGB 图像子集（28×28）**，并非 A1 探索过的大米形态图像。两次作业可以延续严谨的评估流程，但数据性质与研究结论不可混用。课程要求的三种模型为：前六周自选算法、MLP、CNN。仓库另设的 baseline 只做**辅助比较**，不能替代其中任何一个模型。

## 1. 文件结构

```text
5318_A2_Workspace/
├── Canvas Sources/                           # Canvas 原始材料，请保留原样
│   ├── COMP5318-assignment2-Sem2-2026-2.pdf
│   ├── COMP5318-assignment2-template-notebook-1.ipynb
│   └── Assignment2Data-1/Assignment2Data/
│       ├── X_train.npy
│       ├── y_train.npy
│       ├── X_test.npy
│       └── y_test.npy
├── baseline.ipynb                             # 额外的简明参考 Baseline（英文）
├── CNN.ipynb                                  # CNN 负责人
├── MLP.ipynb                                  # MLP 负责人
├── Specific_Algorithm_Rememeber_to_change_name.ipynb
│                                              # 前六周算法负责人：确定算法后请改名
├── notebooks_zh/
│   └── baseline_中文版.ipynb                  # 中文审阅与交流用
├── eda_lab/
│   ├── app.py                                 # 中文可视化工具，仅供内部探索
│   └── README.md                              # 工具详细说明
├── scripts/
│   ├── execute_baseline.py                    # Notebook 运行及中英文输出同步
│   └── smoke_eda.py                           # EDA 页面基础启动与渲染检查
├── .github/workflows/
│   ├── run_baseline.yml                       # 自动执行并保存 Baseline 的真实输出
│   └── eda_smoke.yml                          # EDA 应用自动冒烟测试
├── requirements.yaml                         # Conda 运行环境配置
├── .gitignore
└── README.md                                  # 当前说明
```

我们优先以 **Canvas 原始 PDF 和 Notebook 模板**为准。英文 Notebook 维持原模板的五个主要章节及三种算法的小节，以便将来合并。每个人只需在自己负责的 Notebook 内实施模型；其他模型的小节保留模板定位即可。**具体分工依照小组已经协商好的安排**，不按任何参考指南重新分配。

## 2. 数据与统一实验口径

1. **数据唯一来源：** 使用仓库 `Canvas Sources/Assignment2Data-1/Assignment2Data/` 的四个 NPY 文件。请勿从官网重新下载 PathMNIST 来替换课程子集；也请勿移动、覆盖或手动修改这些原始文件。
2. **原始划分：** Canvas 已提供训练集和测试集。所有模型都必须保留原始测试集，开发期间不得利用测试集来选模型、调参、早停或决定预处理。
3. **统一验证集：** 在**原始训练集**内部通过 `train_test_split(..., test_size=0.20, stratify=y_train, random_state=5318)` 进行固定、分层的训练/验证划分。不同模型使用同一批索引（不各自重新抽样）。如需在搜索后合并训练和验证进行最终重新训练，应提前固定相关选择，并在 Notebook 写明。
4. **随机种子：** 全员统一使用**纯数字整数 `5318`**；请勿写作 `5318L`。即使种子相同，不同硬件和框架版本的结果仍可能有微小差异。
5. **图像接口：** 优先保留 RGB 通道结构。MLP 与传统方法可以展平（28×28×3 → 2352 特征），CNN 保留 `(N, 28, 28, 3)`。训练图像像素若原本为 0–255，转换 `float32 / 255`；如果已是 0–1，则不要重复除以 255。任何数据驱动变换（例如 StandardScaler、PCA）必须只在训练子集上拟合。
6. **类别与公平性：** 类别顺序、标签编号及测试指标计算方法保持一致。若因显存/计算限制而使用训练子集或改变分辨率，记录实际样本量和原因；这种结果与完整训练集模型的比较必须注明边界。

**建议的统一评价体系：** 以**验证集 Macro-F1** 为主要模型选择指标，Accuracy 与 Balanced Accuracy 为辅助；最终使用同一原始测试集汇报 Accuracy、Macro-F1、Balanced Accuracy、逐类 Precision/Recall、混淆矩阵。同时记录每个超参数组合的训练与验证用时、各次最终模型的训练与测试预测用时、神经网络参数量/训练轮数（适用时）。尽量在同一硬件环境下讨论耗时差异；跨设备计时仅作为环境相关观察。

Baseline 内有两种**额外的固定参考方法**：多数类 Dummy 分类器、RGB 展平特征上的最近质心分类器。它们用来为其他三个模型提供参考点，**并不构成前六周自选算法**。这两个参考方法不进行课程意义上的超参数搜索。请勿将它们的简单性能差异写成三种要求模型的调参成果。

## 3. 环境安装与 Notebook 运行

推荐安装 Miniconda/Anaconda，然后在**仓库根目录**执行：

```bash
conda env create -f requirements.yaml
conda activate comp5318-a2
python -m ipykernel install --user --name comp5318-a2 --display-name "Python (COMP5318 A2)"
jupyter lab
```

推荐采用 `Python 3.11`，主要依赖包括 NumPy、scikit-learn、pandas、Matplotlib、Streamlit、Plotly，以及用于 **MLP/CNN** 的 TensorFlow/Keras。详见 `requirements.yaml`。首次安装 TensorFlow 可能需要较长时间；CPU 可以运行小型网络，但训练效率取决于机器配置。部分硬件或操作系统的 TensorFlow GPU 支持需要额外的平台配置。最终提交代码必须能够在本地运行。

运行独立 Notebook 时，请把工作目录设在**仓库根目录**（或者依靠 Notebook 自带的相对路径搜索）；按照单元格从上到下执行。若环境有冲突，先核查当前 kernel 及 `requirements.yaml`，不要直接改动 `Canvas Sources`。

## 4. 组内中文 EDA 可视化工具

这是一个**独立于最终提交代码**的中文 Streamlit 图像探索界面，集中帮助大家了解 NPY 的四维结构、类别分布、图像纹理和 RGB 颜色强度等情况，不用于正式模型评估。

在仓库根目录执行：

```bash
conda activate comp5318-a2
streamlit run eda_lab/app.py
```

运行后浏览器打开工具页面。提供以下探索方向：

- **数据概览：** 四个 NPY 文件的维度、dtype、类别数量与原始训练集分布；
- **样本图库：** 按真实训练类别查看 RGB 病理组织图像，理解类别可能的形态差异；
- **色彩强度：** 训练样本的 RGB 直方图及各类通道均值/标准差，用于讨论强度和颜色差异；
- **低维投影：** 使用抽样训练图像 PCA 生成二维散点图，观察相似性、重叠和类间可分性；
- **数据质量：** 对抽样训练图像进行基础像素范围与异常值检查，并总结可解释的局限。

标签中文译名用于理解，不替代 MedMNIST 官方九类别映射。**测试集内容默认不进入探索图表**：仅在选中明确的开关时展示其结构和标签概况；不要把工具中观察的测试集特征用于调整模型。数据的原始公开版本与课程子集的具体来源/切片或患者身份无法仅凭这四个数组逐一核查。

使用过程中如想分享发现，可以截取工具的示意图或将观察写到小组讨论中；正式报告中的图表、结论与数值请对应到提交 Notebook 可复现的实际输出。

更具体操作详见 [EDA 工具说明](eda_lab/README.md)。

## 5. 协作方式与后续工作流

我们采用**一个主分支的轻量协作方式**。组员可以**直接在 `main` 修改并提交自己负责的 Notebook**，不要求创建 branch。为了减少冲突，请尽量避免同时修改同一个 Notebook；若要修改其他负责人的文件，先在小组中沟通。原始 Canvas 文件请保持不变。

每位负责模型的同学可按以下顺序完成自己的模块：

1. 在独立 Notebook 完成真实数据探索、与模型相适应的预处理和可运行初始模型；
2. **完成调参并保存完整输出**：清楚记录搜索范围、每种参数组合的验证结果、运行时间、选中参数的依据；MLP、CNN 各自至少搜索三种不同超参数；
3. 将**真实搜索选定的最佳参数写在独立、可直接运行的代码单元**，再独立重新构建并训练最终模型；保证**跳过耗时搜索单元也能运行之后的最终模型**；
4. 对冻结配置执行最终测试，保存准确率、Macro-F1、混淆矩阵、训练与预测时间、必要的训练曲线等；**请将运行输出实际保留在各自 `.ipynb` 里，提交前不要一键清空输出**；
5. 本人检查 Notebook 的从头执行顺序、术语说明、结果解读、实验限制和 AI 使用声明，再提交到 `main` 供其他组员复核。

建议每位模型负责人提供一个简洁的最终对比记录：

| 字段 | 说明 |
|---|---|
| Model | 算法名称及关键架构 |
| Best hyperparameters | 真实实验确定的参数，不使用虚构值 |
| Validation Macro-F1 | 主要选参指标 |
| Test Accuracy / Macro-F1 / Balanced Accuracy | 冻结参数后原始测试集实测 |
| Fit seconds / Test predict seconds | 分开计时，并注明设备和数据范围 |
| Search log / Time | 所有试验组合结果及耗时，不仅是最佳值 |
| Notes | 样本量、预处理、种子、局限与异常情况 |

**后续整合由仓库负责人组织：** 待三位模型负责人各自完成真实训练、调参、独立最终评估，并**在各自 Notebook 中保存相应输出**后，再把三个必做模型及必要的 EDA 与对比图表整合为**一个统一的英文 Notebook**。接着根据作业指定标题完成并校对 PDF 报告与 Notebook PDF。全体组员需要写各自的 Reflection，并如实确认 AI Acknowledgement。

按照当前 Canvas 作业说明，最终需提交一份报告 PDF、一份 `.ipynb` 及对应 Notebook PDF，文件名需使用组员学号，提交时再统一填写。作业说明显示截止日期为 **2026 年 10 月 30 日 23:59**；以 Canvas 页面最终通知和时区为准。

## 6. 可复现性、AI 说明与自动检查

课程强调：**Notebook 最终输出应保留、运行过程能够重现、搜索单元可以跳过而不破坏最终模型部分**。仓库包含 `.github/workflows/run_baseline.yml`，用于在 GitHub Actions 环境可用且有写入权限时，对英文 Baseline 执行真实 Canvas 数据，并将产生的结果同步到中文版 Notebook。该自动检查是额外辅助，**成功前不能当作已完成的实测验证**。若动作运行失败，请查看 Actions 日志并在本地复跑；不要填入估算成绩。脚本是 `scripts/execute_baseline.py`。此外 `eda_smoke.yml` 在 EDA 工具更新时执行真实 Canvas 数据上的页面冒烟测试，辅助发现语法、页面渲染或依赖错误。

本仓库 Notebook 的初始结构、Baseline 实现、EDA 工具及这些协作说明由 **ChatGPT（OpenAI）** 辅助起草。最终提交时须根据实际使用情况，在**Notebook 和报告中**完整、准确填写 AI 使用声明，并对代码、结果和学术论证进行小组审查。

**参考资料：** Canvas 任务说明及原始模板（见 `Canvas Sources/`）；MedMNIST 官方类别定义 https://github.com/MedMNIST/MedMNIST/blob/main/medmnist/info.py 。

谢谢大家配合！我们把各自的 Notebook 做完整、把真实结果留下来，最后的整合和结果分析就会更顺畅。

## V2 Docker Reproduction

`reproduction_v2/` 保存只读原仓库挂载下的独立复现脚本、V1 快照和 V2 报告。实验基于 commit `0f2ffeaa118a82a39f4d2585ceca6e1d691e5036`；镜像使用 `python:3.11.11-slim-bookworm`（linux/amd64）、NumPy 1.26.4、scikit-learn 1.5.2、TensorFlow 2.17.1、Keras 3.6.0，CPU 运行。

从仓库根目录执行 `docker compose -f reproduction_v2/compose.yaml build --pull`、`docker compose -f reproduction_v2/compose.yaml run --rm reproduce --audit` 和 `docker compose -f reproduction_v2/compose.yaml run --rm reproduce --all`。报告见 `reproduction_v2/reports/`，逐次执行日志与预测保存在 Git 忽略的 `reproduction_v2/runs/`。

五个模型均完成严格执行及独立指标复核。Dummy、Nearest Centroid、Gaussian NB 与 V1 保存结果在显示精度内一致；MLP Test Macro-F1 为 0.438672（V1 0.449128，WARNING），CNN 为 0.723255（V1 0.697860，WARNING）。跨平台和依赖版本差异限制神经网络结果及耗时的直接等同性；训练轨迹、逐类差异与跳过搜索对照见 `reproduction_v2/reports/05_difference_analysis.md`，一次人工重启 Docker 的中断记录见 `reproduction_v2/reports/03_experiment_integrity_audit.md`。

供小组审阅的实测产物已整理在 `reproduction_v2/results/`：`strict_*` 是完整搜索的执行副本、日志、预测与指标，`final_only_*` 是跳过搜索的对照，`interrupted_1` 保留人工重启造成的中断记录。`manifest.json` 记录逐文件 SHA-256，`package_verification.json` 证实上传的预测标签能够重算已报告的测试指标；大型模型权重和临时缓存不在上传包内。
