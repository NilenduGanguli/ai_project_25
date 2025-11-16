#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Document Classification Service Management${NC}"
echo "============================================="

# Function to display usage
usage() {
    echo "Usage: $0 {build|up|down|restart|logs|status|backend-logs|frontend-logs}"
    echo ""
    echo "Commands:"
    echo "  build           - Build the Docker image"
    echo "  up              - Start the service container"
    echo "  down            - Stop and remove the service container"
    echo "  restart         - Restart the service container"
    echo "  logs            - Show all container logs"
    echo "  backend-logs    - Show backend logs only"
    echo "  frontend-logs   - Show frontend logs only"
    echo "  status          - Show container status"
    exit 1
}

# Check if command is provided
if [ $# -eq 0 ]; then
    usage
fi

# Source environment variables
if [ -f "./env.sh" ]; then
    source ./env.sh
fi

case "$1" in
    build)
        echo -e "${YELLOW}Building Docker image...${NC}"
        docker build -t document-classification:latest .
        echo -e "${GREEN}Build complete!${NC}"
        ;;
    
    up)
        echo -e "${YELLOW}Starting document classification service...${NC}"
        docker run -d \
            --name document-classification \
            -p 8004:8004 \
            -p 8503:8501 \
            -e PORT=8004 \
            -e FRONTEND_PORT=8501 \
            -e GOOGLE_API_KEY="${GOOGLE_API_KEY}" \
            -e LANGSMITH_TRACING="${LANGSMITH_TRACING:-false}" \
            -e LANGSMITH_ENDPOINT="${LANGSMITH_ENDPOINT:-}" \
            -e LANGSMITH_API_KEY="${LANGSMITH_API_KEY:-}" \
            -e LANGSMITH_PROJECT="${LANGSMITH_PROJECT:-}" \
            document-classification:latest
        
        echo -e "${GREEN}Service started!${NC}"
        echo -e "${GREEN}Backend API: http://localhost:8004${NC}"
        echo -e "${GREEN}Frontend UI: http://localhost:8503${NC}"
        ;;
    
    down)
        echo -e "${YELLOW}Stopping and removing container...${NC}"
        docker stop document-classification
        docker rm document-classification
        echo -e "${GREEN}Container stopped and removed!${NC}"
        ;;
    
    restart)
        echo -e "${YELLOW}Restarting container...${NC}"
        docker restart document-classification
        echo -e "${GREEN}Container restarted!${NC}"
        ;;
    
    logs)
        echo -e "${YELLOW}Showing all logs (Ctrl+C to exit)...${NC}"
        docker logs -f document-classification
        ;;
    
    backend-logs)
        echo -e "${YELLOW}Showing backend logs (Ctrl+C to exit)...${NC}"
        docker logs -f document-classification 2>&1 | grep -E "INFO|ERROR|WARNING|uvicorn"
        ;;
    
    frontend-logs)
        echo -e "${YELLOW}Showing frontend logs (Ctrl+C to exit)...${NC}"
        docker logs -f document-classification 2>&1 | grep -i streamlit
        ;;
    
    status)
        echo -e "${YELLOW}Container status:${NC}"
        docker ps -a --filter name=document-classification --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        
        echo ""
        echo -e "${YELLOW}Testing endpoints:${NC}"
        
        # Test backend
        if curl -s http://localhost:8004/ > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Backend API (port 8004): Running${NC}"
        else
            echo -e "${RED}✗ Backend API (port 8004): Not responding${NC}"
        fi
        
        # Test frontend
        if curl -s http://localhost:8503/_stcore/health > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Frontend UI (port 8503): Running${NC}"
        else
            echo -e "${RED}✗ Frontend UI (port 8503): Not responding${NC}"
        fi
        ;;
    
    *)
        echo -e "${RED}Invalid command: $1${NC}"
        usage
        ;;
esac
