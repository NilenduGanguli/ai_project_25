#!/bin/bash

# Frontend Run Script for Image Data Extractor
# This script provides easy commands to run, build, and manage the frontend

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_URL="${API_BASE_URL:-http://localhost:8005}"
STREAMLIT_PORT="${STREAMLIT_PORT:-8501}"

# Helper Functions
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_header() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  Image Data Extractor - Frontend Manager      ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python installation
check_python() {
    if ! command_exists python3; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    
    python_version=$(python3 --version | cut -d' ' -f2)
    print_info "Python version: $python_version"
}

# Check if backend is running
check_backend() {
    print_info "Checking backend API at $API_URL..."
    
    if curl -f -s "$API_URL/" > /dev/null 2>&1; then
        print_success "Backend API is running"
        return 0
    else
        print_warning "Backend API is not responding at $API_URL"
        print_warning "Please ensure the backend service is running"
        return 1
    fi
}

# Install dependencies
install_deps() {
    print_header
    print_info "Installing Python dependencies..."
    
    check_python
    
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
        print_success "Dependencies installed successfully"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

# Run local development server
run_local() {
    print_header
    print_info "Starting Streamlit frontend..."
    
    check_python
    
    # Check if dependencies are installed
    if ! python3 -c "import streamlit" 2>/dev/null; then
        print_warning "Streamlit not found. Installing dependencies..."
        install_deps
    fi
    
    # Check backend
    check_backend
    
    print_info "Frontend will be available at: http://localhost:$STREAMLIT_PORT"
    print_info "Press Ctrl+C to stop"
    echo ""
    
    # Run streamlit
    streamlit run app.py --server.port="$STREAMLIT_PORT" --server.address=0.0.0.0
}

# Build Docker image
build_docker() {
    print_header
    print_info "Building Docker image..."
    
    if ! command_exists docker; then
        print_error "Docker is not installed"
        exit 1
    fi
    
    docker build -t image-extractor-frontend:latest .
    print_success "Docker image built successfully"
}

# Run with Docker
run_docker() {
    print_header
    print_info "Running frontend in Docker container..."
    
    if ! command_exists docker; then
        print_error "Docker is not installed"
        exit 1
    fi
    
    # Stop existing container if running
    if docker ps -a --format '{{.Names}}' | grep -q "^image-extractor-frontend$"; then
        print_info "Stopping existing container..."
        docker stop image-extractor-frontend >/dev/null 2>&1 || true
        docker rm image-extractor-frontend >/dev/null 2>&1 || true
    fi
    
    print_info "Starting container..."
    docker run -d \
        --name image-extractor-frontend \
        -p "$STREAMLIT_PORT:8501" \
        -e API_BASE_URL="$API_URL" \
        --add-host=host.docker.internal:host-gateway \
        image-extractor-frontend:latest
    
    print_success "Frontend container started"
    print_info "Access at: http://localhost:$STREAMLIT_PORT"
    print_info "View logs: docker logs -f image-extractor-frontend"
}

# Run with docker-compose
run_compose() {
    print_header
    print_info "Starting services with docker-compose..."
    
    if ! command_exists docker-compose && ! docker compose version >/dev/null 2>&1; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check for .env file
    if [ ! -f ".env" ]; then
        print_warning ".env file not found"
        if [ -f ".env.example" ]; then
            print_info "Creating .env from .env.example..."
            cp .env.example .env
            print_warning "Please edit .env file with your configuration"
            exit 0
        fi
    fi
    
    # Use docker compose or docker-compose
    if docker compose version >/dev/null 2>&1; then
        COMPOSE_CMD="docker compose"
    else
        COMPOSE_CMD="docker-compose"
    fi
    
    $COMPOSE_CMD up -d
    
    print_success "Services started successfully"
    echo ""
    print_info "Services:"
    print_info "  Frontend: http://localhost:8501"
    print_info "  Backend API: http://localhost:8005"
    print_info "  MongoDB: localhost:27017"
    echo ""
    print_info "View logs: $COMPOSE_CMD logs -f"
    print_info "Stop services: $COMPOSE_CMD down"
}

# Stop Docker services
stop_docker() {
    print_header
    print_info "Stopping Docker services..."
    
    # Stop standalone container
    if docker ps --format '{{.Names}}' | grep -q "^image-extractor-frontend$"; then
        print_info "Stopping frontend container..."
        docker stop image-extractor-frontend
        docker rm image-extractor-frontend
        print_success "Frontend container stopped"
    fi
    
    # Stop docker-compose services
    if [ -f "docker-compose.yml" ]; then
        if docker compose version >/dev/null 2>&1; then
            COMPOSE_CMD="docker compose"
        else
            COMPOSE_CMD="docker-compose"
        fi
        
        if $COMPOSE_CMD ps -q 2>/dev/null | grep -q .; then
            print_info "Stopping docker-compose services..."
            $COMPOSE_CMD down
            print_success "Docker-compose services stopped"
        fi
    fi
}

# View logs
view_logs() {
    print_header
    
    if docker ps --format '{{.Names}}' | grep -q "^image-extractor-frontend$"; then
        print_info "Viewing frontend logs (Ctrl+C to exit)..."
        docker logs -f image-extractor-frontend
    elif [ -f "docker-compose.yml" ]; then
        if docker compose version >/dev/null 2>&1; then
            COMPOSE_CMD="docker compose"
        else
            COMPOSE_CMD="docker-compose"
        fi
        
        print_info "Viewing all service logs (Ctrl+C to exit)..."
        $COMPOSE_CMD logs -f
    else
        print_error "No running containers found"
    fi
}

# Show status
show_status() {
    print_header
    
    # Check Python
    if command_exists python3; then
        python_version=$(python3 --version | cut -d' ' -f2)
        print_success "Python: $python_version"
    else
        print_error "Python: Not installed"
    fi
    
    # Check Streamlit
    if python3 -c "import streamlit" 2>/dev/null; then
        streamlit_version=$(python3 -c "import streamlit; print(streamlit.__version__)")
        print_success "Streamlit: $streamlit_version"
    else
        print_warning "Streamlit: Not installed"
    fi
    
    # Check Docker
    if command_exists docker; then
        docker_version=$(docker --version | cut -d' ' -f3 | tr -d ',')
        print_success "Docker: $docker_version"
        
        # Check running containers
        if docker ps --format '{{.Names}}' | grep -q "image-extractor-frontend"; then
            print_success "Frontend container: Running"
        else
            print_info "Frontend container: Not running"
        fi
    else
        print_info "Docker: Not installed"
    fi
    
    # Check backend
    echo ""
    check_backend
    
    echo ""
    print_info "Configuration:"
    print_info "  API URL: $API_URL"
    print_info "  Streamlit Port: $STREAMLIT_PORT"
}

# Show help
show_help() {
    print_header
    echo "Usage: ./run.sh [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  install         Install Python dependencies"
    echo "  run             Run frontend locally (default)"
    echo "  docker-build    Build Docker image"
    echo "  docker-run      Run frontend in Docker container"
    echo "  compose         Run all services with docker-compose"
    echo "  stop            Stop all Docker services"
    echo "  logs            View logs from running containers"
    echo "  status          Show system status"
    echo "  help            Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  API_BASE_URL       Backend API URL (default: http://localhost:8005)"
    echo "  STREAMLIT_PORT     Frontend port (default: 8501)"
    echo ""
    echo "Examples:"
    echo "  ./run.sh run                    # Run locally"
    echo "  ./run.sh compose                # Run with docker-compose"
    echo "  API_BASE_URL=http://api:8005 ./run.sh run"
    echo ""
}

# Main script logic
main() {
    case "${1:-run}" in
        install)
            install_deps
            ;;
        run|local)
            run_local
            ;;
        docker-build|build)
            build_docker
            ;;
        docker-run|docker)
            run_docker
            ;;
        compose|up)
            run_compose
            ;;
        stop|down)
            stop_docker
            ;;
        logs)
            view_logs
            ;;
        status)
            show_status
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
