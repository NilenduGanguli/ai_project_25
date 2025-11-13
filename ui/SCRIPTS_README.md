# KYC Ops UI - Build Scripts

This directory contains scripts to build and run the KYC Ops Document Service Hub UI (Streamlit application).

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

- **Container Name:** `ui-app`
- **Streamlit Port:** `8502`
- **HTTP Server Port:** `9001`
- **Network:** `citi-intern-network`
- **Health Check:** `http://localhost:8502/_stcore/health`

## Features

### 📊 Integrated Services Dashboard

The UI provides a unified interface for all backend services:

1. **Document Classifier** (port 8004)
   - Multi-page PDF classification
   - Document type detection
   - Confidence scoring

2. **Document Extraction** (port 8005)
   - Structured data extraction
   - Schema generation and approval
   - Multi-format support

3. **Ops Document Query Tool** (port 8001)
   - PDF analysis and querying
   - Page-specific analysis
   - Multi-document support

4. **Sentiment Analysis** (port 8002)
   - PDF sentiment analysis
   - Multimodal and vector modes
   - Sentiment scoring

5. **Document Summarizer** (port 8003)
   - PDF summarization
   - Multiple summary modes
   - Adjustable length

6. **OCR Service** (port 8006)
   - Text extraction from images
   - PDF text extraction
   - Vision-based OCR

## Using the Application

### 1. Access the Dashboard
Open http://localhost:8502 in your browser

### 2. Service Overview
- View all available services
- See service descriptions and features
- Check service status

### 3. Select a Service
Click on any service card to:
- Upload documents (PDF/images)
- Configure service-specific options
- View results and outputs

### 4. View Results
- Structured JSON responses
- Visualizations (where applicable)
- Download results

## Environment Variables

Required in `.env`:
```bash
GOOGLE_API_KEY=your_api_key_here
```

Optional (LangSmith tracing):
```bash
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=your_langsmith_key
LANGSMITH_PROJECT=your_project_name
```

## Docker Commands

### View Logs
```bash
docker logs -f ui-app
```

### Stop Service
```bash
docker stop ui-app
```

### Restart Service
```bash
docker restart ui-app
```

### Remove Container
```bash
docker rm -f ui-app
```

### Rebuild Image
```bash
docker build -t kyc-ops-ui .
```

## Troubleshooting

### Service Not Starting
1. Check environment file exists: `ls -la .env`
2. Verify API key is set: `grep GOOGLE_API_KEY .env`
3. Check logs: `docker logs ui-app`

### Port Already in Use
```bash
# Find process using port 8502
lsof -i :8502

# Kill the process
kill -9 <PID>

# Or find port 9001 (HTTP server)
lsof -i :9001
```

### Cannot Connect to Backend Services
```bash
# Check all services are running
docker ps | grep -E "analyzer|sentiment|summarizer|doc_classify|image_extractor|ocr"

# Verify network connectivity
docker network inspect citi-intern-network

# Check UI is on the same network
docker inspect ui-app | grep NetworkMode
```

### Health Check Failing
```bash
# Check service status
docker ps | grep ui-app

# View detailed logs
docker logs --tail 100 ui-app

# Test health endpoint
curl http://localhost:8502/_stcore/health
```

### Volume Issues
```bash
# Create directories if missing
mkdir -p uploads temp plots

# Check permissions
ls -la uploads temp plots

# Fix permissions if needed
chmod 755 uploads temp plots
```

## Development Tips

1. **Fast Iteration:** Use `quick-start.sh` for quick rebuilds during development
2. **Production Deploy:** Use `build-and-run.sh` for thorough validation
3. **Monitor Logs:** Keep logs open during testing: `docker logs -f ui-app`
4. **Backend Testing:** Test individual backend services first before integrating with UI

## Service Integration

### Backend Service URLs (from UI perspective)
```python
# When UI is in citi-intern-network:
analyzer: http://pdf-analyzer-api:8001
sentiment: http://sentiment-analyzer-api:8002
summarizer: http://summarizer-api:8003
doc-classify: http://doc_classify_app:8004
image-extractor: http://image_extractor_app:8005
ocr: http://ocr-service:8006
```

### Testing Backend Connectivity
```bash
# From within UI container
docker exec ui-app curl -s http://pdf-analyzer-api:8001/health
docker exec ui-app curl -s http://sentiment-analyzer-api:8002/health
docker exec ui-app curl -s http://summarizer-api:8003/health
docker exec ui-app curl -s http://doc_classify_app:8004/health
docker exec ui-app curl -s http://image_extractor_app:8005/health
docker exec ui-app curl -s http://ocr-service:8006/health
```

## Architecture

```
┌─────────────────────────────────────────┐
│      KYC Ops UI (Streamlit)             │
│         Port: 8502, 9001                │
│  - Service dashboard                    │
│  - File upload interface                │
│  - Result visualization                 │
└─────────────┬───────────────────────────┘
              │
              │ citi-intern-network
              ▼
┌─────────────────────────────────────────┐
│        Backend Services                 │
│                                         │
│  📄 Doc Classifier      (8004)         │
│  📊 Data Extractor      (8005)         │
│  📋 Query Tool          (8001)         │
│  💬 Sentiment           (8002)         │
│  📝 Summarizer          (8003)         │
│  🔍 OCR                 (8006)         │
└─────────────────────────────────────────┘
```

## Features by Service

### Document Classifier
- Upload PDF
- View page-by-page classifications
- See confidence scores
- Read classification reasoning

### Document Extraction
- Upload document/image
- Generate schema automatically
- Approve/regenerate schema
- Extract structured data
- View JSON results

### Ops Query Tool
- Upload single/multiple PDFs
- Ask questions about documents
- Get page-specific answers
- Receive detailed analysis

### Sentiment Analysis
- Upload PDF
- Choose analysis mode (multimodal/vector/hybrid)
- Select summary length
- View sentiment scores and analysis

### Document Summarizer
- Upload PDF
- Choose summary mode
- Select length (short/medium/long)
- Get comprehensive summaries

## Production Notes

- UI connects to backend services via Docker network
- Files are stored in mounted volumes (uploads/, temp/, plots/)
- HTTP server on port 9001 serves temporary files
- All services should be running before starting UI
- Health checks ensure service availability

## Common Workflows

### 1. Document Classification
1. Open UI → Select "Document Classifier"
2. Upload PDF
3. View classifications by page
4. Check confidence scores

### 2. Data Extraction
1. Open UI → Select "Document Extraction"
2. Upload document
3. Review generated schema
4. Approve or regenerate
5. Extract and view data

### 3. Document Analysis
1. Open UI → Select "Ops Document Query"
2. Upload PDF(s)
3. Ask questions
4. Review answers with sources

All services are accessible through the unified dashboard interface!
