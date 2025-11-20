FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend and frontend code
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY entrypoint.sh /app/
COPY env.sh /app/

# Make scripts executable
RUN chmod +x /app/entrypoint.sh /app/env.sh

# Expose ports
EXPOSE 8000 8001 8080 8501 8502

# Use entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
