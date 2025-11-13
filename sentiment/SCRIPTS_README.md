# Sentiment Analyzer Service - Build Scripts

This directory contains scripts to easily build and run the Sentiment Analyzer service.

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
   PORT=8002
   ```

## Service Information

Once running, the service will be available at:
- **API**: http://localhost:8002
- **Interactive API Docs**: http://localhost:8002/docs
- **ReDoc Documentation**: http://localhost:8002/redoc
- **Health Check**: http://localhost:8002/

## Useful Docker Commands

### View Logs
```bash
docker logs -f sentiment-analyzer-api
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
docker ps | grep sentiment-analyzer-api
```

## Troubleshooting

### Container won't start
1. Check if port 8002 is already in use:
   ```bash
   lsof -i :8002
   ```

2. View container logs:
   ```bash
   docker logs sentiment-analyzer-api
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

### POST /sentiment-pdf
Analyze sentiment of PDF documents.

**Request:**
- Content-Type: multipart/form-data
- Body:
  - file: PDF file
  - mode: "vector" or "multimodal" (default: "multimodal")

**Response:**
```json
{
  "message": "PDF sentiment analyzed successfully",
  "mode": "multimodal",
  "filename": "document.pdf",
  "result": {
    "sentiment": "positive",
    "confidence": 0.92,
    "explanation": "The document expresses positive sentiments...",
    "key_phrases": ["excellent service", "highly satisfied"]
  }
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

## Analysis Modes

### Multimodal Mode (Default)
- Uses Gemini Vision to analyze PDF directly
- Processes text, images, and layout together
- Best for complex documents with visual elements
- Slower but more accurate

### Vector Mode
- Extracts text and analyzes using embeddings
- Faster processing
- Good for text-heavy documents
- Uses FAISS for semantic search

## Integration with Other Services

This service is part of the `citi-intern-network` Docker network and can communicate with:
- Analyzer Service (port 8001)
- Summarizer Service (port 8003)
- Doc Classifier (port 8004)
- Image Data Extractor (port 8005)
- OCR Service (port 8006)
- CSV Analyzer (port 8501)
- UI Service (port 8500)

## Example Usage

### Using curl

```bash
# Multimodal analysis
curl -X POST "http://localhost:8002/sentiment-pdf" \
  -F "file=@document.pdf" \
  -F "mode=multimodal"

# Vector-based analysis
curl -X POST "http://localhost:8002/sentiment-pdf" \
  -F "file=@document.pdf" \
  -F "mode=vector"
```

### Using Python

```python
import requests

url = "http://localhost:8002/sentiment-pdf"

with open("document.pdf", "rb") as f:
    files = {"file": f}
    data = {"mode": "multimodal"}
    response = requests.post(url, files=files, data=data)
    
print(response.json())
```

## Support

For issues or questions:
1. Check the service logs
2. Verify environment configuration
3. Ensure all prerequisites are met
4. Review the main README.md in the project root
