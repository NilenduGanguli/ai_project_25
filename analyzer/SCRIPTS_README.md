# Analyzer Service - Build & Run Scripts

This directory contains scripts to easily build and run the Analyzer service Docker container.

## Quick Start

For the fastest way to start the service:

```bash
./quick-start.sh
```

This will:
- Create required directories
- Create Docker network
- Build and start the container
- Display service URLs

## Full Build Script

For a more comprehensive build with checks and options:

```bash
./build-and-run.sh
```

This script includes:
- ✅ Pre-flight checks (Docker, Docker Compose)
- ✅ Environment file validation
- ✅ Directory creation
- ✅ Network setup
- ✅ Container health checks
- ✅ API testing
- ✅ Detailed logging
- ✅ Interactive log viewing option

## Prerequisites

1. **Docker** - [Install Docker](https://docs.docker.com/get-docker/)
2. **Docker Compose** - Usually included with Docker Desktop
3. **Environment Variables** - Create `.env` file with:

```bash
PORT=8001
GOOGLE_API_KEY=your_google_api_key_here
LANGSMITH_TRACING=false
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=
OPENROUTER_API_KEY=
```

## Manual Commands

If you prefer running commands manually:

```bash
# Create required directories
mkdir -p uploads faiss_index

# Create Docker network
docker network create citi-intern-network

# Build and start
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop service
docker-compose down
```

## Service URLs

Once running, access the service at:

- **API Endpoint**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **File Server**: http://localhost:9000 (serves uploaded files)

## API Endpoints

- `GET /` - Health check
- `POST /analyze` - Analyze PDF with query (vector or multimodal)
- `POST /vectorstore/ingest` - Add PDF to vector store
- `POST /vectorstore/query` - Query the vector store

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs

# Check container status
docker ps -a

# Rebuild without cache
docker-compose build --no-cache
docker-compose up -d
```

### Port already in use
```bash
# Find process using port 8001
lsof -i :8001

# Kill the process or change PORT in .env file
```

### Permission issues
```bash
# Ensure scripts are executable
chmod +x build-and-run.sh quick-start.sh

# Ensure directories are writable
chmod -R 755 uploads faiss_index
```

### API Key errors
- Verify `GOOGLE_API_KEY` is set in `.env`
- Check API key has correct permissions
- Ensure API quota is not exceeded

## Stopping the Service

```bash
# Stop and remove containers
docker-compose down

# Stop, remove containers, and remove volumes
docker-compose down -v
```

## Updating the Service

```bash
# Pull latest code
git pull

# Rebuild and restart
./build-and-run.sh
```

## Development Mode

To run in development mode with live reload:

```bash
# Edit docker-compose.yml to add volume mount for src/
# Then run:
docker-compose up --build
```

## Files Created by Scripts

- `uploads/` - Stores uploaded PDF files
- `faiss_index/` - Stores FAISS vector index
- `.env` - Environment variables (auto-created if missing)

## Support

For issues or questions:
1. Check logs: `docker-compose logs`
2. Verify environment variables
3. Ensure all prerequisites are installed
4. Review the main documentation
