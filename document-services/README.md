# Unified Document Services

A combined document classification and extraction service with schema management capabilities.

## Features

### 📋 PDF Document Classification
- Page-by-page classification of multi-page PDFs
- Identifies document types (passport, driver's license, utility bill, etc.)
- Confidence scoring and reasoning for each classification
- Support for mixed document PDFs

### 📊 Document Data Extraction
- Automated schema generation from documents
- Schema-based structured data extraction
- Version-controlled schema management
- Support for multiple document types and countries

### ⚙️ Schema Management
- View all schemas with filtering
- Approve schemas for activation
- Modify existing schemas with version control
- Delete deprecated schemas

## Architecture

The document-services module combines two separate services while preserving their original interfaces:

### Services

1. **Document Classification** (from doc-classify)
   - Classifies PDF documents page-by-page using Gemini AI
   - FastAPI backend on port 8000
   - Streamlit UI on port 8502
   - Original doc-classify functionality
   
2. **Document Extraction** (from document-extraction)
   - Extracts structured data using schema-based approach
   - FastAPI backend on port 8001
   - Streamlit UI on port 8501
   - Original document-extraction interface
   - PostgreSQL database for schema storage

3. **Landing Page**
   - Simple HTML page on port 8080
   - Navigate to either Classification or Extraction UI

### Service Ports

| Port | Service | Description |
|------|---------|-------------|
| 8080 | Landing Page | HTML page to choose service |
| 8000 | Classification API | FastAPI backend for classification |
| 8001 | Extraction API | FastAPI backend for extraction |
| 8502 | Classification UI | Streamlit UI for PDF classification |
| 8501 | Extraction UI | Streamlit UI for document extraction |
| 5434 | PostgreSQL | Database for schema storage |

### Access Points

**Start Here:**
- **Landing Page**: http://localhost:8080
  - Simple HTML page with links to both UIs
  - Choose between Classification or Extraction

**Classification Service:**
- **Classification UI**: http://localhost:8502
  - Upload PDFs for page-by-page classification
  - View confidence scores and reasoning
  - Original doc-classify Streamlit interface
- **Classification API Docs**: http://localhost:8000/docs
  - Swagger UI for API testing

**Extraction Service:**
- **Extraction UI**: http://localhost:8501
  - Upload documents for data extraction
  - Manage schemas (approve, modify, delete)
  - Original document-extraction Streamlit interface
- **Extraction API Docs**: http://localhost:8001/docs
  - Swagger UI for API testing

### Navigation

Both Streamlit UIs include:
- **🏠 Home** button (top right) → Returns to landing page
- **Cross-service navigation** → Links to the other service UI

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Google API Key (for Gemini LLM)

### 1. Setup Environment

Before running the service, you need to set your Google API key in the `env.sh` file:

```bash
# Edit env.sh and add your Google API key
nano env.sh

# Update this line:
export GOOGLE_API_KEY="your_actual_api_key_here"
```

### 2. Start Services

Using the management script (recommended):

```bash
# Build and start containers
./run.sh build
./run.sh up

# Check status
./run.sh status

# View logs
./run.sh logs
```

Or using docker-compose directly:

```bash
# Set your API key first
export GOOGLE_API_KEY="your_api_key_here"

# Build and start containers
docker-compose up -d

# View logs
docker-compose logs -f
```

### 3. Access Services

- **Frontend UI**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5434

### 4. Stop Services

Using the management script:

```bash
./run.sh down

# To remove volumes (database data):
docker-compose down -v
```

Or using docker-compose directly:

```bash
docker-compose down

# To remove volumes (database data):
docker-compose down -v
```

## Management Script

The `run.sh` script provides convenient commands for managing the service:

```bash
./run.sh build          # Build Docker images
./run.sh up             # Start all services
./run.sh down           # Stop and remove all services
./run.sh restart        # Restart all services
./run.sh logs           # Show all container logs
./run.sh backend-logs   # Show backend logs only
./run.sh frontend-logs  # Show frontend logs only
./run.sh db-logs        # Show PostgreSQL logs
./run.sh status         # Show container status and test endpoints
```

## API Endpoints

### Classification
- `POST /classify-pdf` - Classify pages in a PDF document

### Extraction
- `POST /extract` - Extract structured data from documents

### Schema Management
- `GET /schemas` - Get all schemas
- `PUT /schemas/{schema_id}/approve` - Approve a schema
- `PUT /schemas/{schema_id}/modify` - Modify a schema
- `DELETE /schemas/{schema_id}` - Delete a schema

### Health
- `GET /` - Health check and service info

## Database Schema

### document_schemas Table

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| document_type | VARCHAR(100) | Document type (e.g., "us_passport") |
| country | VARCHAR(2) | ISO country code |
| document_schema | JSONB | Schema definition (JSON) |
| status | ENUM | Status: active, in_review, deprecated |
| created_at | TIMESTAMP WITH TIME ZONE | Creation timestamp |
| updated_at | TIMESTAMP WITH TIME ZONE | Last update timestamp |
| version | INTEGER | Schema version number |

See `DATABASE_SCHEMA_SPECIFICATION.md` in the root directory for complete details.

## Development

### Local Development (without Docker)

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Setup database**:
```bash
# Start PostgreSQL
docker run -d \
  --name postgres \
  -e POSTGRES_DB=document_services \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5434:5432 \
  postgres:15-alpine
```

3. **Run backend**:
```bash
cd backend
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5434/document_services"
export GOOGLE_API_KEY="your_key_here"
python main.py
```

4. **Run frontend** (in another terminal):
```bash
cd frontend
export API_BASE_URL="http://localhost:8000"
streamlit run app.py
```

### Project Structure

```
document-services/
├── backend/
│   ├── main.py                 # Unified FastAPI application
│   └── src/
│       ├── db/                 # Database models and connection
│       ├── extractors/         # Document processing and extraction
│       ├── config/             # LLM and app configuration
│       ├── schemas/            # Pydantic models and classification
│       └── utils/              # Utility functions
├── frontend/
│   └── app.py                  # Unified Streamlit UI
├── docker-compose.yml          # Container orchestration
├── Dockerfile                  # Container definition
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Environment Variables

### Required
- `GOOGLE_API_KEY` - Google Gemini API key

### Optional
- `DATABASE_URL` - PostgreSQL connection URL (default: from docker-compose)
- `POSTGRES_DB` - Database name (default: document_services)
- `POSTGRES_USER` - Database user (default: postgres)
- `POSTGRES_PASSWORD` - Database password (default: postgres)
- `MIN_CLASSIFICATION_CONFIDENCE` - Minimum confidence for extraction (default: 0.7)
- `BACKEND_PORT` - Backend port (default: 8000)
- `FRONTEND_PORT` - Frontend port (default: 8501)

## Usage Examples

### 1. Classify a PDF Document

```python
import requests

with open("document.pdf", "rb") as f:
    files = {"file": f}
    response = requests.post("http://localhost:8000/classify-pdf", files=files)
    
result = response.json()
for page in result["page_classifications"]:
    print(f"Page {page['page']}: {page['document_type']} ({page['confidence']:.2%})")
```

### 2. Extract Data from Documents

```python
import requests

with open("passport.jpg", "rb") as f:
    files = [("document", f)]
    response = requests.post("http://localhost:8000/extract", files=files)

if response.status_code == 200:
    result = response.json()
    print(f"Extracted data: {result['data']}")
    print(f"Schema used: {result['schema_used']['schema_id']}")
```

### 3. Approve a Schema

```python
import requests

schema_id = "550e8400-e29b-41d4-a716-446655440000"
response = requests.put(f"http://localhost:8000/schemas/{schema_id}/approve")

if response.status_code == 200:
    print("Schema approved successfully")
```

## Workflow

1. **Document Upload**: Upload documents via the frontend or API
2. **Classification**: System classifies document type and country
3. **Schema Check**: 
   - If active schema exists → Extract data immediately
   - If no schema exists → Generate new schema (awaits approval)
   - If schema in review → Notify user
4. **Schema Approval**: Admin reviews and approves generated schemas
5. **Data Extraction**: Extract structured data using approved schema
6. **Results**: View and download extracted data

## Monitoring

### Check Service Health

```bash
curl http://localhost:8000/
```

### View Logs

```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f document-services

# Database only
docker-compose logs -f postgres
```

### Database Access

```bash
# Connect to PostgreSQL
docker exec -it document-services-postgres psql -U postgres -d document_services

# List schemas
SELECT id, document_type, country, status, version FROM document_schemas;
```

## Troubleshooting

### Port Already in Use

```bash
# Change ports in docker-compose.yml
ports:
  - "8001:8000"  # Backend (change 8000 to 8001)
  - "8502:8501"  # Frontend (change 8501 to 8502)
```

### Database Connection Issues

```bash
# Reset database
docker-compose down -v
docker-compose up -d postgres
# Wait for postgres to be ready
docker-compose up -d document-services
```

### API Key Issues

```bash
# Verify API key is set
docker-compose exec document-services env | grep GOOGLE_API_KEY

# Update API key
# Edit env.sh file and restart
docker-compose restart document-services
```

## Comparison with Separate Modules

### Before (Separate Modules)
- `doc-classify`: Classification service (port 8004)
- `document-extraction`: Extraction service (port 8005)
- Two separate containers, two separate UIs
- Different endpoints and configurations

### After (Unified Module)
- Single `document-services` module (ports 8000, 8501)
- One container with both services
- Unified frontend with tabbed interface
- Shared database and configuration
- Easier deployment and maintenance

## Migration from Separate Modules

If migrating from separate `doc-classify` and `document-extraction` modules:

1. Export existing schemas from `document-extraction`:
```bash
docker exec document-extraction-postgres pg_dump -U postgres -d document_extraction -t document_schemas > schemas_backup.sql
```

2. Import into unified service:
```bash
docker exec -i document-services-postgres psql -U postgres -d document_services < schemas_backup.sql
```

## Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Review API docs: http://localhost:8000/docs
- See database schema spec: `DATABASE_SCHEMA_SPECIFICATION.md`

## License

Internal use only - AI Project 25
