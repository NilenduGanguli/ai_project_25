# Document Extraction Service

A combined frontend and backend service for AI-powered document extraction with schema management. Both services run in a single container with MongoDB for data persistence.

## Features

- 🚀 **Single Container Deployment** - Backend and frontend in one container
- 📄 **Document Upload & Processing** - Schema generation and data extraction
- 🤖 **AI-Powered** - Uses Gemini 2.5 Flash for classification and extraction
- 📊 **Schema Management** - Create, modify, approve, and delete schemas
- 🗄️ **MongoDB Integration** - Persistent storage for schemas
- 🎨 **Web UI** - Beautiful Streamlit interface with multiple pages
- 🔌 **REST API** - FastAPI backend for programmatic access

## Architecture

```
┌──────────────────────────────────────────────────┐
│  Document Extraction Container                   │
│                                                   │
│  ┌──────────────┐  ┌──────────────┐             │
│  │   Backend    │  │   Frontend   │             │
│  │   FastAPI    │  │  Streamlit   │             │
│  │   Port 8005  │  │  Port 8501   │             │
│  └──────┬───────┘  └──────────────┘             │
│         │                                         │
│         └──────────────localhost                 │
└─────────────────────┬───────────────────────────┘
                      │
              ┌───────┴────────┐
              │    MongoDB     │
              │   Container    │
              │   Port 27017   │
              └────────────────┘
```

## Prerequisites

- Docker and Docker Compose
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

- **Frontend UI**: http://localhost:8504
- **Backend API**: http://localhost:8005
- **API Docs**: http://localhost:8005/docs
- **MongoDB**: mongodb://localhost:27018

## Management Commands

```bash
./run.sh build          # Build Docker images
./run.sh up             # Start all services
./run.sh down           # Stop and remove all services
./run.sh restart        # Restart all services
./run.sh logs           # View all logs
./run.sh backend-logs   # View backend logs only
./run.sh frontend-logs  # View frontend logs only
./run.sh mongo-logs     # View MongoDB logs
./run.sh status         # Check all services status
```

## Using Docker Compose

```bash
# Set environment variable
export GOOGLE_API_KEY="your_api_key_here"

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

## Environment Variables

All environment variables are managed in `env.sh`:

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Backend API port | 8005 |
| `FRONTEND_PORT` | Frontend UI port | 8501 |
| `MONGO_URI` | MongoDB connection URI | mongodb://mongodb:27017 |
| `MONGO_DB_NAME` | MongoDB database name | document_extraction_db |
| `GOOGLE_API_KEY` | Google Gemini API key | Required |
| `MIN_CLASSIFICATION_CONFIDENCE` | Min confidence threshold | 0.7 |
| `LANGSMITH_TRACING` | Enable LangSmith tracing | false |
| `LANGSMITH_ENDPOINT` | LangSmith endpoint | - |
| `LANGSMITH_API_KEY` | LangSmith API key | - |
| `LANGSMITH_PROJECT` | LangSmith project name | - |

## API Endpoints

### Backend API (Port 8005)

#### Health Check
```bash
GET /
```

#### Upload & Extract Documents
```bash
POST /extract
Content-Type: multipart/form-data
Body: document[] (PDF/JPEG/PNG)
```

Response scenarios:
- Schema generated (201)
- Schema pending review (202)
- Data extracted (200)

#### Get All Schemas
```bash
GET /schemas
```

#### Approve Schema
```bash
PUT /schemas/{schema_id}/approve
```

#### Modify Schema
```bash
PUT /schemas/{schema_id}/modify
Body: { modifications, change_description }
```

#### Delete Schema
```bash
DELETE /schemas/{schema_id}
```

## Frontend Features

### 1. Upload Documents Page
- Drag and drop PDF/JPEG/PNG files
- Document preview
- Schema generation for new document types
- Automatic data extraction for existing schemas
- View extracted data with document preview side-by-side

### 2. View All Schemas Page
- List all schemas with filtering and sorting
- Status indicators (Active, In Review, Deprecated)
- Schema details with field information
- Quick actions: Approve, Modify, Delete

### 3. Modify Schemas Page
- Add new fields
- Update existing fields
- Remove fields
- Delete entire schema
- Change tracking and versioning

### 4. Extract & View Page
- Upload documents for extraction
- View results alongside document
- Download results as JSON
- Support for multiple document types

## Service Startup Sequence

1. MongoDB container starts and initializes
2. Health check waits for MongoDB to be ready
3. Application container starts and sources `env.sh`
4. Backend (FastAPI) starts on port 8005
5. Health check waits for backend to be ready
6. Frontend (Streamlit) starts on port 8501
7. Frontend connects to backend via localhost

## Document Types Supported

The system can classify and extract data from various document types:
- Government IDs (Passport, Aadhaar, PAN Card, Driver's License, etc.)
- Financial Documents
- Educational Certificates
- Medical Records
- And more...

## Schema Management

### Schema Lifecycle
1. **Generation**: Upload document → AI generates schema
2. **Review**: Schema created with "In Review" status
3. **Modification**: Edit fields, add/remove properties
4. **Approval**: Activate schema for production use
5. **Deprecation**: Old versions archived when new version approved
6. **Deletion**: Remove unused schemas

### Schema Versioning
- Automatic version incrementing
- Track changes with descriptions
- Multiple versions per document type
- Only latest version can be modified

## Troubleshooting

### MongoDB not starting

Check logs:
```bash
./run.sh mongo-logs
```

Verify MongoDB health:
```bash
docker exec document-extraction-mongodb mongosh --eval "db.adminCommand('ping')"
```

### Backend not responding

Check backend logs:
```bash
./run.sh backend-logs
```

Verify API key is set:
```bash
docker exec document-extraction env | grep GOOGLE_API_KEY
```

### Frontend can't connect to backend

Since both services are in the same container, they communicate via `localhost`.
Check that backend is running:
```bash
curl http://localhost:8005/
```

### Port conflicts

If ports are in use, modify `docker-compose.yml`:
```yaml
ports:
  - "9005:8005"  # Backend
  - "9504:8501"  # Frontend
  - "37018:27017"  # MongoDB
```

## Development

### Local testing without Docker

1. Start MongoDB:
```bash
docker run -d -p 27017:27017 --name mongodb mongo:7.0
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Source environment:
```bash
source env.sh
export MONGO_URI="mongodb://localhost:27017"
```

4. Start backend:
```bash
cd backend
python main.py &
```

5. Start frontend:
```bash
cd frontend
streamlit run app.py
```

## Performance

- **Classification Time**: ~30-60 seconds per document
- **Extraction Time**: ~20-40 seconds per document
- **Supported File Size**: Up to 10MB recommended
- **Concurrent Requests**: Handled by FastAPI async
- **Database**: MongoDB for fast schema queries

## Security Notes

- API keys should be kept secure
- Don't commit `env.sh` with real credentials
- Use environment-specific key management in production
- Consider implementing authentication for production
- MongoDB should use authentication in production

## License

Part of the ai_project_25 repository.
