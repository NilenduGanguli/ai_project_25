#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Document Extraction Service Management${NC}"
echo "=========================================="

# Function to display usage
usage() {
    echo "Usage: $0 {build|up|down|restart|logs|status|backend-logs|frontend-logs|db-logs}"
    echo ""
    echo "Commands:"
    echo "  build           - Build the Docker images"
    echo "  up              - Start all services (PostgreSQL + Extraction)"
    echo "  down            - Stop and remove all services"
    echo "  restart         - Restart all services"
    echo "  logs            - Show all container logs"
    echo "  backend-logs    - Show backend logs only"
    echo "  frontend-logs   - Show frontend logs only"
    echo "  db-logs         - Show PostgreSQL logs"
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
        echo -e "${YELLOW}Building Docker images...${NC}"
        docker-compose build
        echo -e "${GREEN}Build complete!${NC}"
        ;;
    
    up)
        echo -e "${YELLOW}Starting document extraction service...${NC}"
        docker-compose up -d
        
        echo -e "${GREEN}Services started!${NC}"
        echo -e "${GREEN}Backend API: http://localhost:8005${NC}"
        echo -e "${GREEN}Frontend UI: http://localhost:8504${NC}"
        echo -e "${GREEN}PostgreSQL: postgresql://localhost:5433/document_extraction${NC}"
        ;;
    
    down)
        echo -e "${YELLOW}Stopping and removing containers...${NC}"
        docker-compose down
        echo -e "${GREEN}Containers stopped and removed!${NC}"
        ;;
    
    restart)
        echo -e "${YELLOW}Restarting containers...${NC}"
        docker-compose restart
        echo -e "${GREEN}Containers restarted!${NC}"
        ;;
    
    logs)
        echo -e "${YELLOW}Showing all logs (Ctrl+C to exit)...${NC}"
        docker-compose logs -f
        ;;
    
    backend-logs)
        echo -e "${YELLOW}Showing backend logs (Ctrl+C to exit)...${NC}"
        docker logs -f document-extraction 2>&1 | grep -E "INFO|ERROR|WARNING|uvicorn"
        ;;
    
    frontend-logs)
        echo -e "${YELLOW}Showing frontend logs (Ctrl+C to exit)...${NC}"
        docker logs -f document-extraction 2>&1 | grep -i streamlit
        ;;
    
    db-logs)
        echo -e "${YELLOW}Showing PostgreSQL logs (Ctrl+C to exit)...${NC}"
        docker logs -f document-extraction-postgres
        ;;
    
    status)
        echo -e "${YELLOW}Container status:${NC}"
        docker-compose ps
        
        echo ""
        echo -e "${YELLOW}Testing endpoints:${NC}"
        
        # Test PostgreSQL
        if docker exec document-extraction-postgres pg_isready -U admin -d document_extraction > /dev/null 2>&1; then
            echo -e "${GREEN}✓ PostgreSQL (port 5433): Running${NC}"
        else
            echo -e "${RED}✗ PostgreSQL (port 5433): Not responding${NC}"
        fi
        
        # Test backend
        if curl -s http://localhost:8005/ > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Backend API (port 8005): Running${NC}"
        else
            echo -e "${RED}✗ Backend API (port 8005): Not responding${NC}"
        fi
        
        # Test frontend
        if curl -s http://localhost:8504/_stcore/health > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Frontend UI (port 8504): Running${NC}"
        else
            echo -e "${RED}✗ Frontend UI (port 8504): Not responding${NC}"
        fi
        ;;
    
    *)
        echo -e "${RED}Invalid command: $1${NC}"
        usage
        ;;
esac
