#!/bin/bash

###############################################################################
# Image Data Extractor - Test Runner Script
# 
# This script provides easy test execution with various options
# Usage: ./run_tests.sh [options]
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

###############################################################################
# Helper Functions
###############################################################################

print_header() {
    echo -e "\n${BLUE}============================================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}============================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${CYAN}→ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

show_usage() {
    cat << EOF
${CYAN}Image Data Extractor - Test Runner${NC}

${YELLOW}Usage:${NC}
    ./run_tests.sh [command] [options]

${YELLOW}Commands:${NC}
    all              Run all tests (default)
    unit             Run unit tests only
    integration      Run integration tests only
    e2e              Run end-to-end tests only
    fast             Run fast tests (exclude slow)
    offline          Run offline tests (no LLM/DB)
    coverage         Run tests with coverage report
    quick            Run quick validation tests
    watch            Run tests in watch mode (requires pytest-watch)
    
${YELLOW}Options:${NC}
    -v, --verbose    Verbose output
    -vv              Extra verbose output
    -s               Show print statements
    -x               Stop on first failure
    -k PATTERN       Run tests matching pattern
    --pdb            Drop into debugger on failure
    --html           Generate HTML coverage report
    --term           Show coverage in terminal
    --parallel       Run tests in parallel (requires pytest-xdist)
    -h, --help       Show this help message

${YELLOW}Examples:${NC}
    ./run_tests.sh                    # Run all tests
    ./run_tests.sh unit -v            # Run unit tests with verbose output
    ./run_tests.sh coverage --html    # Generate HTML coverage report
    ./run_tests.sh fast -x            # Run fast tests, stop on first failure
    ./run_tests.sh -k "test_classify" # Run tests matching "test_classify"
    ./run_tests.sh offline            # Run tests without external dependencies

${YELLOW}Coverage Reports:${NC}
    HTML Report: htmlcov/index.html
    Terminal Report: Shown in console with --term option

EOF
}

check_dependencies() {
    print_header "Checking Dependencies"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 not found. Please install Python 3.12+"
        exit 1
    fi
    print_success "Python found: $(python3 --version)"
    
    # Check pip
    if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
        print_error "pip not found. Please install pip"
        exit 1
    fi
    print_success "pip found"
    
    # Check pytest
    if ! python3 -m pytest --version &> /dev/null; then
        print_warning "pytest not found. Installing dependencies..."
        pip3 install -r requirements.txt
    else
        print_success "pytest found: $(python3 -m pytest --version | head -n 1)"
    fi
}

install_dependencies() {
    print_header "Installing Dependencies"
    print_info "Installing packages from requirements.txt..."
    
    if pip3 install -r requirements.txt; then
        print_success "Dependencies installed successfully"
    else
        print_error "Failed to install dependencies"
        exit 1
    fi
}

setup_environment() {
    print_header "Setting Up Test Environment"
    
    # Set PYTHONPATH
    export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"
    print_info "PYTHONPATH set to: ${SCRIPT_DIR}"
    
    # Set test environment variables
    export GOOGLE_API_KEY="${GOOGLE_API_KEY:-test_api_key_12345}"
    export MONGODB_URI="${MONGODB_URI:-mongodb://localhost:27017}"
    export DATABASE_NAME="${DATABASE_NAME:-test_document_extraction}"
    export PORT="${PORT:-8005}"
    
    print_success "Environment configured"
}

run_all_tests() {
    print_header "Running All Tests"
    python3 -m pytest "$@"
}

run_unit_tests() {
    print_header "Running Unit Tests"
    python3 -m pytest -m unit "$@"
}

run_integration_tests() {
    print_header "Running Integration Tests"
    python3 -m pytest -m integration "$@"
}

run_e2e_tests() {
    print_header "Running End-to-End Tests"
    python3 -m pytest -m e2e "$@"
}

run_fast_tests() {
    print_header "Running Fast Tests (Excluding Slow Tests)"
    python3 -m pytest -m "not slow" "$@"
}

run_offline_tests() {
    print_header "Running Offline Tests (No LLM/DB)"
    python3 -m pytest -m "not requires_llm and not requires_db" "$@"
}

run_coverage() {
    print_header "Running Tests with Coverage"
    
    local coverage_opts="--cov=src --cov-report=term-missing"
    
    # Check for HTML option
    if [[ "$*" == *"--html"* ]]; then
        coverage_opts="--cov=src --cov-report=html --cov-report=term-missing"
        print_info "HTML coverage report will be generated in htmlcov/"
    fi
    
    # Remove --html and --term from args
    local filtered_args=("${@}")
    filtered_args=("${filtered_args[@]/--html/}")
    filtered_args=("${filtered_args[@]/--term/}")
    
    python3 -m pytest ${coverage_opts} "${filtered_args[@]}"
    
    if [[ "$*" == *"--html"* ]]; then
        print_success "Coverage report generated"
        print_info "View report: open htmlcov/index.html"
    fi
}

run_quick_tests() {
    print_header "Running Quick Validation Tests"
    print_info "Running fast offline tests for quick validation"
    python3 -m pytest -m "not slow and not requires_llm and not requires_db" -x "$@"
}

run_watch_mode() {
    print_header "Running Tests in Watch Mode"
    
    if ! command -v ptw &> /dev/null; then
        print_warning "pytest-watch not found. Installing..."
        pip3 install pytest-watch
    fi
    
    print_info "Tests will re-run automatically on file changes"
    print_info "Press Ctrl+C to stop"
    ptw "$@"
}

run_parallel() {
    print_header "Running Tests in Parallel"
    
    if ! python3 -c "import xdist" &> /dev/null; then
        print_warning "pytest-xdist not found. Installing..."
        pip3 install pytest-xdist
    fi
    
    python3 -m pytest -n auto "$@"
}

show_test_info() {
    print_header "Test Information"
    
    echo -e "${CYAN}Test Statistics:${NC}"
    total_tests=$(python3 -m pytest --collect-only -q 2>/dev/null | tail -n 1 | awk '{print $1}')
    echo -e "  Total Tests: ${GREEN}${total_tests}${NC}"
    
    echo -e "\n${CYAN}Test Markers:${NC}"
    python3 -m pytest --markers | grep "^@pytest.mark" | head -n 7
    
    echo -e "\n${CYAN}Available Fixtures:${NC}"
    python3 -m pytest --fixtures -q | grep "^conftest" | head -n 10
    echo -e "  ${YELLOW}... and more (run 'pytest --fixtures' for full list)${NC}"
}

###############################################################################
# Main Script
###############################################################################

main() {
    # Show header
    echo -e "${CYAN}"
    cat << "EOF"
╔══════════════════════════════════════════════════════════╗
║  Image Data Extractor - Test Runner                     ║
║  Comprehensive Testing Framework                        ║
╚══════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    
    # Handle help flag
    if [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
        show_usage
        exit 0
    fi
    
    # Check dependencies
    check_dependencies
    
    # Setup environment
    setup_environment
    
    # Parse command
    local command="${1:-all}"
    shift || true
    
    # Handle --parallel flag globally
    if [[ "$@" == *"--parallel"* ]]; then
        local filtered_args=("${@}")
        filtered_args=("${filtered_args[@]/--parallel/}")
        run_parallel "${filtered_args[@]}"
        exit $?
    fi
    
    # Execute command
    case "$command" in
        all)
            run_all_tests "$@"
            ;;
        unit)
            run_unit_tests "$@"
            ;;
        integration)
            run_integration_tests "$@"
            ;;
        e2e)
            run_e2e_tests "$@"
            ;;
        fast)
            run_fast_tests "$@"
            ;;
        offline)
            run_offline_tests "$@"
            ;;
        coverage)
            run_coverage "$@"
            ;;
        quick)
            run_quick_tests "$@"
            ;;
        watch)
            run_watch_mode "$@"
            ;;
        info)
            show_test_info
            ;;
        install)
            install_dependencies
            ;;
        *)
            print_error "Unknown command: $command"
            echo ""
            show_usage
            exit 1
            ;;
    esac
    
    # Show result
    local exit_code=$?
    echo ""
    if [ $exit_code -eq 0 ]; then
        print_success "Tests completed successfully!"
    else
        print_error "Tests failed with exit code: $exit_code"
    fi
    
    exit $exit_code
}

# Run main function
main "$@"
