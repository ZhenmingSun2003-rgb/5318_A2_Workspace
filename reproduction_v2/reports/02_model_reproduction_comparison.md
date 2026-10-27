# 02 模型复现对比

主实验始终使用原 Notebook 冻结的 V1 最终参数；V2 搜索最佳项单独列出。差值阈值仅为工程调查触发条件，不代表统计显著性。

| 模型 | 指标 | V1 | V2 | 绝对差 | 相对差 | 状态 | 证据 | 注释 |
|---|---|---:|---:|---:|---:|---|---|---|
| dummy | validation_accuracy | 0.1467 | 0.146719 | 1.875e-05 | 0.000127812 | MATCHES PRINTED PRECISION | `V1 A: baseline.ipynb Cell 22 保存输出; V2 runs/20261027T083549Z_baseline_5893c130/validation_results.csv` | V1 rounded display precision |
| dummy | validation_macro_f1 | 0.0284 | 0.0284326 | 3.25748e-05 | 0.001147 | MATCHES PRINTED PRECISION | `V1 A: baseline.ipynb Cell 22 保存输出; V2 runs/20261027T083549Z_baseline_5893c130/validation_results.csv` | V1 rounded display precision |
| dummy | validation_balanced_accuracy | 0.1111 | 0.111111 | 1.11111e-05 | 0.00010001 | MATCHES PRINTED PRECISION | `V1 A: baseline.ipynb Cell 22 保存输出; V2 runs/20261027T083549Z_baseline_5893c130/validation_results.csv` | V1 rounded display precision |
| dummy | test_accuracy | 0.1468 | 0.14675 | 5e-05 | 0.000340599 | MATCHES PRINTED PRECISION | `V1 A: baseline.ipynb Cell 29 保存输出; V2 runs/20261027T083549Z_baseline_5893c130/verified_metrics.json` | V1 rounded display precision |
| dummy | test_macro_f1 | 0.0284 | 0.0284379 | 3.78558e-05 | 0.00133295 | MATCHES PRINTED PRECISION | `V1 A: baseline.ipynb Cell 29 保存输出; V2 runs/20261027T083549Z_baseline_5893c130/verified_metrics.json` | V1 rounded display precision |
| dummy | test_balanced_accuracy | 0.1111 | 0.111111 | 1.11111e-05 | 0.00010001 | MATCHES PRINTED PRECISION | `V1 A: baseline.ipynb Cell 29 保存输出; V2 runs/20261027T083549Z_baseline_5893c130/verified_metrics.json` | V1 rounded display precision |
| dummy | fit_seconds | 0.0009 | 0.00116555 | 0.000265554 | D | HARDWARE NOT CONTROLLED | `V1 A: baseline.ipynb Cell 29 保存输出; V2 runs/20261027T083549Z_baseline_5893c130/notebook_final_results.csv` | V1 rounded display precision |
| dummy | prediction_seconds | 0.0001 | 4.7802e-05 | 5.2198e-05 | D | HARDWARE NOT CONTROLLED | `V1 A: baseline.ipynb Cell 29 保存输出; V2 runs/20261027T083549Z_baseline_5893c130/notebook_final_results.csv` | V1 rounded display precision |
| dummy | parameters | D | D | D | D | NOT AVAILABLE | `V1 A: baseline.ipynb Cell 29 保存输出; V2 runs/20261027T083549Z_baseline_5893c130/notebook_final_results.csv` | V1 rounded display precision |
| dummy | selected_epochs | D | D | D | D | NOT AVAILABLE | `V1 A: baseline.ipynb Cell 29 保存输出; V2 runs/20261027T083549Z_baseline_5893c130/notebook_final_results.csv` | V1 rounded display precision |
| nearest_centroid | validation_accuracy | 0.4222 | 0.422187 | 1.25e-05 | 2.96068e-05 | MATCHES PRINTED PRECISION | `V1 A: baseline.ipynb Cell 22 保存输出; V2 runs/20261027T083549Z_baseline_5893c130/validation_results.csv` | V1 rounded display precision |
| nearest_centroid | validation_macro_f1 | 0.4051 | 0.405128 | 2.7913e-05 | 6.89041e-05 | MATCHES PRINTED PRECISION | `V1 A: baseline.ipynb Cell 22 保存输出; V2 runs/20261027T083549Z_baseline_5893c130/validation_results.csv` | V1 rounded display precision |
| nearest_centroid | validation_balanced_accuracy | 0.4237 | 0.423687 | 1.29284e-05 | 3.0513e-05 | MATCHES PRINTED PRECISION | `V1 A: baseline.ipynb Cell 22 保存输出; V2 runs/20261027T083549Z_baseline_5893c130/validation_results.csv` | V1 rounded display precision |
| nearest_centroid | test_accuracy | 0.4302 | 0.43025 | 5e-05 | 0.000116225 | MATCHES PRINTED PRECISION | `V1 A: baseline.ipynb Cell 29 保存输出; V2 runs/20261027T083549Z_baseline_5893c130/verified_metrics.json` | V1 rounded display precision |
| nearest_centroid | test_macro_f1 | 0.4105 | 0.410469 | 3.05646e-05 | 7.4457e-05 | MATCHES PRINTED PRECISION | `V1 A: baseline.ipynb Cell 29 保存输出; V2 runs/20261027T083549Z_baseline_5893c130/verified_metrics.json` | V1 rounded display precision |
| nearest_centroid | test_balanced_accuracy | 0.4325 | 0.432515 | 1.48344e-05 | 3.42992e-05 | MATCHES PRINTED PRECISION | `V1 A: baseline.ipynb Cell 29 保存输出; V2 runs/20261027T083549Z_baseline_5893c130/verified_metrics.json` | V1 rounded display precision |
| nearest_centroid | fit_seconds | 0.106 | 0.0951006 | 0.0108994 | D | HARDWARE NOT CONTROLLED | `V1 A: baseline.ipynb Cell 29 保存输出; V2 runs/20261027T083549Z_baseline_5893c130/notebook_final_results.csv` | V1 rounded display precision |
| nearest_centroid | prediction_seconds | 0.0648 | 0.0465848 | 0.0182152 | D | HARDWARE NOT CONTROLLED | `V1 A: baseline.ipynb Cell 29 保存输出; V2 runs/20261027T083549Z_baseline_5893c130/notebook_final_results.csv` | V1 rounded display precision |
| nearest_centroid | parameters | D | D | D | D | NOT AVAILABLE | `V1 A: baseline.ipynb Cell 29 保存输出; V2 runs/20261027T083549Z_baseline_5893c130/notebook_final_results.csv` | V1 rounded display precision |
| nearest_centroid | selected_epochs | D | D | D | D | NOT AVAILABLE | `V1 A: baseline.ipynb Cell 29 保存输出; V2 runs/20261027T083549Z_baseline_5893c130/notebook_final_results.csv` | V1 rounded display precision |
| gaussian_nb | validation_accuracy | 0.4041 | 0.404062 | 3.75e-05 | 9.27988e-05 | MATCHES PRINTED PRECISION | `V1 A: Naive_Bayes.ipynb Cell 15 保存输出; V2 runs/20261027T084817Z_naive_bayes_c0d7f694/search_results.csv` | V1 rounded display precision |
| gaussian_nb | validation_macro_f1 | 0.3749 | 0.37492 | 1.96062e-05 | 5.22973e-05 | MATCHES PRINTED PRECISION | `V1 A: Naive_Bayes.ipynb Cell 15 保存输出; V2 runs/20261027T084817Z_naive_bayes_c0d7f694/search_results.csv` | V1 rounded display precision |
| gaussian_nb | validation_balanced_accuracy | 0.4188 | 0.418822 | 2.15003e-05 | 5.13379e-05 | MATCHES PRINTED PRECISION | `V1 A: Naive_Bayes.ipynb Cell 15 保存输出; V2 runs/20261027T084817Z_naive_bayes_c0d7f694/search_results.csv` | V1 rounded display precision |
| gaussian_nb | test_accuracy | 0.4155 | 0.4155 | 0 | 0 | EXACT | `V1 A: Naive_Bayes.ipynb Cell 22 保存输出; V2 runs/20261027T084817Z_naive_bayes_c0d7f694/verified_metrics.json` | V1 rounded display precision |
| gaussian_nb | test_macro_f1 | 0.3857 | 0.385748 | 4.79115e-05 | 0.00012422 | MATCHES PRINTED PRECISION | `V1 A: Naive_Bayes.ipynb Cell 22 保存输出; V2 runs/20261027T084817Z_naive_bayes_c0d7f694/verified_metrics.json` | V1 rounded display precision |
| gaussian_nb | test_balanced_accuracy | 0.4307 | 0.430696 | 3.8982e-06 | 9.05084e-06 | MATCHES PRINTED PRECISION | `V1 A: Naive_Bayes.ipynb Cell 22 保存输出; V2 runs/20261027T084817Z_naive_bayes_c0d7f694/verified_metrics.json` | V1 rounded display precision |
| gaussian_nb | fit_seconds | 0.3792 | 0.3691 | 0.0101 | D | HARDWARE NOT CONTROLLED | `V1 A: Naive_Bayes.ipynb Cell 22 保存输出; V2 runs/20261027T084817Z_naive_bayes_c0d7f694/execution.log` | V1 rounded display precision |
| gaussian_nb | prediction_seconds | 0.9081 | 0.7947 | 0.1134 | D | HARDWARE NOT CONTROLLED | `V1 A: Naive_Bayes.ipynb Cell 22 保存输出; V2 runs/20261027T084817Z_naive_bayes_c0d7f694/execution.log` | V1 rounded display precision |
| gaussian_nb | parameters | D | 42345 | D | D | NOT AVAILABLE | `V1 A: Naive_Bayes.ipynb Cell 22 保存输出; V2 runs/20261027T084817Z_naive_bayes_c0d7f694/parameter_inventory.json` | V1 rounded display precision |
| gaussian_nb | selected_epochs | D | D | D | D | NOT AVAILABLE | `V1 A: Naive_Bayes.ipynb Cell 22 保存输出; V2 runs/20261027T084817Z_naive_bayes_c0d7f694/execution.log` | V1 rounded display precision |
| gaussian_nb | selected_hyperparameters | {"var_smoothing": 1e-06} | {"var_smoothing": 1e-06} | D | D | EXACT | `V1 C: Cell 22 BEST_VAR_SMOOTHING；B: Cell 18 tie-break 描述; V2 runs/20261027T084817Z_naive_bayes_c0d7f694/execution.log` | Final model uses V1 frozen choice, independent of V2 search winner |
| mlp | validation_accuracy | 0.468281 | 0.445469 | 0.0228125 | 0.0487154 | INVESTIGATE (>0.02) | `V1 A: MLP.ipynb Cell 18 保存输出; V2 runs/20261027T083829Z_mlp_13872e7e/search_results.csv` |  |
| mlp | validation_macro_f1 | 0.424545 | 0.42886 | 0.00431463 | 0.0101629 | SMALL DIFFERENCE | `V1 A: MLP.ipynb Cell 18 保存输出; V2 runs/20261027T083829Z_mlp_13872e7e/search_results.csv` |  |
| mlp | validation_balanced_accuracy | 0.462493 | 0.443837 | 0.0186557 | 0.0403373 | NOTICE (>0.01) | `V1 A: MLP.ipynb Cell 18 保存输出; V2 runs/20261027T083829Z_mlp_13872e7e/search_results.csv` |  |
| mlp | test_accuracy | 0.496375 | 0.48925 | 0.007125 | 0.0143541 | SMALL DIFFERENCE | `V1 A: MLP.ipynb Cell 27 保存输出; V2 runs/20261027T083829Z_mlp_13872e7e/verified_metrics.json` |  |
| mlp | test_macro_f1 | 0.449128 | 0.438672 | 0.0104556 | 0.0232797 | NOTICE (>0.01) | `V1 A: MLP.ipynb Cell 27 保存输出; V2 runs/20261027T083829Z_mlp_13872e7e/verified_metrics.json` |  |
| mlp | test_balanced_accuracy | 0.477117 | 0.469945 | 0.00717223 | 0.0150324 | SMALL DIFFERENCE | `V1 A: MLP.ipynb Cell 27 保存输出; V2 runs/20261027T083829Z_mlp_13872e7e/verified_metrics.json` |  |
| mlp | fit_seconds | 10.7666 | 13.1891 | 2.42255 | D | HARDWARE NOT CONTROLLED | `V1 A: MLP.ipynb Cell 27 保存输出; V2 runs/20261027T083829Z_mlp_13872e7e/mlp_final_results.csv` |  |
| mlp | prediction_seconds | 0.205754 | 0.180592 | 0.025162 | D | HARDWARE NOT CONTROLLED | `V1 A: MLP.ipynb Cell 27 保存输出; V2 runs/20261027T083829Z_mlp_13872e7e/mlp_final_results.csv` |  |
| mlp | parameters | 604681 | 604681 | 0 | 0 | EXACT | `V1 A: MLP.ipynb Cell 27 保存输出; V2 runs/20261027T083829Z_mlp_13872e7e/mlp_final_results.csv` |  |
| mlp | selected_epochs | 10 | 10 | 0 | 0 | EXACT | `V1 A: MLP.ipynb Cell 27 保存输出; V2 runs/20261027T083829Z_mlp_13872e7e/mlp_final_results.csv` |  |
| mlp | selected_hyperparameters | {"dropout_rate": 0.0, "hidden_units": 256, "learning_rate": 0.001} | {"dropout_rate": 0.0, "hidden_units": 256, "learning_rate": 0.001} | D | D | EXACT | `V1 frozen source cell; V2 runs/20261027T083829Z_mlp_13872e7e/mlp_final_results.csv` | Final model uses V1 frozen choice, independent of V2 search winner |
| cnn | validation_accuracy | 0.75125 | 0.748125 | 0.003125 | 0.00415973 | SMALL DIFFERENCE | `V1 A: CNN.ipynb Cell 19 保存输出; V2 runs/20261027T084038Z_cnn_85313f9d/search_results.csv` |  |
| cnn | validation_macro_f1 | 0.738608 | 0.736969 | 0.00163864 | 0.00221855 | SMALL DIFFERENCE | `V1 A: CNN.ipynb Cell 19 保存输出; V2 runs/20261027T084038Z_cnn_85313f9d/search_results.csv` |  |
| cnn | validation_balanced_accuracy | 0.743245 | 0.736217 | 0.00702813 | 0.009456 | SMALL DIFFERENCE | `V1 A: CNN.ipynb Cell 19 保存输出; V2 runs/20261027T084038Z_cnn_85313f9d/search_results.csv` |  |
| cnn | test_accuracy | 0.720375 | 0.73925 | 0.018875 | 0.0262016 | NOTICE (>0.01) | `V1 A: CNN.ipynb Cell 29 保存输出; V2 runs/20261027T084038Z_cnn_85313f9d/verified_metrics.json` |  |
| cnn | test_macro_f1 | 0.69786 | 0.723255 | 0.0253952 | 0.0363901 | INVESTIGATE (>0.02) | `V1 A: CNN.ipynb Cell 29 保存输出; V2 runs/20261027T084038Z_cnn_85313f9d/verified_metrics.json` |  |
| cnn | test_balanced_accuracy | 0.705091 | 0.726501 | 0.0214102 | 0.0303651 | INVESTIGATE (>0.02) | `V1 A: CNN.ipynb Cell 29 保存输出; V2 runs/20261027T084038Z_cnn_85313f9d/verified_metrics.json` |  |
| cnn | fit_seconds | 30.1813 | 57.7016 | 27.5203 | D | HARDWARE NOT CONTROLLED | `V1 A: CNN.ipynb Cell 29 保存输出; V2 runs/20261027T084038Z_cnn_85313f9d/cnn_final_results.csv` |  |
| cnn | prediction_seconds | 0.248718 | 0.506011 | 0.257293 | D | HARDWARE NOT CONTROLLED | `V1 A: CNN.ipynb Cell 29 保存输出; V2 runs/20261027T084038Z_cnn_85313f9d/cnn_final_results.csv` |  |
| cnn | parameters | 106089 | 106089 | 0 | 0 | EXACT | `V1 A: CNN.ipynb Cell 29 保存输出; V2 runs/20261027T084038Z_cnn_85313f9d/cnn_final_results.csv` |  |
| cnn | selected_epochs | 11 | 11 | 0 | 0 | EXACT | `V1 A: CNN.ipynb Cell 29 保存输出; V2 runs/20261027T084038Z_cnn_85313f9d/cnn_final_results.csv` |  |
| cnn | selected_hyperparameters | {"base_filters": 16, "dropout_rate": 0.3, "learning_rate": 0.001} | {"base_filters": 16, "dropout_rate": 0.3, "learning_rate": 0.001} | D | D | EXACT | `V1 frozen source cell; V2 runs/20261027T084038Z_cnn_85313f9d/cnn_final_results.csv` | Final model uses V1 frozen choice, independent of V2 search winner |

## 搜索和最终模型隔离

- dummy: PASS（源 Cell 执行 PASS）；实际搜索 0 组；V1 冻结参数 `{}`，冻结 epoch `None`；V2 搜索最佳 D；最终测试仍使用 V1 冻结配置。运行 `C:\Users\Saberken\Downloads\5318_A2_Workspace\reproduction_v2\runs\20261027T083549Z_baseline_5893c130`。
- nearest_centroid: PASS（源 Cell 执行 PASS）；实际搜索 0 组；V1 冻结参数 `{}`，冻结 epoch `None`；V2 搜索最佳 D；最终测试仍使用 V1 冻结配置。运行 `C:\Users\Saberken\Downloads\5318_A2_Workspace\reproduction_v2\runs\20261027T083549Z_baseline_5893c130`。
- gaussian_nb: PASS（源 Cell 执行 PASS）；实际搜索 8 组；V1 冻结参数 `{'var_smoothing': 1e-06}`，冻结 epoch `None`；V2 搜索最佳 trial D，参数 `{'var_smoothing': '1e-12'}`，Macro-F1 0.3749196062459024，best epoch D；最终测试仍使用 V1 冻结配置。运行 `C:\Users\Saberken\Downloads\5318_A2_Workspace\reproduction_v2\runs\20261027T084817Z_naive_bayes_c0d7f694`。
- mlp: WARNING（源 Cell 执行 PASS）；实际搜索 8 组；V1 冻结参数 `{'hidden_units': 256, 'learning_rate': 0.001, 'dropout_rate': 0.0}`，冻结 epoch `10`；V2 搜索最佳 trial 5，参数 `{'hidden_units': '256', 'learning_rate': '0.001', 'dropout_rate': '0.0'}`，Macro-F1 0.4288596287516593，best epoch 9；最终测试仍使用 V1 冻结配置。运行 `C:\Users\Saberken\Downloads\5318_A2_Workspace\reproduction_v2\runs\20261027T083829Z_mlp_13872e7e`。
- cnn: WARNING（源 Cell 执行 PASS）；实际搜索 8 组；V1 冻结参数 `{'base_filters': 16, 'learning_rate': 0.001, 'dropout_rate': 0.3}`，冻结 epoch `11`；V2 搜索最佳 trial 6，参数 `{'base_filters': '16', 'learning_rate': '0.001', 'dropout_rate': '0.3'}`，Macro-F1 0.7369693606145916，best epoch 12；最终测试仍使用 V1 冻结配置。运行 `C:\Users\Saberken\Downloads\5318_A2_Workspace\reproduction_v2\runs\20261027T084038Z_cnn_85313f9d`。

## 逐类 Recall 与 F1

V1 为 Notebook 保存的分类报告显示精度；V2 从保存的预测标签独立计算。

| 模型 | 类别 | 指标 | V1 | V2 | 绝对差 | 状态 |
|---|---|---|---:|---:|---:|---|
| nearest_centroid | 0 Adipose | recall | 0.960000 | 0.959908 | 0.000092 | SMALL DIFFERENCE |
| nearest_centroid | 0 Adipose | f1 | 0.788000 | 0.787964 | 0.000036 | MATCHES PRINTED PRECISION |
| nearest_centroid | 1 Background | recall | 0.670000 | 0.670163 | 0.000163 | SMALL DIFFERENCE |
| nearest_centroid | 1 Background | f1 | 0.543000 | 0.542709 | 0.000291 | SMALL DIFFERENCE |
| nearest_centroid | 2 Debris | recall | 0.268000 | 0.267959 | 0.000041 | MATCHES PRINTED PRECISION |
| nearest_centroid | 2 Debris | f1 | 0.290000 | 0.290482 | 0.000482 | SMALL DIFFERENCE |
| nearest_centroid | 3 Lymphocytes | recall | 0.435000 | 0.435449 | 0.000449 | SMALL DIFFERENCE |
| nearest_centroid | 3 Lymphocytes | f1 | 0.556000 | 0.556254 | 0.000254 | SMALL DIFFERENCE |
| nearest_centroid | 4 Mucus | recall | 0.577000 | 0.576662 | 0.000338 | SMALL DIFFERENCE |
| nearest_centroid | 4 Mucus | f1 | 0.394000 | 0.394249 | 0.000249 | SMALL DIFFERENCE |
| nearest_centroid | 5 Smooth muscle | recall | 0.283000 | 0.282649 | 0.000351 | SMALL DIFFERENCE |
| nearest_centroid | 5 Smooth muscle | f1 | 0.363000 | 0.363309 | 0.000309 | SMALL DIFFERENCE |
| nearest_centroid | 6 Normal colon mucosa | recall | 0.199000 | 0.199413 | 0.000413 | SMALL DIFFERENCE |
| nearest_centroid | 6 Normal colon mucosa | f1 | 0.199000 | 0.198830 | 0.000170 | SMALL DIFFERENCE |
| nearest_centroid | 7 Cancer-associated stroma | recall | 0.154000 | 0.153752 | 0.000248 | SMALL DIFFERENCE |
| nearest_centroid | 7 Cancer-associated stroma | f1 | 0.190000 | 0.190259 | 0.000259 | SMALL DIFFERENCE |
| nearest_centroid | 8 Colorectal adenocarcinoma epithelium | recall | 0.347000 | 0.346678 | 0.000322 | SMALL DIFFERENCE |
| nearest_centroid | 8 Colorectal adenocarcinoma epithelium | f1 | 0.370000 | 0.370168 | 0.000168 | SMALL DIFFERENCE |
| gaussian_nb | 0 0 | recall | 0.938100 | 0.938144 | 0.000044 | MATCHES PRINTED PRECISION |
| gaussian_nb | 0 0 | f1 | 0.782200 | 0.782235 | 0.000035 | MATCHES PRINTED PRECISION |
| gaussian_nb | 1 1 | recall | 0.644500 | 0.644522 | 0.000022 | MATCHES PRINTED PRECISION |
| gaussian_nb | 1 1 | f1 | 0.666300 | 0.666265 | 0.000035 | MATCHES PRINTED PRECISION |
| gaussian_nb | 2 2 | recall | 0.102600 | 0.102623 | 0.000023 | MATCHES PRINTED PRECISION |
| gaussian_nb | 2 2 | f1 | 0.132000 | 0.131965 | 0.000035 | MATCHES PRINTED PRECISION |
| gaussian_nb | 3 3 | recall | 0.621400 | 0.621444 | 0.000044 | MATCHES PRINTED PRECISION |
| gaussian_nb | 3 3 | f1 | 0.499300 | 0.499341 | 0.000041 | MATCHES PRINTED PRECISION |
| gaussian_nb | 4 4 | recall | 0.474900 | 0.474898 | 0.000002 | MATCHES PRINTED PRECISION |
| gaussian_nb | 4 4 | f1 | 0.401600 | 0.401606 | 0.000006 | MATCHES PRINTED PRECISION |
| gaussian_nb | 5 5 | recall | 0.075600 | 0.075560 | 0.000040 | MATCHES PRINTED PRECISION |
| gaussian_nb | 5 5 | f1 | 0.129700 | 0.129704 | 0.000004 | MATCHES PRINTED PRECISION |
| gaussian_nb | 6 6 | recall | 0.215500 | 0.215543 | 0.000043 | MATCHES PRINTED PRECISION |
| gaussian_nb | 6 6 | f1 | 0.239800 | 0.239804 | 0.000004 | MATCHES PRINTED PRECISION |
| gaussian_nb | 7 7 | recall | 0.629800 | 0.629766 | 0.000034 | MATCHES PRINTED PRECISION |
| gaussian_nb | 7 7 | f1 | 0.381000 | 0.380952 | 0.000048 | MATCHES PRINTED PRECISION |
| gaussian_nb | 8 8 | recall | 0.173800 | 0.173765 | 0.000035 | MATCHES PRINTED PRECISION |
| gaussian_nb | 8 8 | f1 | 0.239900 | 0.239859 | 0.000041 | MATCHES PRINTED PRECISION |
| mlp | 0 Adipose | recall | 0.964500 | 0.957617 | 0.006883 | SMALL DIFFERENCE |
| mlp | 0 Adipose | f1 | 0.825900 | 0.830189 | 0.004289 | SMALL DIFFERENCE |
| mlp | 1 Background | recall | 0.639900 | 0.638695 | 0.001205 | SMALL DIFFERENCE |
| mlp | 1 Background | f1 | 0.690600 | 0.680745 | 0.009855 | SMALL DIFFERENCE |
| mlp | 2 Debris | recall | 0.138000 | 0.139111 | 0.001111 | SMALL DIFFERENCE |
| mlp | 2 Debris | f1 | 0.221400 | 0.205734 | 0.015666 | NOTICE (>0.01) |
| mlp | 3 Lymphocytes | recall | 0.668500 | 0.682713 | 0.014213 | NOTICE (>0.01) |
| mlp | 3 Lymphocytes | f1 | 0.550900 | 0.553191 | 0.002291 | SMALL DIFFERENCE |
| mlp | 4 Mucus | recall | 0.529200 | 0.530529 | 0.001329 | SMALL DIFFERENCE |
| mlp | 4 Mucus | f1 | 0.518600 | 0.532698 | 0.014098 | NOTICE (>0.01) |
| mlp | 5 Smooth muscle | recall | 0.442200 | 0.455224 | 0.013024 | NOTICE (>0.01) |
| mlp | 5 Smooth muscle | f1 | 0.431100 | 0.416738 | 0.014362 | NOTICE (>0.01) |
| mlp | 6 Normal colon mucosa | recall | 0.082100 | 0.032258 | 0.049842 | INVESTIGATE (>0.02) |
| mlp | 6 Normal colon mucosa | f1 | 0.132200 | 0.057971 | 0.074229 | SIGNIFICANT RISK (>0.05) |
| mlp | 7 Cancer-associated stroma | recall | 0.127900 | 0.134071 | 0.006171 | SMALL DIFFERENCE |
| mlp | 7 Cancer-associated stroma | f1 | 0.181300 | 0.180913 | 0.000387 | SMALL DIFFERENCE |
| mlp | 8 Colorectal adenocarcinoma epithelium | recall | 0.701900 | 0.659284 | 0.042616 | INVESTIGATE (>0.02) |
| mlp | 8 Colorectal adenocarcinoma epithelium | f1 | 0.490000 | 0.489873 | 0.000127 | SMALL DIFFERENCE |
| cnn | 0 Adipose | recall | 0.975900 | 0.973654 | 0.002246 | SMALL DIFFERENCE |
| cnn | 0 Adipose | f1 | 0.905900 | 0.903294 | 0.002606 | SMALL DIFFERENCE |
| cnn | 1 Background | recall | 0.923100 | 0.930070 | 0.006970 | SMALL DIFFERENCE |
| cnn | 1 Background | f1 | 0.946800 | 0.951699 | 0.004899 | SMALL DIFFERENCE |
| cnn | 2 Debris | recall | 0.264500 | 0.391106 | 0.126606 | SIGNIFICANT RISK (>0.05) |
| cnn | 2 Debris | f1 | 0.402400 | 0.506647 | 0.104247 | SIGNIFICANT RISK (>0.05) |
| cnn | 3 Lymphocytes | recall | 0.953000 | 0.952954 | 0.000046 | SMALL DIFFERENCE |
| cnn | 3 Lymphocytes | f1 | 0.921700 | 0.916842 | 0.004858 | SMALL DIFFERENCE |
| cnn | 4 Mucus | recall | 0.686600 | 0.687924 | 0.001324 | SMALL DIFFERENCE |
| cnn | 4 Mucus | f1 | 0.689800 | 0.705146 | 0.015346 | NOTICE (>0.01) |
| cnn | 5 Smooth muscle | recall | 0.764000 | 0.722015 | 0.041985 | INVESTIGATE (>0.02) |
| cnn | 5 Smooth muscle | f1 | 0.700000 | 0.713364 | 0.013364 | NOTICE (>0.01) |
| cnn | 6 Normal colon mucosa | recall | 0.489700 | 0.514663 | 0.024963 | INVESTIGATE (>0.02) |
| cnn | 6 Normal colon mucosa | f1 | 0.552100 | 0.554941 | 0.002841 | SMALL DIFFERENCE |
| cnn | 7 Cancer-associated stroma | recall | 0.433000 | 0.509225 | 0.076225 | SIGNIFICANT RISK (>0.05) |
| cnn | 7 Cancer-associated stroma | f1 | 0.446700 | 0.505495 | 0.058795 | SIGNIFICANT RISK (>0.05) |
| cnn | 8 Colorectal adenocarcinoma epithelium | recall | 0.856000 | 0.856899 | 0.000899 | SMALL DIFFERENCE |
| cnn | 8 Colorectal adenocarcinoma epithelium | f1 | 0.715300 | 0.751868 | 0.036568 | INVESTIGATE (>0.02) |

完整逐类表亦见 `per_class_comparison.csv`，混淆矩阵见每次运行的 `*_confusion_matrix_verified.csv`。
