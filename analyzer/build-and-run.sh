#!/bin/bash

# Build and Run Script for Analyzer Service
# This script builds the Docker container and runs the analyzer service

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default values
PORT="${PORT:-8001}"
SERVICE_NAME="pdf-analyzer-api"
NETWORK_NAME="citi-intern-network"

# Function to print colored messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if .env file exists
check_env_file() {
    if [ ! -f "$SCRIPT_DIR/.env" ]; then
        print_warning ".env file not found in $SCRIPT_DIR"
        print_info "Creating .env file with default values..."
        cat > "$SCRIPT_DIR/.env" << EOF
PORT=8001
GOOGLE_API_KEY=your_api_key_here
LANGSMITH_TRACING=false
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=
OPENROUTER_API_KEY=
EOF
        print_warning "Please update .env file with your actual API keys"
        return 1
    fi
    print_success ".env file found"
    return 0
}

# Function to create required directories
create_directories() {
    print_info "Creating required directories..."
    mkdir -p "$SCRIPT_DIR/uploads"
    mkdir -p "$SCRIPT_DIR/faiss_index"
    print_success "Directories created"
}

# Function to check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    print_success "Docker is installed"
}

# Function to check if Docker Compose is installed
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    print_success "Docker Compose is installed"
}

# Function to create Docker network if it doesn't exist
create_network() {
    print_info "Checking Docker network '$NETWORK_NAME'..."
    if ! docker network ls | grep -q "$NETWORK_NAME"; then
        print_info "Creating Docker network '$NETWORK_NAME'..."
        docker network create "$NETWORK_NAME"
        print_success "Network created"
    else
        print_success "Network already exists"
    fi
}

# Function to stop existing container
stop_container() {
    print_info "Checking for existing containers..."
    if docker ps -a | grep -q "$SERVICE_NAME"; then
        print_info "Stopping and removing existing container..."
        docker stop "$SERVICE_NAME" 2>/dev/null || true
        docker rm "$SERVICE_NAME" 2>/dev/null || true
        print_success "Existing container removed"
    else
        print_info "No existing container found"
    fi
}

# Function to build Docker image
build_image() {
    print_info "Building Docker image..."
    cd "$SCRIPT_DIR"
    docker-compose build --no-cache
    print_success "Docker image built successfully"
}

# Function to start container
start_container() {
    print_info "Starting container..."
    cd "$SCRIPT_DIR"
    docker-compose up -d
    print_success "Container started"
}

# Function to show container logs
show_logs() {
    print_info "Showing container logs (Press Ctrl+C to exit)..."
    sleep 2
    docker-compose logs -f
}

# Function to check container health
check_health() {
    print_info "Waiting for container to be healthy..."
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if docker ps | grep -q "$SERVICE_NAME"; then
            local health_status=$(docker inspect --format='{{.State.Health.Status}}' "$SERVICE_NAME" 2>/dev/null || echo "no-health-check")
            
            if [ "$health_status" = "healthy" ]; then
                print_success "Container is healthy!"
                return 0
            elif [ "$health_status" = "no-health-check" ]; then
                # If no health check, just check if container is running
                print_success "Container is running (no health check configured)"
                return 0
            fi
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_warning "Container health check timed out. Check logs for details."
    return 1
}

# Function to display service info
show_service_info() {
    echo ""
    echo "=========================================="
    echo "  Analyzer Service Information"
    echo "=========================================="
    echo "Service Name: $SERVICE_NAME"
    echo "API URL: http://localhost:$PORT"
    echo "Health Check: http://localhost:$PORT/"
    echo "API Docs: http://localhost:$PORT/docs"
    echo "ReDoc: http://localhost:$PORT/redoc"
    echo "File Server: http://localhost:9000"
    echo "Uploads Directory: $SCRIPT_DIR/uploads"
    echo "FAISS Index: $SCRIPT_DIR/faiss_index"
    echo "=========================================="
    echo ""
}

# Function to test API
test_api() {
    print_info "Testing API endpoint..."
    sleep 3
    if curl -s -f "http://localhost:$PORT/" > /dev/null; then
        print_success "API is responding!"
    else
        print_warning "API is not responding yet. Check logs for details."
    fi
}

# Main execution
main() {
    echo "=========================================="
    echo "  Analyzer Service - Build & Run Script"
    echo "=========================================="
    echo ""
    
    # Change to script directory
    cd "$SCRIPT_DIR"
    
    # Pre-flight checks
    check_docker
    check_docker_compose
    
    # Check environment
    if ! check_env_file; then
        print_error "Please configure .env file before running this script"
        exit 1
    fi
    
    # Source .env file
    if [ -f .env ]; then
        export $(cat .env | grep -v '^#' | xargs)
    fi
    
    # Create required directories
    create_directories
    
    # Create Docker network
    create_network
    
    # Stop existing container
    stop_container
    
    # Build image
    build_image
    
    # Start container
    start_container
    
    # Check health
    check_health
    
    # Test API
    test_api
    
    # Show service info
    show_service_info
    
    print_success "Analyzer service is up and running!"
    print_info "To view logs: docker-compose logs -f"
    print_info "To stop service: docker-compose down"
    
    # Ask if user wants to see logs
    echo ""
    read -p "Do you want to view logs now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        show_logs
    fi
}

# Run main function
main
