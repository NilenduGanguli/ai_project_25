FROM python:3.12-slim

# Install system dependencies including PostgreSQL client
RUN apt-get update && \
    apt-get install -y curl postgresql-client && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy frontend code
COPY frontend/ ./frontend/

# Copy environment and entrypoint scripts
COPY env.sh .
COPY entrypoint.sh .

# Make scripts executable
RUN chmod +x entrypoint.sh env.sh

# Expose ports
EXPOSE 8005 8501

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
