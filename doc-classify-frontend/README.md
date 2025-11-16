# PDF Document Classifier Frontend

A Streamlit-based web interface for the PDF Document Classifier service.

## Features

- 📄 Upload PDF documents (single or multi-page)
- 🤖 AI-powered page-by-page document classification
- 📊 Visual classification results with confidence scores
- 💡 Reasoning for each classification decision
- 📥 Export results as JSON
- 🎨 Beautiful, responsive UI

## Prerequisites

- Docker and Docker Compose
- Doc-classify backend service running on port 8004

## Quick Start

### Using Docker

1. Build and start the frontend:
```bash
chmod +x run.sh
./run.sh build
./run.sh up
```

2. Access the application at: http://localhost:8502

### Using Docker Compose

```bash
docker-compose up -d
```

## Usage

1. Upload a PDF document using the file uploader
2. Click "Classify Document" button
3. View page-by-page classification results
4. Download results as JSON if needed

## API Configuration

The frontend connects to the backend at `http://host.docker.internal:8004` by default.

To change the backend URL, update the `API_BASE_URL` in `app.py` or set the environment variable:

```bash
docker run -d \
  --name doc-classify-frontend \
  -p 8502:8501 \
  -e API_BASE_URL=http://your-backend:8004 \
  doc-classify-frontend:latest
```

## Management Commands

```bash
./run.sh build    # Build Docker image
./run.sh up       # Start container
./run.sh down     # Stop and remove container
./run.sh restart  # Restart container
./run.sh logs     # View logs
./run.sh status   # Check status
```

## Features Explained

### Document Classification
- Analyzes each page of the PDF
- Identifies document types (Aadhaar, PAN, Passport, etc.)
- Provides confidence scores and reasoning
- Handles mixed document PDFs

### Results Display
- Document preview with embedded PDF viewer
- Summary statistics (total pages, document types, avg confidence)
- Page-by-page breakdown with visual indicators
- Confidence level color coding (green/yellow/red)

### Export Options
- Download classification results as JSON
- View raw JSON data in expandable section

## Architecture

```
Frontend (Streamlit) → Backend (FastAPI) → Gemini AI
Port 8502           → Port 8004
```

## Troubleshooting

### Frontend can't connect to backend
- Ensure backend is running: `curl http://localhost:8004/`
- Check Docker networking: Use `host.docker.internal` for Docker containers
- Verify ports are not blocked by firewall

### Container not starting
- Check logs: `./run.sh logs`
- Verify port 8502 is not in use: `lsof -i :8502`
- Rebuild image: `./run.sh down && ./run.sh build && ./run.sh up`

## Development

To run locally without Docker:

```bash
pip install -r requirements.txt
export API_BASE_URL=http://localhost:8004
streamlit run app.py
```

## License

Part of the ai_project_25 repository.
