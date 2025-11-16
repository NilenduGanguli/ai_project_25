#!/bin/bash
# Environment variables for document extraction service

# API Configuration
export PORT=8005
export FRONTEND_PORT=8501

# Python Configuration
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=/app

# Google API Key (required for Gemini AI)
export GOOGLE_API_KEY="${GOOGLE_API_KEY:-your_api_key_here}"

# PostgreSQL Database Configuration
export DATABASE_URL="${DATABASE_URL:-postgresql+asyncpg://admin:password123@postgres:5432/document_extraction}"

# Document Classification Service Configuration
export MIN_CLASSIFICATION_CONFIDENCE="${MIN_CLASSIFICATION_CONFIDENCE:-0.7}"

# LangSmith Configuration (optional)
export LANGSMITH_TRACING="${LANGSMITH_TRACING:-false}"
export LANGSMITH_ENDPOINT="${LANGSMITH_ENDPOINT:-}"
export LANGSMITH_API_KEY="${LANGSMITH_API_KEY:-}"
export LANGSMITH_PROJECT="${LANGSMITH_PROJECT:-}"

# Streamlit Configuration
export STREAMLIT_SERVER_PORT=${FRONTEND_PORT}
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# API Base URL for frontend
export API_BASE_URL="http://localhost:${PORT}"
