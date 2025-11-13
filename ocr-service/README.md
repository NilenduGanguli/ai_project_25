# LLM-Based OCR Service

A high-quality Optical Character Recognition (OCR) service powered by Google Gemini Vision AI for extracting text from images and PDF documents.

## Features

- 🤖 **LLM-Powered**: Uses Google Gemini 2.0 Flash for superior text extraction
- 📄 **Multi-Format Support**: Handles PNG, JPG, JPEG, and PDF files
- 🎯 **High Accuracy**: Maintains structure, formatting, and layout
- 📊 **Confidence Scoring**: Provides quality assessment for each extraction
- 🚀 **Fast & Async**: Built with FastAPI for high performance
- 🔄 **Batch Processing**: Extract text from multiple files at once
- 🐳 **Docker Ready**: Easy deployment with Docker and Docker Compose

## Quick Start

### Using the Scripts

**Quick Start** (fastest way):
```bash
cd ocr-service
./quick-start.sh
```

**Full Build** (with checks):
```bash
cd ocr-service
./build-and-run.sh
```

### Manual Setup

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

2. **Configure Environment**:
```bash
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

3. **Run the Service**:
```bash
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --host 0.0.0.0 --port 8006 --reload
```

### Using Docker

```bash
# Build and run
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop service
docker-compose down
```

## API Endpoints

### Health Check
```bash
GET /
```

**Response**:
```json
{
  "status": "healthy",
  "service": "LLM-Based OCR Service",
  "version": "1.0.0"
}
```

### Extract Text from Single File
```bash
POST /extract-text
```

**Parameters**:
- `file` (required): Image or PDF file (PNG, JPG, JPEG, PDF)

**Example Request**:
```bash
curl -X POST http://localhost:8006/extract-text \
  -F "file=@document.png"
```

**Response**:
```json
{
  "text": "Extracted text content here...",
  "confidence": 0.95,
  "message": "Text extracted successfully"
}
```

### Extract Text from Multiple Files
```bash
POST /extract-text-batch
```

**Parameters**:
- `files` (required): Array of image or PDF files

**Example Request**:
```bash
curl -X POST http://localhost:8006/extract-text-batch \
  -F "files=@document1.png" \
  -F "files=@document2.pdf" \
  -F "files=@document3.jpg"
```

**Response**:
```json
{
  "total_files": 3,
  "successful": 3,
  "failed": 0,
  "results": [
    {
      "filename": "document1.png",
      "index": 0,
      "text": "Extracted text...",
      "confidence": 0.95,
      "status": "success"
    },
    {
      "filename": "document2.pdf",
      "index": 1,
      "text": "Extracted text...",
      "confidence": 0.92,
      "status": "success"
    },
    {
      "filename": "document3.jpg",
      "index": 2,
      "text": "Extracted text...",
      "confidence": 0.88,
      "status": "success"
    }
  ]
}
```

## Service URLs

Once running:
- **API Endpoint**: http://localhost:8006
- **API Documentation**: http://localhost:8006/docs
- **ReDoc**: http://localhost:8006/redoc

## Integration with Analyzer Service

The analyzer service is configured to use this OCR service. Update the analyzer's `src/utils/analyzer.py` to use:

```python
import requests

def extract_text_from_image(image):
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        image.save(tmp.name)
        tmp_path = tmp.name
    
    with open(tmp_path, "rb") as f:
        files = {"file": f}
        response = requests.post("http://localhost:8006/extract-text", files=files)
        
        if response.status_code == 200:
            return response.json()["text"]
        else:
            print(f"OCR Error: {response.status_code} - {response.text}")
            return ""
```

## Environment Variables

Required environment variables:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PORT` | Service port | 8006 | No |
| `GOOGLE_API_KEY` | Google Gemini API key | - | Yes |

## Confidence Scoring

The service provides confidence scores for text extraction quality:

- **0.9-1.0**: Crystal clear, all text readable
- **0.7-0.9**: Mostly clear, minor blur or quality issues  
- **0.5-0.7**: Moderate quality, some unclear sections
- **0.0-0.5**: Poor quality, significant illegibility

## Text Extraction Features

The OCR engine:
- ✅ Extracts ALL visible text from images and PDFs
- ✅ Preserves structure, layout, and formatting
- ✅ Maintains line breaks and paragraph structure
- ✅ Handles tables with proper alignment
- ✅ Extracts text in reading order
- ✅ Includes headers, footers, and watermarks
- ✅ Supports multi-language documents
- ✅ Preserves special characters and symbols

## Error Handling

**Unsupported file type**:
```json
{
  "detail": "Unsupported file type: text/plain. Supported types: image/png, image/jpeg, image/jpg, application/pdf"
}
```

**Extraction failure**:
```json
{
  "detail": "Failed to extract text: [error details]"
}
```

## Performance

- **Single Image**: ~2-5 seconds
- **PDF (multi-page)**: ~3-8 seconds
- **Batch Processing**: Parallel processing for multiple files

## Troubleshooting

### Service won't start
```bash
# Check logs
docker-compose logs

# Verify API key
cat .env | grep GOOGLE_API_KEY
```

### Low confidence scores
- Check image quality and resolution
- Ensure text is clearly visible and not too small
- Verify image is not overly compressed

### Port conflicts
```bash
# Change port in .env file
echo "PORT=8007" >> .env

# Restart service
docker-compose down && docker-compose up -d
```

## Development

Run in development mode with auto-reload:
```bash
uvicorn main:app --host 0.0.0.0 --port 8006 --reload
```

## Testing

Test the service:
```bash
# Health check
curl http://localhost:8006/

# Extract text from image
curl -X POST http://localhost:8006/extract-text \
  -F "file=@test_image.png" \
  | jq .
```

## Production Deployment

For production:
1. Use environment-specific `.env` files
2. Enable HTTPS/TLS
3. Configure rate limiting
4. Set up monitoring and logging
5. Use container orchestration (Kubernetes, Docker Swarm)

## License

Part of the KYC Ops Document Service Hub

## Support

For issues or questions, refer to the main project documentation.
