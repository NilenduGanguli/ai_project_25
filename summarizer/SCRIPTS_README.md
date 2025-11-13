# Summarizer Service - Build Scripts

This directory contains scripts to build and run the PDF Summarizer service.

## Available Scripts

### 1. `build-and-run.sh` (Recommended)
Comprehensive build and deployment script with validation and health checks.

**Features:**
- Environment validation
- Docker network setup
- Container cleanup
- Image building with progress
- Health monitoring
- Detailed service information

**Usage:**
```bash
chmod +x build-and-run.sh
./build-and-run.sh
```

### 2. `quick-start.sh`
Fast deployment script for development.

**Usage:**
```bash
chmod +x quick-start.sh
./quick-start.sh
```

## Service Information

- **Container Name:** `summarizer-api`
- **Port:** `8003`
- **Network:** `citi-intern-network`
- **Health Check:** `http://localhost:8003/health`

## API Endpoints

### Health Check
```bash
curl http://localhost:8003/health
```

### Summarize PDF
```bash
curl -X POST http://localhost:8003/summarize \
  -F "file=@document.pdf" \
  -F "mode=hybrid" \
  -F "summary_length=medium"
```

**Parameters:**
- `file`: PDF file to summarize
- `mode`: `multimodal` (Gemini Vision), `vector` (FAISS embeddings), or `hybrid` (both)
- `summary_length`: `short`, `medium`, or `long`

### Interactive API Documentation
Visit: `http://localhost:8003/docs`

## Environment Variables

Required in `.env`:
```properties
GOOGLE_API_KEY=your_api_key_here
PORT=8003
```

## Docker Commands

### View Logs
```bash
docker logs -f summarizer-api
```

### Stop Service
```bash
docker stop summarizer-api
```

### Restart Service
```bash
docker restart summarizer-api
```

### Remove Container
```bash
docker rm -f summarizer-api
```

### Rebuild Image
```bash
docker build -t summarizer-service .
```

## Troubleshooting

### Service Not Starting
1. Check environment file exists: `ls -la .env`
2. Verify API key is set: `grep GOOGLE_API_KEY .env`
3. Check logs: `docker logs summarizer-api`

### Port Already in Use
```bash
# Find process using port 8003
lsof -i :8003

# Or change PORT in .env file
```

### Health Check Failing
```bash
# Check service status
docker ps | grep summarizer-api

# View detailed logs
docker logs --tail 100 summarizer-api

# Test health endpoint
curl http://localhost:8003/health
```

### Network Issues
```bash
# Verify network exists
docker network inspect citi-intern-network

# Recreate network if needed
docker network rm citi-intern-network
docker network create citi-intern-network
```

## Integration with Other Services

The summarizer service can work independently or integrate with other services in the `citi-intern-network`:

- **Standalone:** Upload PDFs directly for summarization
- **With Analyzer:** Get analysis + summary in one workflow
- **With UI:** Frontend interface for document processing

## Development Tips

1. **Fast Iteration:** Use `quick-start.sh` for quick rebuilds during development
2. **Production Deploy:** Use `build-and-run.sh` for thorough validation
3. **Monitor Logs:** Keep logs open during testing: `docker logs -f summarizer-api`
4. **API Testing:** Use the Swagger UI at `/docs` for interactive testing

## Summary Modes

### Multimodal Mode
Uses Gemini 2.0 Flash with vision capabilities to process PDF visually.
- Best for: Documents with complex layouts, images, tables
- Speed: Slower but more comprehensive

### Vector Mode
Uses FAISS for vector-based retrieval and summarization.
- Best for: Text-heavy documents, faster processing
- Speed: Faster, efficient for long documents

### Hybrid Mode (Recommended)
Combines both approaches for comprehensive summaries.
- Best for: Most use cases
- Speed: Balanced
