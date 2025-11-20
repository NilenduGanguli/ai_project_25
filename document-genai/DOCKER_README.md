# Document GenAI - Docker-Only Execution

A comprehensive document processing system using Google GenerativeAI for classification, extraction, and schema generation. **This module is designed to run exclusively via Docker Compose.**

## 🚀 Quick Start (Docker Only)

### Prerequisites
- Docker and Docker Compose installed
- Google API Key for GenerativeAI access

### 1. Set Environment Variables
```bash
export GOOGLE_API_KEY="your-google-api-key-here"
```

### 2. Build and Run
```bash
# Clone and navigate to the directory
cd document-genai

# Build and start all services
./run.sh build
./run.sh up

# Check status
./run.sh status
```

### 3. Access Services
- **Landing Page**: http://localhost:8080
- **Classification API**: http://localhost:8000/docs
- **Extraction API**: http://localhost:8001/docs  
- **Classification UI**: http://localhost:8502
- **Extraction UI**: http://localhost:8501

## 📋 Architecture

### Container Services
- **Classification API** (Port 8000): PDF document classification
- **Extraction API** (Port 8001): Data extraction and schema management
- **Landing Page** (Port 8080): Static HTML interface
- **Classification UI** (Port 8502): Streamlit classification interface
- **Extraction UI** (Port 8501): Streamlit extraction interface

### Key Features
- **Google GenerativeAI Integration**: Direct API access without LangChain
- **SQLite Database**: Embedded database for schema management
- **Multi-Format Support**: PDF, JPEG, PNG document processing
- **Dynamic Schema Generation**: AI-powered schema creation
- **Docker-First Design**: Optimized for container deployment

## 🔧 Management Commands

### Basic Operations
```bash
# Build containers
./run.sh build

# Start all services
./run.sh up

# Stop services
./run.sh down

# Restart services
./run.sh restart

# Check status
./run.sh status
```

### Monitoring
```bash
# View all logs
./run.sh logs

# View backend API logs only
./run.sh backend-logs

# View frontend UI logs only
./run.sh frontend-logs

# Database information
./run.sh db-info
```

## 🧪 Testing

### Automated Docker Test
```bash
# Run comprehensive test suite
./test_docker.sh
```

### Manual API Testing
```bash
# Test classification endpoint
curl -X POST "http://localhost:8000/classify" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample.pdf"

# Test extraction endpoint
curl -X POST "http://localhost:8001/extract" \
  -H "Content-Type: multipart/form-data" \
  -F "front_image=@document.jpg" \
  -F "schema_id=1"

# Get available schemas
curl http://localhost:8001/schemas
```

## 🗄️ Database Management

### Schema Operations
- **View Schemas**: http://localhost:8001/schemas
- **Download Schemas**: http://localhost:8001/download-schemas
- **Schema Generation**: Automatic via AI analysis

### Data Persistence
- SQLite database stored in Docker volume `sqlite_data`
- Schemas directory mounted read-only from `./schemas`

## 🔐 Environment Configuration

### Required Variables
```bash
GOOGLE_API_KEY=your_google_api_key_here
```

### Optional Variables
```bash
MIN_CLASSIFICATION_CONFIDENCE=0.7  # Default confidence threshold
DATABASE_PATH=/app/data/document_services.db  # Database location
```

## 🐛 Troubleshooting

### Container Issues
```bash
# Check container status
docker-compose ps

# View detailed logs
docker-compose logs -f

# Restart specific service
docker-compose restart document-genai
```

### API Connection Issues
```bash
# Test container connectivity
docker exec -it document-genai curl http://localhost:8000/

# Check port bindings
docker port document-genai
```

### Database Issues
```bash
# Access container shell
docker exec -it document-genai bash

# Check database files
ls -la /app/data/

# View schemas
curl http://localhost:8001/schemas
```

## 📁 Project Structure

```
document-genai/
├── backend/                 # FastAPI applications
│   ├── classification_main.py
│   ├── extraction_main.py
│   └── src/
│       ├── config/         # Google GenAI configuration
│       ├── extractors/     # Document processing
│       ├── db/             # Database models
│       ├── schemas/        # Response models
│       └── utils/          # Utility functions
├── frontend/               # Streamlit UIs
│   ├── classification_app.py
│   ├── extraction_app.py
│   └── index.html
├── schemas/                # Predefined schemas
├── docker-compose.yml      # Container orchestration
├── Dockerfile             # Container definition
├── entrypoint.sh          # Container startup script
├── run.sh                 # Management commands
├── test_docker.sh         # Docker test suite
└── requirements.txt       # Python dependencies
```

## 🔄 Migration from document-services-unified

This module replaces LangChain with direct Google GenerativeAI integration:

- ✅ **Removed**: LangChain dependencies
- ✅ **Added**: Direct `google-generativeai` integration  
- ✅ **Maintained**: All API endpoints and functionality
- ✅ **Improved**: Simplified dependencies and better performance

## 📞 Support

For issues or questions:
1. Check container logs: `./run.sh logs`
2. Run test suite: `./test_docker.sh`
3. Verify API key configuration
4. Review Docker Compose status

---

**Note**: This module is designed exclusively for Docker execution. All commands and instructions assume Docker Compose usage.