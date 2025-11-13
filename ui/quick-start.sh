#!/bin/bash

# Quick start script for UI
SERVICE_NAME="ui-app"
IMAGE_NAME="kyc-ops-ui"
NETWORK="citi-intern-network"

echo "🚀 Quick starting KYC Ops UI..."

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
    -p 8502:8502 \
    -p 9001:9001 \
    --env-file .env \
    -v "$(pwd)/uploads:/app/uploads" \
    -v "$(pwd)/temp:/app/temp" \
    -v "$(pwd)/plots:/app/plots" \
    $IMAGE_NAME

echo "✅ Service started on http://localhost:8502"
echo "🌐 UI ready to connect to all backend services"
