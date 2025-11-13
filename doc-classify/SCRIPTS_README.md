# Document Classifier Service - Build Scripts

This directory contains scripts to easily build and run the Document Classifier service.

## Prerequisites

- Docker and Docker Compose installed
- Google API key for Gemini

## Quick Start

### Option 1: Quick Start (Recommended for first-time users)

```bash
chmod +x quick-start.sh
./quick-start.sh
```

This script will:
- Create the Docker network if needed
- Build and start the container
- Display service URLs

### Option 2: Full Build Script (Recommended for production)

```bash
chmod +x build-and-run.sh
./build-and-run.sh
```

This comprehensive script will:
- Check if Docker is running
- Verify .env file exists and is configured
- Create Docker network if needed
- Clean up any existing containers
- Build the Docker image
- Start the container
- Perform health checks
- Display service information and useful commands

## Environment Setup

1. Copy the template environment file:
   ```bash
   cp .env.template .env
   ```

2. Edit `.env` and add your credentials:
   ```bash
   GOOGLE_API_KEY=your_actual_api_key_here
   PORT=8004
   ```

## Service Information

Once running, the service will be available at:
- **API**: http://localhost:8004
- **Interactive API Docs**: http://localhost:8004/docs
- **ReDoc Documentation**: http://localhost:8004/redoc
- **Health Check**: http://localhost:8004/

## Useful Docker Commands

### View Logs
```bash
docker logs -f doc_classify_app
```

### Stop Service
```bash
docker-compose down
```

### Restart Service
```bash
docker-compose restart
```

### Rebuild and Restart
```bash
docker-compose up -d --build
```

### Check Container Status
```bash
docker ps | grep doc_classify_app
```

## Troubleshooting

### Container won't start
1. Check if port 8004 is already in use:
   ```bash
   lsof -i :8004
   ```

2. View container logs:
   ```bash
   docker logs doc_classify_app
   ```

### API key issues
- Ensure `GOOGLE_API_KEY` is set correctly in `.env`
- Verify the API key is valid and has proper permissions

### Network issues
If the container can't connect to other services:
```bash
docker network inspect citi-intern-network
```

## Script Features

### build-and-run.sh Features:
- ✅ Pre-flight checks (Docker running, .env configured)
- ✅ Automatic network creation
- ✅ Container cleanup
- ✅ Health monitoring
- ✅ Colored output for better readability
- ✅ Detailed error messages
- ✅ Service information display

### quick-start.sh Features:
- ✅ Minimal configuration
- ✅ Fast startup
- ✅ Network auto-creation
- ✅ One-command deployment

## API Endpoints

### POST /classify-pdf
Classify a PDF document into document types.

**Request:**
- Content-Type: multipart/form-data
- Body: PDF file

**Response:**
```json
{
  "page_classifications": [
    {
      "page_number": 1,
      "classification": "invoice",
      "confidence": 0.95
    }
  ]
}
```

### GET /
Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

## Integration with Other Services

This service is part of the `citi-intern-network` Docker network and can communicate with:
- Analyzer Service (port 8001)
- Sentiment Service (port 8002)
- Summarizer Service (port 8003)
- Image Data Extractor (port 8005)
- OCR Service (port 8006)
- CSV Analyzer (port 8501)
- UI Service (port 8500)

## Support

For issues or questions:
1. Check the service logs
2. Verify environment configuration
3. Ensure all prerequisites are met
4. Review the main README.md in the project root
