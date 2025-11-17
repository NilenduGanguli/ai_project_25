#!/bin/bash
set -e

echo "Starting Image Data Extractor Service..."
echo "Port: ${PORT:-8005}"
echo "Environment: ${ENVIRONMENT:-production}"
echo "MongoDB URI: ${MONGODB_URI:-mongodb://mongodb:27017}"
echo "Database Name: ${DATABASE_NAME:-document_extraction}"

# Check if GOOGLE_API_KEY is set
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "ERROR: GOOGLE_API_KEY environment variable is not set"
    exit 1
fi

echo "GOOGLE_API_KEY is configured"

# Check if MONGODB_URI is set
if [ -z "$MONGODB_URI" ]; then
    echo "WARNING: MONGODB_URI not set, using default: mongodb://mongodb:27017"
    export MONGODB_URI="mongodb://mongodb:27017"
fi

# Check if DATABASE_NAME is set
if [ -z "$DATABASE_NAME" ]; then
    echo "WARNING: DATABASE_NAME not set, using default: document_extraction"
    export DATABASE_NAME="document_extraction"
fi

echo "Starting server..."

# Start the FastAPI server
exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8005}" --workers 1 --loop asyncio
