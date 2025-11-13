#!/bin/bash

# Quick start script for Summarizer service
SERVICE_NAME="summarizer-api"
IMAGE_NAME="summarizer-service"
NETWORK="citi-intern-network"

echo "🚀 Quick starting Summarizer service..."

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
    -p 8003:8003 \
    --env-file .env \
    $IMAGE_NAME

echo "✅ Service started on http://localhost:8003"
echo "📖 API docs: http://localhost:8003/docs"
