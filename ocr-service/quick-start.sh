#!/bin/bash

# Quick Start Script for OCR Service
# Simple one-command build and run

set -e

cd "$(dirname "$0")"

echo "🚀 Starting OCR Service..."
echo ""

# Create network if doesn't exist
docker network create citi-intern-network 2>/dev/null || true

# Stop existing container
docker-compose down 2>/dev/null || true

# Build and start
docker-compose up --build -d

echo ""
echo "✅ Service started successfully!"
echo ""
echo "📍 API URL: http://localhost:8006"
echo "📚 API Docs: http://localhost:8006/docs"
echo ""
echo "🔧 Endpoints:"
echo "   POST /extract-text       - Extract text from single file"
echo "   POST /extract-text-batch - Extract text from multiple files"
echo ""
echo "📋 View logs: docker-compose logs -f"
echo "🛑 Stop service: docker-compose down"
echo ""
