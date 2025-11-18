# Unified Document Services (MongoDB Version)

A combined document classification and extraction service with schema management capabilities using MongoDB.

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

The document-services-mongo module combines two separate services while preserving their original interfaces, using MongoDB instead of PostgreSQL.

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
   - MongoDB database for schema storage (instead of PostgreSQL)

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
| 27019 | MongoDB | Database for schema storage |

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
- **MongoDB**: localhost:27019

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

### document_schemas Collection (MongoDB)

MongoDB document structure using Beanie ODM:

| Field | Type | Description |
|-------|------|-------------|
| _id | ObjectId | Primary key (auto-generated by MongoDB) |
| document_type | String | Document type (e.g., "us_passport") |
| country | String | ISO country code (2 letters) |
| document_schema | Dict | Schema definition (JSON/Dict) |
| status | String (Enum) | Status: active, in_review, deprecated |
| created_at | DateTime | Creation timestamp (UTC) |
| updated_at | DateTime | Last update timestamp (UTC) |
| version | Integer | Schema version number |

**Indexes:**
- Compound index on: (document_type, country, status)

**Key Differences from PostgreSQL version:**
- Uses MongoDB ObjectId instead of UUID
- JSONB → Dict (native MongoDB document)
- Async operations using Beanie ODM
- No explicit table definition (collection-based)

See `DATABASE_SCHEMA_SPECIFICATION.md` in the root directory for PostgreSQL version details.

## Development

### Local Development (without Docker)

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Setup database**:
```bash
# Start MongoDB
docker run -d \
  --name mongodb \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=password123 \
  -p 27019:27017 \
  mongo:7.0
```

3. **Run backend**:
```bash
cd backend
export MONGODB_URL="mongodb://admin:password123@localhost:27019"
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
- `MONGODB_URL` - MongoDB connection URL (default: mongodb://admin:password123@mongodb:27017)
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
# Connect to MongoDB
docker exec -it document-services-mongodb mongosh -u admin -p password123

# Switch to database
use document_extraction

# List schemas
db.document_schemas.find().pretty()

# Count schemas by status
db.document_schemas.aggregate([
  { $group: { _id: "$status", count: { $sum: 1 } } }
])
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
docker-compose up -d mongodb
# Wait for mongodb to be ready
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

## Key Differences from PostgreSQL Version

### Database Layer
- **Primary Keys**: ObjectId (auto-generated) instead of UUID
- **ORM**: Beanie (MongoDB ODM) instead of SQLAlchemy
- **Queries**: Beanie async methods instead of SQL queries
- **Schema Storage**: Native MongoDB documents instead of JSONB columns

### Benefits of MongoDB Version
- **Flexible Schema**: Better suited for dynamic document schemas
- **Native JSON**: No need for JSONB serialization
- **Scalability**: Horizontal scaling with sharding
- **Performance**: Faster document-based queries

### API Compatibility
- All endpoints remain the same
- Request/response formats unchanged
- UI functionality preserved
- Same workflow and user experience

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

## Migration from PostgreSQL Version

If migrating from the PostgreSQL-based `document-services` module:

### Option 1: Export and Import (Manual)

1. **Export schemas from PostgreSQL**:
```bash
# Connect to PostgreSQL version
docker exec document-services-postgres psql -U admin -d document_services -c "\copy (SELECT row_to_json(t) FROM (SELECT * FROM document_schemas) t) TO STDOUT" > schemas_export.json
```

2. **Transform and import to MongoDB**:
```python
import json
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

# Connect to MongoDB
client = MongoClient('mongodb://admin:password123@localhost:27019')
db = client['document_extraction']

# Read PostgreSQL export
with open('schemas_export.json', 'r') as f:
    for line in f:
        schema = json.loads(line)
        # Transform UUID to ObjectId
        schema.pop('id')  # Remove UUID, MongoDB will create ObjectId
        # Insert into MongoDB
        db.document_schemas.insert_one(schema)
```

### Option 2: API-based Migration

Use the `/schemas` endpoint to export from PostgreSQL and `/register-schema` to import into MongoDB version.

## Comparison with PostgreSQL Version

| Feature | PostgreSQL Version | MongoDB Version |
|---------|-------------------|-----------------|
| Database | PostgreSQL 15 | MongoDB 7.0 |
| ORM/ODM | SQLAlchemy | Beanie |
| Primary Key | UUID | ObjectId |
| Schema Storage | JSONB column | Native document |
| Queries | SQL-based | Document-based |
| Port | 5434 | 27019 |
| API Endpoints | Same | Same |
| UI Functionality | Same | Same |

## Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Review API docs: http://localhost:8000/docs
- See database schema spec: `DATABASE_SCHEMA_SPECIFICATION.md`

## License

Internal use only - AI Project 25
