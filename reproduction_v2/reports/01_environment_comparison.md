# 01 环境比较

V1 源 Commit: `0f2ffeaa118a82a39f4d2585ceca6e1d691e5036`；V2 运行目录见模型比较报告。

| 项目 | V1 记录 | V2 实测 |
|---|---|---|
| baseline.ipynb | Seed: 5318 / Python: 3.11.17 / NumPy: 1.26.4 / scikit-learn: 1.5.2; Machine: Linux-6.17.0-1022-azure-x86_64-with-glibc2.39; Original Canvas data: /home/runner/work/5318_A2_Workspace/5318_A2_Workspace/Canvas Sources/Assig | Python 3.11.11, NumPy 1.26.4, TensorFlow 2.17.1, Keras 3.6.0, Linux-6.18.54.1-microsoft-standard-WSL2-x86_64-with-glibc2.36 |
| Naive_Bayes.ipynb | D: Notebook 未保存版本/硬件输出 | Python 3.11.11, NumPy 1.26.4, TensorFlow 2.17.1, Keras 3.6.0, Linux-6.18.54.1-microsoft-standard-WSL2-x86_64-with-glibc2.36 |
| MLP.ipynb | Python 3.11.15, NumPy 1.26.4, TensorFlow 2.17.1, Keras 3.6.0, Windows-10-10.0.26200-SP0 | Python 3.11.11, NumPy 1.26.4, TensorFlow 2.17.1, Keras 3.6.0, Linux-6.18.54.1-microsoft-standard-WSL2-x86_64-with-glibc2.36 |
| CNN.ipynb | Python 3.12.14, NumPy 1.26.4, TensorFlow 2.17.1, Keras 3.5.0, macOS-26.3-arm64-arm-64bit | Python 3.11.11, NumPy 1.26.4, TensorFlow 2.17.1, Keras 3.6.0, Linux-6.18.54.1-microsoft-standard-WSL2-x86_64-with-glibc2.36 |

V2: Python 3.11.11; `Linux-6.18.54.1-microsoft-standard-WSL2-x86_64-with-glibc2.36`; CPU 数 16。
Docker 镜像 `comp5318-a2-v2:local`；ID `sha256:71253f48695fa0d9149b4f762b0dd242dfc332cc682eddaeaa2931d95831f11e`；架构 `linux/amd64`。
实际 TensorFlow 设备：`['/physical_device:CPU:0']`；cgroup CPU 配额 `400000 100000`；cgroup 内存配置 `10737418240` 字节。
CNN 完整运行期间 Docker stats 采样 26 次，观察到最高内存 1.664 GiB；这是采样峰值，不是精确最大值。
固定包：numpy=1.26.4, pandas=2.2.3, scikit-learn=1.5.2, scipy=1.14.1, matplotlib=3.9.2, tensorflow=2.17.1, keras=3.6.0, ipykernel=6.29.5, nbclient=0.10.2, nbformat=5.10.4, ipython=8.30.0, pillow=10.4.0。
`pip check` 退出码：0；完整依赖见各运行的 `pip-freeze.txt`。
V1 来自不同系统和 CPU，耗时差异不能解释为控制变量后的算法速度差异。
