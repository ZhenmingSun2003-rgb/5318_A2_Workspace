"""COMP5318 A2 - PathMNIST 中文 EDA 界面（仅组内）。"""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.decomposition import PCA

SEED = 5318
NAMES = {
    0: "脂肪组织 (Adipose)",
    1: "背景 (Background)",
    2: "组织碎屑 (Debris)",
    3: "淋巴细胞 (Lymphocytes)",
    4: "黏液 (Mucus)",
    5: "平滑肌 (Smooth muscle)",
    6: "正常结肠黏膜 (Normal mucosa)",
    7: "肿瘤相关间质 (Cancer-associated stroma)",
    8: "结直肠腺癌上皮 (Tumour epithelium)",
}
CHANNELS = ("红 / R", "绿 / G", "蓝 / B")
ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "Canvas Sources" / "Assignment2Data-1" / "Assignment2Data"

st.set_page_config(
    page_title="COMP5318 A2 · PathMNIST EDA",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

@st.cache_resource(show_spinner="读取原始 NPY 数据中…")
def load_data(directory: str):
    directory = Path(directory)
    arrays = {
        k: np.load(directory / (k + ".npy"), mmap_mode="r", allow_pickle=False)
        for k in ("X_train", "y_train", "X_test", "y_test")
    }
    if arrays["X_train"].ndim != 4 or arrays["X_test"].ndim != 4:
        raise ValueError("预计 X 为 (N,H,W,C) 四维数组，请先核对数据来源。")
    if arrays["X_train"].shape[-1] != 3 or arrays["X_test"].shape[1:] != arrays["X_train"].shape[1:]:
        raise ValueError("预计训练/测试尺寸一致，且图像为 3 通道 RGB。")
    if len(arrays["X_train"]) != len(arrays["y_train"]):
        raise ValueError("训练图像和标签数量不匹配。")
    if len(arrays["X_test"]) != len(arrays["y_test"]):
        raise ValueError("测试图像和标签数量不匹配。")
    return arrays

def rgb_image(img, divisor):
    return np.clip(np.asarray(img, dtype=np.float32) / divisor, 0, 1)

def caption_of(label):
    return f"{int(label)} · {NAMES.get(int(label), '未知类别')}"

def stratified_count(y):
    ids, counts = np.unique(y.astype(int), return_counts=True)
    return pd.DataFrame({
        "类别 ID": ids.astype(int),
        "类别名称": [NAMES.get(int(k), "未知类别") for k in ids],
        "样本数": counts.astype(int),
        "比例": np.round(counts / counts.sum(), 4)
    })

if not DATA.is_dir():
    st.error("无法找到 Canvas 数据目录： " + str(DATA))
    st.info("请确认在本仓库保留了 Canvas Sources/Assignment2Data-1/Assignment2Data 下四个原始文件。")
    st.stop()

try:
    raw = load_data(str(DATA))
except Exception as exc:
    st.exception(exc)
    st.stop()

X = raw["X_train"]
y = np.asarray(raw["y_train"]).reshape(-1).astype(int)
X_test = raw["X_test"]
y_test = np.asarray(raw["y_test"]).reshape(-1).astype(int)
class_ids = np.sort(np.unique(y))
train_min = float(np.min(X))
train_max = float(np.max(X))
if not np.isfinite(train_min) or not np.isfinite(train_max):
    st.error("原始训练像素存在非有限的极值，请先处理数据质量问题。")
    st.stop()
divisor = 255.0 if train_max > 1.0 + 1e-6 else 1.0

st.title("🔬 COMP5318 A2 · PathMNIST 图像探索实验室")
st.caption("仅供小组内部 EDA 与讨论 · 数据来源为 Canvas 课程子集 · 固定随机种子 5318")
st.warning(
    "这次 A2 数据是结直肠组织病理图像（PathMNIST），不是 A1 的大米图像。"
    "本工具不负责训练、调参或正式测试评估；请不要利用测试集观察来改变模型设计。",
    icon="⚠️",
)
with st.sidebar:
    st.header("探索设置")
    st.write("固定种子：", SEED)
    st.write("训练图像数量：", f"{len(X):,}")
    st.write("训练图像尺寸：", " × ".join(str(i) for i in X.shape[1:]))
    st.write("像素归一化分母：", divisor)
    st.divider()
    inspect_test = st.checkbox(
        "解锁测试集的结构/标签概况（谨慎）",
        value=False,
        help="仅用于核对文件。不要在据此选择模型或调整超参数。"
    )
    st.divider()
    st.markdown("**官方类别映射**来自 [MedMNIST info.py](https://github.com/MedMNIST/MedMNIST/blob/main/medmnist/info.py)。")
    st.caption("所有 PCA 与训练图像探索结果都只使用 X_train / y_train。")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📦 数据概览", "🖼️ 图库", "🌈 颜色与强度", "📊 PCA 投影", "🧪 质量与研究边界"
])

with tab1:
    st.subheader("NPY 的四维数据结构")
    st.write("四维 X 的含义：**（样本数 N，高 H，宽 W，RGB 通道 C）**。")
    rows = [{
        "文件": key + ".npy", "维度": str(value.shape),
        "dtype": str(value.dtype), "元素数": f"{value.size:,}"
    } for key, value in raw.items()]
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
    a, b, c = st.columns(3)
    a.metric("训练样本", f"{len(X):,}")
    b.metric("训练类别", f"{len(class_ids)}")
    c.metric("训练原始像素范围", f"{train_min:g} ～ {train_max:g}")
    st.subheader("原始训练集类别数量")
    cls_df = stratified_count(y)
    st.dataframe(cls_df, hide_index=True, use_container_width=True)
    st.plotly_chart(
        px.bar(cls_df, x="类别 ID", y="样本数", hover_name="类别名称",
               title="训练集类别分布（原始 Canvas 子集）"),
        use_container_width=True,
    )
    st.info("本图不代表官网完整 PathMNIST 的类别分布。子集规模与原版可能不同。")
    if inspect_test:
        st.divider()
        st.warning("测试集仅供结构核对。不要利用以下信息做模型选择。")
        st.write("测试图像:", X_test.shape, "测试标签:", y_test.shape)
        st.dataframe(stratified_count(y_test), hide_index=True, use_container_width=True)

with tab2:
    st.subheader("按照训练类别查看真实病理图像")
    selected_class = st.selectbox(
        "选择类别", [int(i) for i in class_ids],
        format_func=caption_of, key="gallery_class"
    )
    per_class = st.slider("展示样本数", min_value=1, max_value=24, value=12, step=1)
    image_indices = np.flatnonzero(y == selected_class)
    n = min(per_class, len(image_indices))
    sample_indices = np.random.default_rng(SEED + int(selected_class)).choice(
        image_indices, size=n, replace=False
    )
    cols = st.columns(4)
    for j, ix in enumerate(sample_indices):
        with cols[j % 4]:
            st.image(rgb_image(X[ix], divisor), caption=f"训练索引 {ix}", use_column_width=True)
    st.caption(
        "每张图像是 28×28 的 RGB 切片块。仅凭这种低分辨率图片，"
        "不宜推断病患信息或做临床诊断；此处用于理解视觉特征和潜在混淆。"
    )

with tab3:
    st.subheader("RGB 像素与类别颜色差异")
    sample_n = st.slider(
        "随机抽样训练图像数量（统计用）",
        min_value=min(100, len(X)), max_value=min(2000, len(X)),
        value=min(600, len(X)), step=1
    )
    indices = np.random.default_rng(SEED).choice(len(X), size=sample_n, replace=False)
    sampled = np.asarray(X[indices], dtype=np.float32) / divisor
    # Downsample pixels within each image for a responsive interactive histogram.
    pixel_values = sampled.reshape(-1, 3)[::max(1, sample_n // 100)]
    hist_data = pd.DataFrame(pixel_values, columns=["R", "G", "B"]).melt(
        var_name="通道", value_name="归一化强度"
    )
    st.plotly_chart(
        px.histogram(hist_data, x="归一化强度", color="通道", nbins=50,
                     opacity=0.65, barmode="overlay",
                     title="抽样训练像素 RGB 直方图（0～1）"),
        use_container_width=True
    )
    mean = sampled.mean(axis=(1, 2))
    std = sampled.std(axis=(1, 2))
    records = []
    for ix, lab, m, s in zip(indices, y[indices], mean, std):
        for chan, avg, sig in zip("RGB", m, s):
            records.append({
                "训练索引": int(ix), "类别": caption_of(lab),
                "通道": chan, "均值": float(avg), "标准差": float(sig)
            })
    color_df = pd.DataFrame(records)
    st.plotly_chart(
        px.box(color_df, x="类别", y="均值", color="通道", points=False,
               title="类别内 RGB 通道平均强度（按图像统计）"),
        use_container_width=True
    )
    st.caption(
        "不同类别的色彩差异不一定等同于组织形态的因果差异；"
        "也可能受到染色、光照、切片来源及采样大小影响。"
    )

with tab4:
    st.subheader("PCA：训练图像的二维视觉探索")
    pca_n = st.slider(
        "PCA 随机抽样量", min_value=min(100, len(X)),
        max_value=min(1500, len(X)), value=min(700, len(X)), step=1
    )
    indices = np.random.default_rng(SEED + 11).choice(len(X), size=pca_n, replace=False)
    features = (np.asarray(X[indices], dtype=np.float32)
                .reshape(pca_n, -1) / divisor)
    projection_model = PCA(n_components=2, svd_solver="randomized", random_state=SEED)
    embedding = projection_model.fit_transform(features)
    scatter_df = pd.DataFrame({
        "主成分 1": embedding[:, 0],
        "主成分 2": embedding[:, 1],
        "类别": [caption_of(i) for i in y[indices]],
        "训练索引": indices,
    })
    fig = px.scatter(
        scatter_df, x="主成分 1", y="主成分 2", color="类别",
        hover_data=["训练索引"], opacity=0.65,
        title="PCA 投影（仅随机训练样本）",
    )
    st.plotly_chart(fig, use_container_width=True)
    ratios = projection_model.explained_variance_ratio_
    st.write(
        f"前两主成分累计解释的像素方差：{float(ratios.sum()):.2%}"
        f"（PC1 {float(ratios[0]):.2%}，PC2 {float(ratios[1]):.2%}）"
    )
    st.info(
        "PCA 仅显示线性投影后的颜色/像素变化，不代表 CNN 学到的特征。"
        "散点重叠不能证明这些类别不可分类；任何投影结果都不能代替独立测试。"
    )

with tab5:
    st.subheader("训练数据质量（抽样检查）")
    audit_n = min(1000, len(X))
    audit_indices = np.random.default_rng(SEED + 99).choice(
        len(X), size=audit_n, replace=False
    )
    audit = np.asarray(X[audit_indices], dtype=np.float32)
    nonfinite = int(np.count_nonzero(~np.isfinite(audit)))
    extreme = int(np.count_nonzero((audit < 0) | (audit > (1.0 if divisor == 1 else 255.0))))
    st.dataframe(pd.DataFrame([
        {"项目": "抽样训练图像数", "检查结果": audit_n},
        {"项目": "非有限像素数", "检查结果": nonfinite},
        {"项目": "超出预计强度范围的像素数", "检查结果": extreme},
        {"项目": "RGB 通道数", "检查结果": X.shape[-1]},
        {"项目": "原始像素类型", "检查结果": str(X.dtype)},
    ]), hide_index=True, use_container_width=True)
    st.markdown(
        """
        #### 使用时需要注意的边界

        - 只有图像与标签，没有病人、玻片和采集中心的分组 ID：
          **无法直接证明患者/切片级独立性**。
        - 原图只有 28×28 像素；细胞或组织形态可能被显著压缩。
        - 小样本与类别不平衡可能影响 Macro-F1 与各类召回率；
          需要按照同一个固定验证协议比较模型。
        - EDA 中的任何「类别很容易区分」直觉都需要在验证集和
          最终独立测试集上用实际模型检验。
        - 不用本工具寻找测试集对策，也不要把这些交互图表当作正式结果。

        数据及类别参考：
        [MedMNIST 官方类别定义](https://github.com/MedMNIST/MedMNIST/blob/main/medmnist/info.py)。
        """
    )
