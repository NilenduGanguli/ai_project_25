FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim AS production

RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

RUN groupadd -r appuser && useradd -r -g appuser -m appuser

WORKDIR /app

RUN mkdir -p /app/temp /app/plots /app/uploads /home/appuser/.streamlit /home/appuser/.config/matplotlib && \
    chown -R appuser:appuser /app /home/appuser

COPY --chown=appuser:appuser main.py .
COPY --chown=appuser:appuser .streamlit /home/appuser/.streamlit

USER appuser

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    STREAMLIT_SERVER_PORT=850 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_CONFIG_DIR=/home/appuser/.streamlit \
    MPLCONFIGDIR=/home/appuser/.config/matplotlib \
    HOME=/home/appuser

EXPOSE 8502
EXPOSE 9001

CMD python3 -m http.server 9001 --directory temp & streamlit run main.py --server.port=8502 --server.address=0.0.0.0