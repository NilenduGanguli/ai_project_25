#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Service configuration
SERVICE_NAME="summarizer"
CONTAINER_NAME="summarizer-api"
IMAGE_NAME="summarizer-service"
PORT=8003
NETWORK="citi-intern-network"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  PDF Summarizer Service Build & Run${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Step 1: Check if .env file exists
echo -e "${YELLOW}[1/6]${NC} Checking environment configuration..."
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found!${NC}"
    echo "Please create a .env file with required variables."
    exit 1
fi

# Check for required environment variables
if ! grep -q "GOOGLE_API_KEY" .env; then
    echo -e "${RED}Error: GOOGLE_API_KEY not found in .env${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Environment configuration validated${NC}\n"

# Step 2: Check network
echo -e "${YELLOW}[2/6]${NC} Checking Docker network..."
if ! docker network inspect $NETWORK >/dev/null 2>&1; then
    echo -e "${YELLOW}Creating network: $NETWORK${NC}"
    docker network create $NETWORK
else
    echo -e "${GREEN}✓ Network $NETWORK exists${NC}"
fi
echo ""

# Step 3: Stop existing container
echo -e "${YELLOW}[3/6]${NC} Stopping existing containers..."
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "Stopping and removing container: $CONTAINER_NAME"
    docker stop $CONTAINER_NAME >/dev/null 2>&1
    docker rm $CONTAINER_NAME >/dev/null 2>&1
    echo -e "${GREEN}✓ Old container removed${NC}"
else
    echo -e "${GREEN}✓ No existing container found${NC}"
fi
echo ""

# Step 4: Build Docker image
echo -e "${YELLOW}[4/6]${NC} Building Docker image..."
echo -e "${BLUE}Building $IMAGE_NAME...${NC}"
if docker build -t $IMAGE_NAME .; then
    echo -e "${GREEN}✓ Docker image built successfully${NC}\n"
else
    echo -e "${RED}✗ Docker build failed${NC}"
    exit 1
fi

# Step 5: Run container
echo -e "${YELLOW}[5/6]${NC} Starting container..."
docker run -d \
    --name $CONTAINER_NAME \
    --network $NETWORK \
    -p $PORT:$PORT \
    --env-file .env \
    --health-cmd="curl -f http://localhost:$PORT/health || exit 1" \
    --health-interval=30s \
    --health-timeout=10s \
    --health-retries=3 \
    $IMAGE_NAME

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Container started successfully${NC}\n"
else
    echo -e "${RED}✗ Failed to start container${NC}"
    exit 1
fi

# Step 6: Wait for service to be healthy
echo -e "${YELLOW}[6/6]${NC} Waiting for service to be healthy..."
TIMEOUT=60
ELAPSED=0
INTERVAL=2

while [ $ELAPSED -lt $TIMEOUT ]; do
    HEALTH_STATUS=$(docker inspect --format='{{.State.Health.Status}}' $CONTAINER_NAME 2>/dev/null)
    
    if [ "$HEALTH_STATUS" = "healthy" ]; then
        echo -e "${GREEN}✓ Service is healthy!${NC}\n"
        break
    elif [ "$HEALTH_STATUS" = "unhealthy" ]; then
        echo -e "${RED}✗ Service is unhealthy${NC}"
        echo "Checking logs..."
        docker logs --tail 50 $CONTAINER_NAME
        exit 1
    fi
    
    echo -n "."
    sleep $INTERVAL
    ELAPSED=$((ELAPSED + INTERVAL))
done

if [ $ELAPSED -ge $TIMEOUT ]; then
    echo -e "\n${YELLOW}Warning: Health check timeout. Checking logs...${NC}"
    docker logs --tail 20 $CONTAINER_NAME
fi

# Display service information
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}  Service Information${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Container: ${GREEN}$CONTAINER_NAME${NC}"
echo -e "Network:   ${GREEN}$NETWORK${NC}"
echo -e "Port:      ${GREEN}$PORT${NC}"
echo -e "API URL:   ${GREEN}http://localhost:$PORT${NC}"
echo -e "${BLUE}========================================${NC}\n"

echo -e "${GREEN}Available endpoints:${NC}"
echo -e "  GET  /health          - Health check"
echo -e "  GET  /docs            - API documentation"
echo -e "  POST /summarize       - Summarize PDF content"
echo ""

echo -e "${YELLOW}Useful commands:${NC}"
echo -e "  View logs:    ${BLUE}docker logs -f $CONTAINER_NAME${NC}"
echo -e "  Stop service: ${BLUE}docker stop $CONTAINER_NAME${NC}"
echo -e "  Restart:      ${BLUE}docker restart $CONTAINER_NAME${NC}"
echo -e "  Remove:       ${BLUE}docker rm -f $CONTAINER_NAME${NC}"
echo ""

echo -e "${GREEN}✓ Summarizer service is ready!${NC}"
