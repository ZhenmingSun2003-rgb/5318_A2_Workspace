# 00 复现前 V1 审计

- 读取时间：2026-10-27T16:26:51.895169+08:00
- HEAD：`0f2ffeaa118a82a39f4d2585ceca6e1d691e5036`（`main`）
- Clone reflog：`HEAD@{2026-10-27 16:23:09 +0800} clone: from https://github.com/ZhenmingSun2003-rgb/5318_A2_Workspace.git`。
- 远程：`https://github.com/ZhenmingSun2003-rgb/5318_A2_Workspace.git`
- 仅解析克隆时保存的 Notebook；此阶段没有训练或重新执行。

## 证据类别

A = 代码 Cell 保存的实际输出；B = Markdown 叙述；C = 源码中硬编码的历史记录；D = 原文件无法核实。A 也只能证明历史执行记录，不证明 V2 执行。

## baseline.ipynb

SHA-256: `0fdbb9a33ac7e73a246b6f173e4c33873f812ab54646f42cac1f28f932242ea7`；代码 Cell 10 个，已执行 10 个，错误输出 0 个。

历史环境见 Cell 4 (A)；数据形状见 Cell 6 (A)，归一化和 25,600/6,400 划分见 Cell 9 (A)。固定基线验证见 Cell 22 (A)，最终测试见 Cell 29 (A)；最近质心逐类报告见 Cell 30 (A)。

| 模型 | 验证 Accuracy / Macro-F1 / Balanced | 测试 Accuracy / Macro-F1 / Balanced | 最终训练 / 预测秒 | 来源 |
|---|---:|---:|---:|---|
| Dummy | 0.1467 / 0.0284 / 0.1111 | 0.1468 / 0.0284 / 0.1111 | 0.0009 / 0.0001 | A: Cell 22, 29，表格仅保留 4 位小数 |
| Nearest Centroid | 0.4222 / 0.4051 / 0.4237 | 0.4302 / 0.4105 / 0.4325 | 0.106 / 0.0648 | A: Cell 22, 29，表格仅保留 4 位小数 |

### 保存输出原文摘录

Cell 22, output 0 (display_data；A：保存输出):

```text
                           model  accuracy  macro_f1  balanced_accuracy  \
0  Nearest centroid (RGB pixels)    0.4222    0.4051             0.4237
1                  Most frequent    0.1467    0.0284             0.1111

   fit_seconds  prediction_seconds
0       0.0824              0.0670
1       0.0010              0.0001
```

Cell 22, output 1 (stream；A：保存输出):

```text
No hyperparameters are optimised here; validation is descriptive only.
Any future choice of assessed-model hyperparameters must use this validation split, not test-set performance.
```

Cell 29, output 0 (display_data；A：保存输出):

```text
                           model  \
0  Nearest centroid (RGB pixels)
1                  Most frequent

                                   frozen_parameters  accuracy  macro_f1  \
0  {'metric': 'euclidean', 'shrink_threshold': None}    0.4302    0.4105
1  {'constant': None, 'random_state': None, 'stra...    0.1468    0.0284

   balanced_accuracy  fit_seconds  prediction_seconds  train_samples  \
0             0.4325       0.1060              0.0648          32000
1             0.1111       0.0009              0.0001          32000

   test_samples  seed
0          8000  5318
1          8000  5318
```

Cell 29, output 1 (stream；A：保存输出):

```text
The reported test metrics are single-split reference measurements, not validation tuning scores.
```

Cell 30, output 0 (stream；A：保存输出):

```text
                                      precision    recall  f1-score   support

                             Adipose      0.668     0.960     0.788       873
                          Background      0.456     0.670     0.543       858
                              Debris      0.317     0.268     0.290       877
                         Lymphocytes      0.770     0.435     0.556       914
                               Mucus      0.300     0.577     0.394       737
                       Smooth muscle      0.508     0.283     0.363      1072
                 Normal colon mucosa      0.198     0.199     0.199       682
            Cancer-associated stroma      0.250     0.154     0.190       813
Colorectal adenocarcinoma epithelium      0.397     0.347     0.370      1174

                            accuracy                          0.430      8000
                           macro avg      0.429     0.433     0.410      8000
                        weighted avg      0.441     0.430     0.415      8000
```

Cell 30, output 2 (stream；A：保存输出):

```text
Interpretation caution: neither temporal nor patient-level grouping is verifiable from the supplied arrays alone.
Cross-machine elapsed times are not controlled hardware benchmarks.
```

### D：缺失或无法核实

- baseline 各模型参数数量未打印
- Dummy 逐类报告未保存
- baseline 划分索引哈希未打印

### nearest_centroid 逐类指标（A：保存的分类报告）

| 类别 | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| Adipose | 0.668 | 0.96 | 0.788 | 873 |
| Background | 0.456 | 0.67 | 0.543 | 858 |
| Debris | 0.317 | 0.268 | 0.29 | 877 |
| Lymphocytes | 0.77 | 0.435 | 0.556 | 914 |
| Mucus | 0.3 | 0.577 | 0.394 | 737 |
| Smooth muscle | 0.508 | 0.283 | 0.363 | 1072 |
| Normal colon mucosa | 0.198 | 0.199 | 0.199 | 682 |
| Cancer-associated stroma | 0.25 | 0.154 | 0.19 | 813 |
| Colorectal adenocarcinoma epithelium | 0.397 | 0.347 | 0.37 | 1174 |

## Naive_Bayes.ipynb

SHA-256: `b1a6bbcea36013dbd262759f64cd334ad9b331fbcf7badcf00e5ff828b98c064`；代码 Cell 8 个，已执行 8 个，错误输出 0 个。

Cell 5 (A) 保存数据形状与划分样本数；Cell 7 (A) 保存 255 缩放、2352 维和训练输入范围；Cell 15 (A) 保存 8 个 `var_smoothing` 搜索表，四位小数；Cell 18 (B) 描述 tie-break；Cell 22 (C 源码冻结 1e-6，A 输出) 保存完整训练/测试评价和逐类报告。

验证 0.4041 / 0.3749 / 0.4188；测试 0.4155 / 0.3857 / 0.4307（Accuracy / Macro-F1 / Balanced，A，四位小数）。训练 0.3792 秒，预测 0.9081 秒（A）。历史环境版本和精确混淆矩阵数据缺失 (D)。

### 保存输出原文摘录

Cell 11, output 0 (stream；A：保存输出):

```text
Initial GaussianNB: fit=0.2529s, validation=0.6211s, accuracy=0.4041, macro_f1=0.3749, balanced_accuracy=0.4188
```

Cell 15, output 0 (display_data；A：保存输出):

```text
  var_smoothing validation_accuracy validation_macro_f1  \
0         1e-12              0.4041              0.3749
1         1e-10              0.4041              0.3749
2         1e-08              0.4041              0.3749
3         1e-06              0.4041              0.3749
4         1e-04              0.4039              0.3748
5         1e-02              0.4028              0.3719
6         1e-01              0.4027              0.3597
7         1e+00              0.3345              0.2664

  validation_balanced_accuracy fit_seconds validation_seconds
0                       0.4188      0.2891             0.5245
1                       0.4188      0.2581             0.5315
2                       0.4188      0.2488             0.5279
3                       0.4188      0.2761             0.5173
4                       0.4186      0.2498             0.5244
5                       0.4172      0.2656             0.5292
6                       0.4161      0.2614             0.5601
7                       0.3494      0.2662             0.5292
```

Cell 22, output 0 (stream；A：保存输出):

```text
Final GaussianNB parameters: {'priors': None, 'var_smoothing': 1e-06}
Training time: 0.3792 seconds
Test prediction time: 0.9081 seconds
Test accuracy: 0.4155
Test macro F1: 0.3857
Test balanced accuracy: 0.4307

              precision    recall  f1-score   support

           0     0.6708    0.9381    0.7822       873
           1     0.6895    0.6445    0.6663       858
           2     0.1848    0.1026    0.1320       877
           3     0.4173    0.6214    0.4993       914
           4     0.3479    0.4749    0.4016       737
           5     0.4576    0.0756    0.1297      1072
           6     0.2702    0.2155    0.2398       682
           7     0.2731    0.6298    0.3810       813
           8     0.3871    0.1738    0.2399      1174

    accuracy                         0.4155      8000
   macro avg     0.4109    0.4307    0.3857      8000
weighted avg     0.4161    0.4155    0.3771      8000
```

### D：缺失或无法核实

- 历史环境版本/硬件没有保存输出
- 参数数量未保存
- 训练/验证索引哈希未打印
- 混淆矩阵数组仅以图像形式保存，无法可靠读取精确各格

### gaussian_nb 逐类指标（A：保存的分类报告）

| 类别 | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| 0 | 0.6708 | 0.9381 | 0.7822 | 873 |
| 1 | 0.6895 | 0.6445 | 0.6663 | 858 |
| 2 | 0.1848 | 0.1026 | 0.132 | 877 |
| 3 | 0.4173 | 0.6214 | 0.4993 | 914 |
| 4 | 0.3479 | 0.4749 | 0.4016 | 737 |
| 5 | 0.4576 | 0.0756 | 0.1297 | 1072 |
| 6 | 0.2702 | 0.2155 | 0.2398 | 682 |
| 7 | 0.2731 | 0.6298 | 0.381 | 813 |
| 8 | 0.3871 | 0.1738 | 0.2399 | 1174 |

## MLP.ipynb

SHA-256: `5297efd9faca2593d87d6304a93de411914fdece974c1f8609d6cd271057027f`；代码 Cell 11 个，已执行 11 个，错误输出 0 个。

环境 Cell 4 (A)；数据与索引指纹 Cell 6 (A)；8 次实际搜索日志 Cell 18 (A)；硬编码的历史绘图数据 Cell 19 (C)；冻结参数/epoch Cell 25 (C 常量，A 打印)；最终模型/逐类结果 Cell 27 (A)。

搜索输出识别到 8 组 trial；逐组至少保存参数与恢复后的验证 Macro-F1。

V1 验证 Accuracy / Macro-F1 / Balanced：0.46828125 / 0.424545 / 0.4624929838057703；V1 测试：0.496375 / 0.449128 / 0.477117。参数 604681.0，最终 10 epochs。

| Trial | 参数 | 验证 Macro-F1（历史运行输出，显示精度） | Cell / Output |
|---:|---|---:|---|
| 1 | `{'hidden_units': 128, 'learning_rate': 0.001, 'dropout_rate': 0.0}` | D | 18 / 0 起 |
| 2 | `{'hidden_units': 128, 'learning_rate': 0.001, 'dropout_rate': 0.3}` | 0.03407 | 18 / 17 起 |
| 3 | `{'hidden_units': 128, 'learning_rate': 0.0003, 'dropout_rate': 0.0}` | 0.40385 | 18 / 31 起 |
| 4 | `{'hidden_units': 128, 'learning_rate': 0.0003, 'dropout_rate': 0.3}` | 0.32889 | 18 / 57 起 |
| 5 | `{'hidden_units': 256, 'learning_rate': 0.001, 'dropout_rate': 0.0}` | 0.42455 | 18 / 83 起 |
| 6 | `{'hidden_units': 256, 'learning_rate': 0.001, 'dropout_rate': 0.3}` | 0.3407 | 18 / 109 起 |
| 7 | `{'hidden_units': 256, 'learning_rate': 0.0003, 'dropout_rate': 0.0}` | 0.40337 | 18 / 125 起 |
| 8 | `{'hidden_units': 256, 'learning_rate': 0.0003, 'dropout_rate': 0.3}` | D | 18 / 151 起 |

### 保存输出原文摘录

Cell 4, output 0 (stream；A：保存输出):

```text
{
  "python": "3.11.15",
  "numpy": "1.26.4",
  "pandas": "2.2.3",
  "scikit_learn": "1.5.2",
  "tensorflow": "2.17.1",
  "keras": "3.6.0",
  "platform": "Windows-10-10.0.26200-SP0",
  "processor": "Intel64 Family 6 Model 189 Stepping 1, GenuineIntel",
  "logical_cpu_count": 8,
  "seed": 5318,
  "devices": [
    "/physical_device:CPU:0"
  ],
  "intra_op_threads": 4,
  "inter_op_threads": 2,
  "deterministic_ops": true
}
```

Cell 6, output 0 (stream；A：保存输出):

```text
{
  "fit_indices_sha256": "191d1629061294ebe7e01fe7a79ac57739fced43795161a0c6b821241311c571",
  "validation_indices_sha256": "c07d9573b52ee95cb6bd73390fde64f9c2dccd1c2ab14c244a479b1aa0dd3718"
}
Train (25600, 28, 28, 3) Val (6400, 28, 28, 3) Test (8000, 28, 28, 3) Labels [0, 1, 2, 3, 4, 5, 6, 7, 8]
Training dtype: uint8 | pixel divisor: 255.0
Flattened fit/validation shapes: (25600, 2352) (6400, 2352)
```

Cell 6, output 1 (display_data；A：保存输出):

```text
   class_id                            class_name  original_train   fit  \
0         0                               Adipose            3490  2792
1         1                            Background            3431  2745
2         2                                Debris            3505  2804
3         3                           Lymphocytes            3656  2925
4         4                                 Mucus            2950  2360
5         5                         Smooth muscle            4290  3432
6         6                   Normal colon mucosa            2728  2182
7         7              Cancer-associated stroma            3253  2602
8         8  Colorectal adenocarcinoma epithelium            4697  3758

   validation
0         698
1         686
2         701
3         731
4         590
5         858
6         546
7         651
8         939
```

Cell 25, output 0 (stream；A：保存输出):

```text
Frozen MLP parameters: {'hidden_units': 256, 'learning_rate': 0.001, 'dropout_rate': 0.0}
Fixed full-data epochs: 10
Recorded validation selection: {'trial_id': 5, 'macro_f1': 0.4245453119342078, 'accuracy': 0.46828125, 'balanced_accuracy': 0.4624929838057703}
```

Cell 27, output 0 (display_data；A：保存输出):

```text
                                                                    value
model                                                                 MLP
best_hyperparameters    {"dropout_rate": 0.0, "hidden_units": 256, "le...
validation_macro_f1                                              0.424545
test_accuracy                                                    0.496375
test_macro_f1                                                    0.449128
test_balanced_accuracy                                           0.477117
fit_seconds                                                      10.76656
prediction_seconds                                               0.205754
parameters                                                         604681
epochs                                                                 10
search_fit_samples                                                  25600
validation_samples                                                   6400
train_samples                                                       32000
test_samples                                                         8000
seed                                                                 5318
```

Cell 27, output 1 (display_data；A：保存输出):

```text
                                      precision  recall  f1-score    support
Adipose                                  0.7221  0.9645    0.8259   873.0000
Background                               0.7500  0.6399    0.6906   858.0000
Debris                                   0.5602  0.1380    0.2214   877.0000
Lymphocytes                              0.4686  0.6685    0.5509   914.0000
Mucus                                    0.5085  0.5292    0.5186   737.0000
Smooth muscle                            0.4206  0.4422    0.4311  1072.0000
Normal colon mucosa                      0.3394  0.0821    0.1322   682.0000
Cancer-associated stroma                 0.3114  0.1279    0.1813   813.0000
Colorectal adenocarcinoma epithelium     0.3764  0.7019    0.4900  1174.0000
accuracy                                 0.4964  0.4964    0.4964     0.4964
macro avg                                0.4952  0.4771    0.4491  8000.0000
weighted avg                             0.4932  0.4964    0.4586  8000.0000
```

### D：缺失或无法核实

- 历史最终测试预测标签文件不在 Git 仓库，无法独立重算 V1 指标
- 保存输出中的某些表格显示位数低于内部精度

### mlp 逐类指标（A：保存的分类报告）

| 类别 | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| Adipose | 0.7221 | 0.9645 | 0.8259 | 873 |
| Background | 0.75 | 0.6399 | 0.6906 | 858 |
| Debris | 0.5602 | 0.138 | 0.2214 | 877 |
| Lymphocytes | 0.4686 | 0.6685 | 0.5509 | 914 |
| Mucus | 0.5085 | 0.5292 | 0.5186 | 737 |
| Smooth muscle | 0.4206 | 0.4422 | 0.4311 | 1072 |
| Normal colon mucosa | 0.3394 | 0.0821 | 0.1322 | 682 |
| Cancer-associated stroma | 0.3114 | 0.1279 | 0.1813 | 813 |
| Colorectal adenocarcinoma epithelium | 0.3764 | 0.7019 | 0.49 | 1174 |

## CNN.ipynb

SHA-256: `e5ec3f85fd46c691cdd148a41eb17528faa3096e72378fab0f3a253bb7f6f605`；代码 Cell 14 个，已执行 14 个，错误输出 0 个。

环境 Cell 3 (A)；数据与索引指纹 Cell 5 (A)；8 次实际搜索日志 Cell 19 (A)；硬编码的历史绘图数据 Cell 20 (C)；冻结参数/epoch Cell 27 (C 常量，A 打印)；最终模型/逐类结果 Cell 29 (A)。

搜索输出识别到 8 组 trial；逐组至少保存参数与恢复后的验证 Macro-F1。

V1 验证 Accuracy / Macro-F1 / Balanced：0.75125 / 0.738608 / 0.743244847776286；V1 测试：0.720375 / 0.69786 / 0.705091。参数 106089.0，最终 11 epochs。

| Trial | 参数 | 验证 Macro-F1（历史运行输出，显示精度） | Cell / Output |
|---:|---|---:|---|
| 1 | `{'base_filters': 8, 'learning_rate': 0.001, 'dropout_rate': 0.0}` | 0.70712 | 19 / 0 起 |
| 2 | `{'base_filters': 8, 'learning_rate': 0.001, 'dropout_rate': 0.3}` | 0.7071 | 19 / 26 起 |
| 3 | `{'base_filters': 8, 'learning_rate': 0.0003, 'dropout_rate': 0.0}` | 0.67006 | 19 / 52 起 |
| 4 | `{'base_filters': 8, 'learning_rate': 0.0003, 'dropout_rate': 0.3}` | D | 19 / 78 起 |
| 5 | `{'base_filters': 16, 'learning_rate': 0.001, 'dropout_rate': 0.0}` | 0.65915 | 19 / 103 起 |
| 6 | `{'base_filters': 16, 'learning_rate': 0.001, 'dropout_rate': 0.3}` | 0.71896 | 19 / 124 起 |
| 7 | `{'base_filters': 16, 'learning_rate': 0.0003, 'dropout_rate': 0.0}` | 0.73861 | 19 / 149 起 |
| 8 | `{'base_filters': 16, 'learning_rate': 0.0003, 'dropout_rate': 0.3}` | 0.69302 | 19 / 174 起 |

### 保存输出原文摘录

Cell 3, output 0 (stream；A：保存输出):

```text
Matplotlib is building the font cache; this may take a moment.
```

Cell 3, output 1 (stream；A：保存输出):

```text
{
  "seed": 5318,
  "python": "3.12.14",
  "numpy": "1.26.4",
  "pandas": "2.2.3",
  "scikit_learn": "1.5.2",
  "tensorflow": "2.17.1",
  "keras": "3.5.0",
  "platform": "macOS-26.3-arm64-arm-64bit",
  "machine": "arm64",
  "logical_cpu_count": 10,
  "tensorflow_devices": [
    "/physical_device:CPU:0"
  ],
  "intra_op_threads": 4,
  "inter_op_threads": 2,
  "deterministic_ops": true
}
```

Cell 5, output 0 (stream；A：保存输出):

```text
Canvas training: (32000, 28, 28, 3) uint8
Development fit: (25600, 28, 28, 3) | validation: (6400, 28, 28, 3)
Original held-out test: (8000, 28, 28, 3) (not used for model selection)
Training pixel range: (0.0, 255.0) | divisor: 255.0
Labels: [0, 1, 2, 3, 4, 5, 6, 7, 8] | seed: 5318
{
  "fit_indices_sha256": "191d1629061294ebe7e01fe7a79ac57739fced43795161a0c6b821241311c571",
  "validation_indices_sha256": "c07d9573b52ee95cb6bd73390fde64f9c2dccd1c2ab14c244a479b1aa0dd3718"
}
```

Cell 5, output 1 (execute_result；A：保存输出):

```text
193
```

Cell 20, output 0 (display_data；A/C：该输出由硬编码历史记录生成):

```text
   base_filters  learning_rate  dropout_rate  validation_accuracy  \
0            16         0.0010           0.3              0.75125
1            16         0.0010           0.0              0.72359
2            16         0.0003           0.0              0.72422
3             8         0.0010           0.0              0.72391
4             8         0.0010           0.3              0.71969
5            16         0.0003           0.3              0.70672
6             8         0.0003           0.0              0.68469
7             8         0.0003           0.3              0.67844

   validation_macro_f1  validation_balanced_accuracy  fit_seconds  \
0              0.73861                       0.74324     34.87628
1              0.71896                       0.71757     31.41409
2              0.70713                       0.71039     36.11053
3              0.70712                       0.71123     23.08751
4              0.70710                       0.70918     20.07215
5              0.69302                       0.69693     28.85534
6              0.67006                       0.67441     21.34698
7              0.65915                       0.66638     20.29596

   training_epoch_seconds  in_fit_validation_seconds  validation_seconds  \
0                32.26599                    2.56279             0.24762
1                29.06962                    2.29953             0.24415
2                33.23610                    2.74609             0.21723
3                21.24770                    1.79329             0.19046
4                18.31457                    1.71631             0.18548
5                26.55802                    2.25545             0.20472
6                19.52069                    1.77598             0.15463
7                18.43119                    1.81848             0.36184

   epochs_run  best_epoch  parameters  trial_id
0          12          11      106089         6
1          10           7      106089         5
2          12          12      106089         7
3          12          11       52217         1
4          12          12       52217         2
5          12          12      106089         8
6          12          12       52217         3
7          12          12       52217         4
```

Cell 27, output 0 (stream；A：保存输出):

```text
Frozen CNN configuration: {'base_filters': 16, 'learning_rate': 0.001, 'dropout_rate': 0.3}
Fixed full-data training epochs: 11
Recorded selection result: {'trial_id': 6, 'macro_f1': 0.7386080336263325, 'accuracy': 0.75125, 'balanced_accuracy': 0.743244847776286}
```

Cell 29, output 0 (display_data；A：保存输出):

```text
                                                                    value
model                                                                 CNN
best_hyperparameters    {"base_filters": 16, "dropout_rate": 0.3, "lea...
validation_macro_f1                                              0.738608
validation_accuracy                                               0.75125
test_accuracy                                                    0.720375
test_macro_f1                                                     0.69786
test_balanced_accuracy                                           0.705091
fit_seconds                                                     30.181307
prediction_seconds                                               0.248718
parameters                                                         106089
epochs                                                                 11
search_fit_samples                                                  25600
validation_samples                                                   6400
train_samples                                                       32000
test_samples                                                         8000
seed                                                                 5318
```

Cell 29, output 1 (stream；A：保存输出):

```text
                                      precision    recall  f1-score   support

                             Adipose     0.8452    0.9759    0.9059       873
                          Background     0.9718    0.9231    0.9468       858
                              Debris     0.8406    0.2645    0.4024       877
                         Lymphocytes     0.8924    0.9530    0.9217       914
                               Mucus     0.6932    0.6866    0.6898       737
                       Smooth muscle     0.6459    0.7640    0.7000      1072
                 Normal colon mucosa     0.6326    0.4897    0.5521       682
            Cancer-associated stroma     0.4613    0.4330    0.4467       813
Colorectal adenocarcinoma epithelium     0.6143    0.8560    0.7153      1174

                            accuracy                         0.7204      8000
                           macro avg     0.7330    0.7051    0.6979      8000
                        weighted avg     0.7319    0.7204    0.7046      8000
```

Cell 30, output 1 (display_data；A：保存输出):

```text
   class_id                            class_name  precision  recall  \
0         0                               Adipose     0.8452  0.9759
1         1                            Background     0.9718  0.9231
2         2                                Debris     0.8406  0.2645
3         3                           Lymphocytes     0.8924  0.9530
4         4                                 Mucus     0.6932  0.6866
5         5                         Smooth muscle     0.6459  0.7640
6         6                   Normal colon mucosa     0.6326  0.4897
7         7              Cancer-associated stroma     0.4613  0.4330
8         8  Colorectal adenocarcinoma epithelium     0.6143  0.8560

   f1_score  support
0    0.9059      873
1    0.9468      858
2    0.4024      877
3    0.9217      914
4    0.6898      737
5    0.7000     1072
6    0.5521      682
7    0.4467      813
8    0.7153     1174
```

Cell 30, output 3 (stream；A：保存输出):

```text
Largest directed test confusions (count, true ID, predicted ID): [(240, 2, 8), (218, 7, 5), (181, 2, 5), (171, 6, 8), (157, 2, 7)]
```

### D：缺失或无法核实

- 历史最终测试预测标签文件不在 Git 仓库，无法独立重算 V1 指标
- 保存输出中的某些表格显示位数低于内部精度

### cnn 逐类指标（A：保存的分类报告）

| 类别 | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| Adipose | 0.8452 | 0.9759 | 0.9059 | 873 |
| Background | 0.9718 | 0.9231 | 0.9468 | 858 |
| Debris | 0.8406 | 0.2645 | 0.4024 | 877 |
| Lymphocytes | 0.8924 | 0.953 | 0.9217 | 914 |
| Mucus | 0.6932 | 0.6866 | 0.6898 | 737 |
| Smooth muscle | 0.6459 | 0.764 | 0.7 | 1072 |
| Normal colon mucosa | 0.6326 | 0.4897 | 0.5521 | 682 |
| Cancer-associated stroma | 0.4613 | 0.433 | 0.4467 | 813 |
| Colorectal adenocarcinoma epithelium | 0.6143 | 0.856 | 0.7153 | 1174 |

## 缺失与使用边界

- 原始 Notebook 保存的图像输出可能显示混淆矩阵，但像素图不能可靠还原全部整数；V2 会保存数值 CSV。
- 所有 V1 用时来自不同硬件/系统，不能当作控制变量后的算法速度比较。
- 此文件仅为训练前快照。V2 成功与否必须由新运行日志和预测标签确认。
