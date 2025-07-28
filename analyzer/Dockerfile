FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim AS production

RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    poppler-utils \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

RUN groupadd -r appuser && useradd -r -g appuser appuser \
    && mkdir -p /app/uploads \
    && mkdir -p /app/faiss_index \
    && chown -R appuser:appuser /app

WORKDIR /app

COPY --chown=appuser:appuser main.py .
# COPY --chown=appuser:appuser test.py .
COPY --chown=appuser:appuser src/ ./src/

USER appuser

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

EXPOSE ${PORT:-8001}

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import os,urllib.request; urllib.request.urlopen(f'http://localhost:{os.environ.get(\"PORT\",8001)}/')" || exit 1

CMD sh -c "ppython3 -m http.server 9000 --bind 0.0.0.0 --directory /app/uploads & exec python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8001} --workers 1"
