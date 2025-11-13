#!/bin/bash

# Quick start script for CSV Analysis Agent
SERVICE_NAME="csv-analysis-streamlit"
IMAGE_NAME="csv-analysis-agent"
NETWORK="citi-intern-network"

echo "🚀 Quick starting CSV Analysis Agent..."

# Create network if it doesn't exist
docker network create $NETWORK 2>/dev/null

# Stop and remove existing container
docker stop $SERVICE_NAME 2>/dev/null
docker rm $SERVICE_NAME 2>/dev/null

# Build and run
docker build -t $IMAGE_NAME . && \
docker run -d \
    --name $SERVICE_NAME \
    --network $NETWORK \
    -p 8501:8501 \
    --env-file .env \
    $IMAGE_NAME

echo "✅ Service started on http://localhost:8501"
echo "📊 Open in browser to start analyzing CSV files"
