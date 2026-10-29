# Interactive EDA dashboard (optional)

A small Streamlit app we used for the initial exploration of the PathMNIST data
(built with assistance from ChatGPT; Chinese-language UI used inside the group).

Tabs: array structure & class balance · class-balanced image gallery ·
RGB histograms and per-class colour statistics · PCA projection of a random
training subset · basic data audit. The test set is hidden unless explicitly enabled.

```bash
pip install streamlit==1.39.0 plotly==5.24.1    # in addition to environment/requirements-lock.txt
streamlit run tools/eda_dashboard/app.py         # from the package root
```

The notebook (Section 1) reproduces the dashboard's key findings with static, reproducible code,
so the dashboard is not needed to run or mark the notebook.
