#!/bin/bash

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}Starting Sentiment Analyzer Service...${NC}"

# Create network if it doesn't exist
if ! docker network ls | grep -q "citi-intern-network"; then
    docker network create citi-intern-network
fi

# Start the service
docker-compose up -d --build

echo -e "${GREEN}Service started!${NC}"
echo -e "${YELLOW}API: http://localhost:8002${NC}"
echo -e "${YELLOW}Docs: http://localhost:8002/docs${NC}"
