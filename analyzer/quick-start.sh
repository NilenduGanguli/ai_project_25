#!/bin/bash

# Quick Start Script for Analyzer Service
# Simple one-command build and run

set -e

cd "$(dirname "$0")"

echo "🚀 Starting Analyzer Service..."
echo ""

# Create required directories
mkdir -p uploads faiss_index

# Create network if doesn't exist
docker network create citi-intern-network 2>/dev/null || true

# Stop existing container
docker-compose down 2>/dev/null || true

# Build and start
docker-compose up --build -d

echo ""
echo "✅ Service started successfully!"
echo ""
echo "📍 API URL: http://localhost:8001"
echo "📚 API Docs: http://localhost:8001/docs"
echo "📁 File Server: http://localhost:9000"
echo ""
echo "📋 View logs: docker-compose logs -f"
echo "🛑 Stop service: docker-compose down"
echo ""
