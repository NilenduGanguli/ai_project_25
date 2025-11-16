FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y curl gnupg && \
    # Add MongoDB tools repository
    curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | gpg --dearmor -o /usr/share/keyrings/mongodb-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/mongodb-archive-keyring.gpg] http://repo.mongodb.org/apt/debian bookworm/mongodb-org/7.0 main" | tee /etc/apt/sources.list.d/mongodb-org-7.0.list && \
    apt-get update && \
    apt-get install -y mongodb-mongosh && \
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
