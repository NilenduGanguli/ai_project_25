#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CONTAINER_NAME="sentiment-analyzer-api"
IMAGE_NAME="sentiment-analyzer-api"
NETWORK_NAME="citi-intern-network"
PORT=${PORT:-8002}

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}   Sentiment Analyzer Service - Build & Run${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}❌ Docker is not running. Please start Docker and try again.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker is running${NC}"
}

# Function to check if .env file exists
check_env_file() {
    if [ ! -f .env ]; then
        echo -e "${YELLOW}⚠ .env file not found${NC}"
        if [ -f .env.template ]; then
            echo -e "${YELLOW}  Creating .env from .env.template...${NC}"
            cp .env.template .env
            echo -e "${YELLOW}  Please edit .env file with your API keys${NC}"
            exit 1
        else
            echo -e "${RED}❌ No .env.template found. Please create .env file manually.${NC}"
            exit 1
        fi
    fi
    
    # Check if GOOGLE_API_KEY is set
    if ! grep -q "GOOGLE_API_KEY=.*[a-zA-Z0-9]" .env; then
        echo -e "${RED}❌ GOOGLE_API_KEY not set in .env file${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Environment file configured${NC}"
}

# Function to create Docker network if it doesn't exist
create_network() {
    if ! docker network ls | grep -q "$NETWORK_NAME"; then
        echo -e "${YELLOW}Creating Docker network: $NETWORK_NAME${NC}"
        docker network create "$NETWORK_NAME"
        echo -e "${GREEN}✓ Network created${NC}"
    else
        echo -e "${GREEN}✓ Network $NETWORK_NAME already exists${NC}"
    fi
}

# Function to stop and remove existing container
cleanup_container() {
    if docker ps -a | grep -q "$CONTAINER_NAME"; then
        echo -e "${YELLOW}Stopping and removing existing container...${NC}"
        docker stop "$CONTAINER_NAME" > /dev/null 2>&1
        docker rm "$CONTAINER_NAME" > /dev/null 2>&1
        echo -e "${GREEN}✓ Container cleaned up${NC}"
    fi
}

# Function to build the Docker image
build_image() {
    echo -e "${BLUE}Building Docker image...${NC}"
    if docker-compose build; then
        echo -e "${GREEN}✓ Image built successfully${NC}"
    else
        echo -e "${RED}❌ Failed to build image${NC}"
        exit 1
    fi
}

# Function to start the container
start_container() {
    echo -e "${BLUE}Starting container...${NC}"
    if docker-compose up -d; then
        echo -e "${GREEN}✓ Container started${NC}"
    else
        echo -e "${RED}❌ Failed to start container${NC}"
        exit 1
    fi
}

# Function to check container health
check_health() {
    echo -e "${BLUE}Checking container health...${NC}"
    sleep 5
    
    max_attempts=30
    attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if docker ps | grep -q "$CONTAINER_NAME.*healthy"; then
            echo -e "${GREEN}✓ Container is healthy${NC}"
            return 0
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}❌ Container failed to become healthy${NC}"
    echo -e "${YELLOW}Container logs:${NC}"
    docker logs "$CONTAINER_NAME" --tail 50
    return 1
}

# Function to display service info
display_info() {
    echo ""
    echo -e "${GREEN}================================================${NC}"
    echo -e "${GREEN}   Service is running successfully!${NC}"
    echo -e "${GREEN}================================================${NC}"
    echo ""
    echo -e "${BLUE}Service URLs:${NC}"
    echo -e "  API:           ${GREEN}http://localhost:$PORT${NC}"
    echo -e "  Docs:          ${GREEN}http://localhost:$PORT/docs${NC}"
    echo -e "  ReDoc:         ${GREEN}http://localhost:$PORT/redoc${NC}"
    echo -e "  Health Check:  ${GREEN}http://localhost:$PORT/${NC}"
    echo ""
    echo -e "${BLUE}Useful commands:${NC}"
    echo -e "  View logs:     ${YELLOW}docker logs -f $CONTAINER_NAME${NC}"
    echo -e "  Stop service:  ${YELLOW}docker-compose down${NC}"
    echo -e "  Restart:       ${YELLOW}docker-compose restart${NC}"
    echo ""
}

# Main execution
main() {
    check_docker
    check_env_file
    create_network
    cleanup_container
    build_image
    start_container
    
    if check_health; then
        display_info
    else
        echo -e "${RED}Service failed to start properly. Check logs above.${NC}"
        exit 1
    fi
}

# Run main function
main
