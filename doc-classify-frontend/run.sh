#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Doc Classify Frontend Management Script${NC}"
echo "========================================"

# Function to display usage
usage() {
    echo "Usage: $0 {build|up|down|restart|logs|status}"
    echo ""
    echo "Commands:"
    echo "  build    - Build the Docker image"
    echo "  up       - Start the frontend container"
    echo "  down     - Stop and remove the frontend container"
    echo "  restart  - Restart the frontend container"
    echo "  logs     - Show container logs"
    echo "  status   - Show container status"
    exit 1
}

# Check if command is provided
if [ $# -eq 0 ]; then
    usage
fi

case "$1" in
    build)
        echo -e "${YELLOW}Building Docker image...${NC}"
        docker build -t doc-classify-frontend:latest .
        echo -e "${GREEN}Build complete!${NC}"
        ;;
    
    up)
        echo -e "${YELLOW}Starting frontend container...${NC}"
        docker run -d \
            --name doc-classify-frontend \
            -p 8502:8501 \
            -e API_BASE_URL=http://host.docker.internal:8004 \
            --add-host=host.docker.internal:host-gateway \
            doc-classify-frontend:latest
        echo -e "${GREEN}Frontend started! Access at: http://localhost:8502${NC}"
        ;;
    
    down)
        echo -e "${YELLOW}Stopping and removing container...${NC}"
        docker stop doc-classify-frontend
        docker rm doc-classify-frontend
        echo -e "${GREEN}Container stopped and removed!${NC}"
        ;;
    
    restart)
        echo -e "${YELLOW}Restarting container...${NC}"
        docker restart doc-classify-frontend
        echo -e "${GREEN}Container restarted!${NC}"
        ;;
    
    logs)
        echo -e "${YELLOW}Showing logs (Ctrl+C to exit)...${NC}"
        docker logs -f doc-classify-frontend
        ;;
    
    status)
        echo -e "${YELLOW}Container status:${NC}"
        docker ps -a --filter name=doc-classify-frontend --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        ;;
    
    *)
        echo -e "${RED}Invalid command: $1${NC}"
        usage
        ;;
esac
