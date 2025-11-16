# Document Classification Service

A combined frontend and backend service for AI-powered PDF document classification. Both services run in a single container.

## Features

- 🚀 **Single Container Deployment** - Backend and frontend in one container
- 📄 **PDF Classification** - Page-by-page document type identification
- 🤖 **AI-Powered** - Uses Gemini 2.5 Flash for classification
- 🎨 **Web UI** - Beautiful Streamlit interface
- 📊 **Detailed Results** - Confidence scores and reasoning for each page
- 🔌 **REST API** - FastAPI backend for programmatic access

## Architecture

```
┌─────────────────────────────────────────┐
│  Document Classification Container      │
│                                          │
│  ┌──────────────┐  ┌──────────────┐    │
│  │   Backend    │  │   Frontend   │    │
│  │   FastAPI    │  │  Streamlit   │    │
│  │   Port 8004  │  │  Port 8501   │    │
│  └──────────────┘  └──────────────┘    │
│         │                  │            │
│         └──────────────────┘            │
│           localhost                     │
└─────────────────────────────────────────┘
        │                    │
     Port 8004           Port 8503
    (Backend API)      (Frontend UI)
```

## Prerequisites

- Docker
- Google API Key for Gemini AI

## Quick Start

### 1. Set up environment variables

Edit `env.sh` and add your Google API Key:

```bash
export GOOGLE_API_KEY="your_actual_api_key_here"
```

### 2. Build and run

```bash
chmod +x run.sh
./run.sh build
./run.sh up
```

### 3. Access the services

- **Frontend UI**: http://localhost:8503
- **Backend API**: http://localhost:8004
- **API Docs**: http://localhost:8004/docs

## Management Commands

```bash
./run.sh build          # Build Docker image
./run.sh up             # Start service
./run.sh down           # Stop and remove service
./run.sh restart        # Restart service
./run.sh logs           # View all logs
./run.sh backend-logs   # View backend logs only
./run.sh frontend-logs  # View frontend logs only
./run.sh status         # Check service status
```

## Using Docker Compose

```bash
# Set environment variable
export GOOGLE_API_KEY="your_api_key_here"

# Start service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop service
docker-compose down
```

## Environment Variables

All environment variables are managed in `env.sh`:

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Backend API port | 8004 |
| `FRONTEND_PORT` | Frontend UI port | 8501 |
| `GOOGLE_API_KEY` | Google Gemini API key | Required |
| `LANGSMITH_TRACING` | Enable LangSmith tracing | false |
| `LANGSMITH_ENDPOINT` | LangSmith endpoint | - |
| `LANGSMITH_API_KEY` | LangSmith API key | - |
| `LANGSMITH_PROJECT` | LangSmith project name | - |

## API Endpoints

### Backend API (Port 8004)

#### Health Check
```bash
GET /
```

#### Classify PDF
```bash
POST /classify-pdf
Content-Type: multipart/form-data
Body: file (PDF)
```

Response:
```json
{
  "page_classifications": [
    {
      "page": 1,
      "document_type": "Passport",
      "confidence": 0.95,
      "reasoning": "Contains passport number, photo, and government seal"
    }
  ]
}
```

## Frontend Features

1. **Upload PDF** - Drag and drop or browse to upload
2. **Classify** - AI analyzes each page
3. **View Results**:
   - Document preview
   - Summary statistics
   - Page-by-page breakdown
   - Confidence scores
   - Classification reasoning
4. **Export** - Download results as JSON

## Service Startup Sequence

1. Container starts and sources `env.sh`
2. Backend (FastAPI) starts on port 8004
3. Health check waits for backend to be ready
4. Frontend (Streamlit) starts on port 8501
5. Frontend connects to backend via localhost

## Troubleshooting

### Container not starting

Check logs:
```bash
./run.sh logs
```

### Backend not responding

Check backend logs:
```bash
./run.sh backend-logs
```

Verify API key is set:
```bash
docker exec document-classification env | grep GOOGLE_API_KEY
```

### Frontend can't connect to backend

Since both services are in the same container, they communicate via `localhost`.
Check that backend is running:
```bash
curl http://localhost:8004/
```

### Port conflicts

If ports 8004 or 8503 are in use, modify the docker run command:
```bash
docker run -d \
  --name document-classification \
  -p 9004:8004 \
  -p 9503:8501 \
  ...
```

## Development

### Local testing without Docker

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Source environment:
```bash
source env.sh
```

3. Start backend:
```bash
cd backend
python main.py &
```

4. Start frontend:
```bash
cd frontend
streamlit run app.py
```

## Document Types Supported

The AI can identify various document types including:
- Government IDs (Aadhaar, PAN, Passport, Driver's License, Voter ID)
- Financial Documents (Bank Statements, Salary Slips, Invoices)
- Legal Documents (Agreements, Contracts)
- Educational Certificates
- Medical Reports
- Utility Bills
- And more...

## Performance

- **Classification Time**: ~30-60 seconds per document
- **Supported PDF Size**: Up to 10MB recommended
- **Pages**: Handles multi-page documents
- **Accuracy**: High confidence (>80%) for standard documents

## Security Notes

- API keys should be kept secure
- Don't commit `env.sh` with real credentials
- Use environment-specific key management in production
- Consider implementing authentication for production deployments

## License

Part of the ai_project_25 repository.
