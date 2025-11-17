#!/bin/bash
set -e

# Source environment variables
source /app/env.sh

echo "=========================================="
echo "Starting Document Services"
echo "=========================================="
echo "Classification API Port: 8000"
echo "Extraction API Port: 8001"
echo "Landing Page Port: 8080"
echo "Classification UI Port: 8502"
echo "Extraction UI Port: 8501"
echo "Database URL: ${DATABASE_URL}"
echo "=========================================="

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
MAX_RETRIES=30
RETRY_COUNT=0

# Extract database connection details from DATABASE_URL
DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\(.*\):.*/\1/p')
DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
DB_NAME=$(echo $DATABASE_URL | sed -n 's/.*\/\(.*\)$/\1/p')
DB_USER=$(echo $DATABASE_URL | sed -n 's/.*:\/\/\(.*\):.*/\1/p')

until PGPASSWORD=password123 psql -h "${DB_HOST:-postgres}" -p "${DB_PORT:-5432}" -U "${DB_USER:-admin}" -d "${DB_NAME:-document_services}" -c '\q' > /dev/null 2>&1; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ ${RETRY_COUNT} -ge ${MAX_RETRIES} ]; then
        echo "WARNING: PostgreSQL not responding after ${MAX_RETRIES} retries"
        echo "Continuing anyway - service will retry connections..."
        break
    fi
    echo "Waiting for PostgreSQL... (${RETRY_COUNT}/${MAX_RETRIES})"
    sleep 2
done

if [ ${RETRY_COUNT} -lt ${MAX_RETRIES} ]; then
    echo "PostgreSQL is ready!"
fi

# Start Classification API (port 8000) in background
echo "Starting Classification API on port 8000..."
cd /app/backend
PORT=8000 python classification_main.py &
CLASSIFICATION_PID=$!
echo "Classification API started with PID: ${CLASSIFICATION_PID}"

# Start Extraction API (port 8001) in background
echo "Starting Extraction API on port 8001..."
PORT=8001 python extraction_main.py &
EXTRACTION_PID=$!
echo "Extraction API started with PID: ${EXTRACTION_PID}"

# Wait for Classification API to be ready
echo "Waiting for Classification API to be ready..."
RETRY_COUNT=0
until curl -s http://localhost:8000/ > /dev/null 2>&1; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ ${RETRY_COUNT} -ge ${MAX_RETRIES} ]; then
        echo "Classification API failed to start after ${MAX_RETRIES} retries"
        exit 1
    fi
    echo "Waiting for Classification API... (${RETRY_COUNT}/${MAX_RETRIES})"
    sleep 2
done
echo "Classification API is ready!"

# Wait for Extraction API to be ready
echo "Waiting for Extraction API to be ready..."
RETRY_COUNT=0
until curl -s http://localhost:8001/ > /dev/null 2>&1; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ ${RETRY_COUNT} -ge ${MAX_RETRIES} ]; then
        echo "Extraction API failed to start after ${MAX_RETRIES} retries"
        exit 1
    fi
    echo "Waiting for Extraction API... (${RETRY_COUNT}/${MAX_RETRIES})"
    sleep 2
done
echo "Extraction API is ready!"

# Start simple HTTP server for landing page (port 8080) in background
echo "Starting landing page server on port 8080..."
cd /app/frontend
python3 -m http.server 8080 &
LANDING_PID=$!
echo "Landing page started with PID: ${LANDING_PID}"

# Start Classification Streamlit UI (port 8502) in background
echo "Starting Classification UI (Streamlit) on port 8502..."
export CLASSIFICATION_API_URL="http://localhost:8000"
streamlit run classification_app.py --server.port=8502 --server.address=0.0.0.0 &
CLASSIFICATION_UI_PID=$!
echo "Classification UI started with PID: ${CLASSIFICATION_UI_PID}"

# Start Extraction Streamlit UI (port 8501) in foreground
echo "Starting Extraction UI (Streamlit) on port 8501..."
# Update API_BASE_URL to point to extraction API on port 8001
export API_BASE_URL="http://localhost:8001"
exec streamlit run extraction_app.py --server.port=8501 --server.address=0.0.0.0

