FROM --platform=linux/amd64 python:3.11.11-slim-bookworm

ENV PYTHONHASHSEED=5318 \
    TF_DETERMINISTIC_OPS=1 \
    CUDA_VISIBLE_DEVICES=-1 \
    OMP_NUM_THREADS=4 \
    TF_NUM_INTRAOP_THREADS=4 \
    TF_NUM_INTEROP_THREADS=2 \
    KERAS_BACKEND=tensorflow \
    MPLBACKEND=Agg \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY requirements-v2.txt /tmp/requirements-v2.txt
RUN python -m pip install --no-cache-dir -r /tmp/requirements-v2.txt \
    && python -m pip check \
    && python -m ipykernel install --sys-prefix --name python3 --display-name 'Python 3 (V2 CPU)'

WORKDIR /workspace/repo
ENTRYPOINT ["python", "/workspace/repo/reproduction_v2/scripts/run_notebooks.py"]
