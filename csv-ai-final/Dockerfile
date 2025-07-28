FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim AS production

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

RUN groupadd -r appuser && useradd -r -g appuser -m appuser

WORKDIR /app

RUN mkdir -p /app/temp /app/plots /home/appuser/.streamlit /home/appuser/.config/matplotlib && \
    chown -R appuser:appuser /app /home/appuser

COPY --chown=appuser:appuser streamlit_app.py .
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser .streamlit/config.toml /home/appuser/.streamlit/config.toml

USER appuser

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_CONFIG_DIR=/home/appuser/.streamlit \
    MPLCONFIGDIR=/home/appuser/.config/matplotlib \
    HOME=/home/appuser

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]