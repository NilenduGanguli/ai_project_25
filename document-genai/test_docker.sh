#!/bin/bash

# Docker Test Script for Document-GenAI
# This script tests the document-genai module via Docker only

set -e

echo "=========================================="
echo "Document-GenAI Docker Test Suite"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if GOOGLE_API_KEY is set
if [ -z "$GOOGLE_API_KEY" ]; then
    echo -e "${RED}❌ GOOGLE_API_KEY environment variable is not set${NC}"
    echo "Please set your Google API key:"
    echo "export GOOGLE_API_KEY='your-api-key-here'"
    exit 1
fi

echo -e "${GREEN}✅ GOOGLE_API_KEY is configured${NC}"

# Function to test endpoint
test_endpoint() {
    local name="$1"
    local url="$2"
    local max_retries=30
    local retry_count=0
    
    echo -n "Testing $name... "
    
    while [ $retry_count -lt $max_retries ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Ready${NC}"
            return 0
        fi
        retry_count=$((retry_count + 1))
        sleep 2
    done
    
    echo -e "${RED}❌ Failed after $max_retries retries${NC}"
    return 1
}

# Step 1: Build the container
echo -e "${YELLOW}Step 1: Building Docker image...${NC}"
docker-compose build
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Docker build successful${NC}"
else
    echo -e "${RED}❌ Docker build failed${NC}"
    exit 1
fi

# Step 2: Start services
echo -e "${YELLOW}Step 2: Starting services...${NC}"
docker-compose up -d
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Services started${NC}"
else
    echo -e "${RED}❌ Failed to start services${NC}"
    exit 1
fi

# Give services time to initialize
echo "Waiting for services to initialize..."
sleep 10

# Step 3: Test all endpoints
echo -e "${YELLOW}Step 3: Testing endpoints...${NC}"

test_endpoint "Landing Page" "http://localhost:8080"
test_endpoint "Classification API" "http://localhost:8000"
test_endpoint "Extraction API" "http://localhost:8001"
test_endpoint "Extraction UI" "http://localhost:8501/_stcore/health"
test_endpoint "Classification UI" "http://localhost:8502/_stcore/health"

# Step 4: Test API functionality with a simple request
echo -e "${YELLOW}Step 4: Testing API functionality...${NC}"

# Test classification API
echo "Testing classification API health..."
response=$(curl -s -w "%{http_code}" http://localhost:8000/ -o /dev/null)
if [ "$response" = "200" ]; then
    echo -e "${GREEN}✅ Classification API health check passed${NC}"
else
    echo -e "${RED}❌ Classification API health check failed (HTTP $response)${NC}"
fi

# Test extraction API
echo "Testing extraction API health..."
response=$(curl -s -w "%{http_code}" http://localhost:8001/ -o /dev/null)
if [ "$response" = "200" ]; then
    echo -e "${GREEN}✅ Extraction API health check passed${NC}"
else
    echo -e "${RED}❌ Extraction API health check failed (HTTP $response)${NC}"
fi

# Step 5: Show container logs
echo -e "${YELLOW}Step 5: Checking container logs...${NC}"
echo "Recent container logs:"
docker-compose logs --tail=20

echo ""
echo "=========================================="
echo -e "${GREEN}✅ Document-GenAI Docker test completed!${NC}"
echo "=========================================="
echo ""
echo "Services are running on:"
echo "  📄 Landing Page:       http://localhost:8080"
echo "  🔍 Classification API: http://localhost:8000/docs"
echo "  📊 Extraction API:     http://localhost:8001/docs"
echo "  🖥️  Classification UI:  http://localhost:8502"
echo "  🖥️  Extraction UI:      http://localhost:8501"
echo ""
echo "To stop services: docker-compose down"
echo "To view logs:     docker-compose logs -f"