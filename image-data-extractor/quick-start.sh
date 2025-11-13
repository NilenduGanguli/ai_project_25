#!/bin/bash

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}Starting Image Data Extractor Service...${NC}"

# Create network if it doesn't exist
if ! docker network ls | grep -q "citi-intern-network"; then
    docker network create citi-intern-network
fi

# Start the services
docker-compose up -d --build

echo -e "${GREEN}Services started!${NC}"
echo -e "${YELLOW}API: http://localhost:8005${NC}"
echo -e "${YELLOW}Docs: http://localhost:8005/docs${NC}"
echo -e "${YELLOW}MongoDB: mongodb://localhost:27017${NC}"
echo -e "${YELLOW}Mongo Express: http://localhost:8081${NC}"
