# Same Linux/AMD64, Python and deterministic CPU strategy as reproduction_v2/Dockerfile.
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
# V2's ACTUALLY RESOLVED transitive pins: stricter than the V2 direct-dependencies file.
COPY reproduction_v2/reference/requirements-v2-resolved.txt /tmp/requirements-v2-resolved.txt
RUN python -m pip install --no-cache-dir -r /tmp/requirements-v2-resolved.txt \
    && python -m pip check \
    && python -m ipykernel install --sys-prefix --name python3 --display-name "Python 3 (V2 CPU)"
COPY integration_v3/scripts/run_v3.py /opt/v3/run_v3.py
WORKDIR /workspace/repo
ENTRYPOINT ["python", "/opt/v3/run_v3.py"]
CMD ["--execute"]
