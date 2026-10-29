# Controlled CPU environment for the COMP5318/4318 A2 notebook.
# Build from the package root:
#   docker compose -f environment/compose.yaml build
FROM --platform=linux/amd64 python:3.11.11-slim-bookworm

# Seeds, CPU-only execution and deterministic TensorFlow kernels.
ENV PYTHONHASHSEED=5318 \
    TF_DETERMINISTIC_OPS=1 \
    TF_CPP_MIN_LOG_LEVEL=2 \
    CUDA_VISIBLE_DEVICES=-1 \
    OMP_NUM_THREADS=4 \
    TF_NUM_INTRAOP_THREADS=4 \
    TF_NUM_INTEROP_THREADS=2 \
    KERAS_BACKEND=tensorflow \
    MPLBACKEND=Agg \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

# Fully resolved (transitive) pins, not just the top-level packages,
# so that a rebuild months later installs byte-identical wheels.
COPY environment/requirements-lock.txt /tmp/requirements-lock.txt
RUN python -m pip install --no-cache-dir -r /tmp/requirements-lock.txt \
    && python -m pip check \
    && python -m ipykernel install --sys-prefix --name python3 --display-name "Python 3 (A2 pinned CPU)"

COPY environment/run_notebook.py /opt/a2/run_notebook.py
WORKDIR /workspace/a2
ENTRYPOINT ["python", "/opt/a2/run_notebook.py"]
CMD []
