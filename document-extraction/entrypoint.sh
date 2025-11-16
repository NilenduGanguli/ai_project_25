#!/bin/bash
set -e

# Source environment variables
source /app/env.sh

echo "=========================================="
echo "Starting Document Extraction Service"
echo "=========================================="
echo "Backend Port: ${PORT}"
echo "Frontend Port: ${FRONTEND_PORT}"
echo "MongoDB URI: ${MONGO_URI}"
echo "=========================================="

# Wait for MongoDB to be ready
echo "Waiting for MongoDB to be ready..."
MAX_RETRIES=30
RETRY_COUNT=0
until mongosh "${MONGO_URI}" --eval "db.adminCommand('ping')" > /dev/null 2>&1; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ ${RETRY_COUNT} -ge ${MAX_RETRIES} ]; then
        echo "WARNING: MongoDB not responding after ${MAX_RETRIES} retries"
        echo "Continuing anyway - service will retry connections..."
        break
    fi
    echo "Waiting for MongoDB... (${RETRY_COUNT}/${MAX_RETRIES})"
    sleep 2
done

if [ ${RETRY_COUNT} -lt ${MAX_RETRIES} ]; then
    echo "MongoDB is ready!"
fi

# Start FastAPI backend in background
echo "Starting FastAPI backend..."
cd /app/backend
python main.py &
BACKEND_PID=$!
echo "Backend started with PID: ${BACKEND_PID}"

# Wait for backend to be ready
echo "Waiting for backend to be ready..."
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
