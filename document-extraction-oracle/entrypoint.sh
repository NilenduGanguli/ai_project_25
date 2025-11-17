#!/bin/bash
set -e

# Source environment variables
source /app/env.sh

echo "=========================================="
echo "Starting Document Extraction Service (Oracle)"
echo "=========================================="
echo "Backend Port: ${PORT}"
echo "Frontend Port: ${FRONTEND_PORT}"
echo "Oracle DSN: ${ORACLE_DSN}"
echo "=========================================="

# Note: Oracle database is external, no health check needed

# Start FastAPI backend in background
echo "Starting FastAPI backend..."
cd /app/backend
python main.py &
BACKEND_PID=$!
echo "Backend started with PID: ${BACKEND_PID}"

# Wait for backend to be ready
echo "Waiting for backend to be ready..."
MAX_RETRIES=30
RETRY_COUNT=0
until curl -s http://localhost:${PORT}/ > /dev/null 2>&1; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ ${RETRY_COUNT} -ge ${MAX_RETRIES} ]; then
        echo "Backend failed to start after ${MAX_RETRIES} retries"
        exit 1
    fi
    echo "Waiting for backend... (${RETRY_COUNT}/${MAX_RETRIES})"
    sleep 2
done
echo "Backend is ready!"

# Start Streamlit frontend in foreground
echo "Starting Streamlit frontend..."
cd /app/frontend
exec streamlit run app.py --server.port=${FRONTEND_PORT} --server.address=0.0.0.0
