# OCR Service - Build & Run Scripts

This directory contains scripts to easily build and run the OCR service Docker container.

## Quick Start

For the fastest way to start the service:

```bash
./quick-start.sh
```

This will:
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
PORT=8006
GOOGLE_API_KEY=your_google_api_key_here
```

## Manual Commands

If you prefer running commands manually:

```bash
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

- **API Endpoint**: http://localhost:8006
- **API Documentation**: http://localhost:8006/docs
- **ReDoc**: http://localhost:8006/redoc

## API Endpoints

- `GET /` - Health check
- `POST /extract-text` - Extract text from single image/PDF
- `POST /extract-text-batch` - Extract text from multiple files

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
# Find process using port 8006
lsof -i :8006

# Kill the process or change PORT in .env file
```

### Permission issues
```bash
# Ensure scripts are executable
chmod +x build-and-run.sh quick-start.sh
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

## Testing the Service

```bash
# Health check
curl http://localhost:8006/

# Extract text from image
curl -X POST http://localhost:8006/extract-text \
  -F "file=@test_image.png"

# View response
curl -X POST http://localhost:8006/extract-text \
  -F "file=@test_image.png" | jq .
```

## Integration with Analyzer

The analyzer service automatically uses this OCR service when processing PDFs with no extractable text. Ensure both services are running on the same Docker network.

## Support

For issues or questions:
1. Check logs: `docker-compose logs`
2. Verify environment variables
3. Ensure GOOGLE_API_KEY is valid
4. Review the main documentation
