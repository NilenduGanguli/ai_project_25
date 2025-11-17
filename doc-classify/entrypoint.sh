#!/bin/bash
set -e

echo "Starting Document Classifier Service..."
echo "Port: ${PORT:-8004}"
echo "Environment: ${ENVIRONMENT:-production}"

# Check if GOOGLE_API_KEY is set
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "ERROR: GOOGLE_API_KEY environment variable is not set"
    exit 1
fi

echo "GOOGLE_API_KEY is configured"

# Start the FastAPI server
exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8004}" --workers 1
