# Image Data Extractor Service - Build Scripts

This directory contains scripts to easily build and run the Image Data Extractor service with MongoDB.

## Prerequisites

- Docker and Docker Compose installed
- Google API key for Gemini
- MongoDB connection (provided via Docker Compose)

## Quick Start

### Option 1: Quick Start (Recommended for first-time users)

```bash
chmod +x quick-start.sh
./quick-start.sh
```

This script will:
- Create the Docker network if needed
- Build and start all containers (app, MongoDB, Mongo Express)
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
- Build the Docker images
- Start all containers (app, MongoDB, Mongo Express)
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
   PORT=8005
   MONGODB_URL=mongodb://admin:password123@mongodb:27017/image_extractor?authSource=admin
   ```

## Service Information

Once running, the services will be available at:
- **API**: http://localhost:8005
- **Interactive API Docs**: http://localhost:8005/docs
- **ReDoc Documentation**: http://localhost:8005/redoc
- **Health Check**: http://localhost:8005/
- **MongoDB**: mongodb://localhost:27017
- **Mongo Express**: http://localhost:8081 (username: admin, password: admin123)

## Services Overview

### Application Service
Extracts structured data from documents (images/PDFs) using LLM-based schema generation and classification.

### MongoDB Service
Stores document schemas with version control and status management.

### Mongo Express
Web-based MongoDB admin interface for viewing and managing schemas.

## Useful Docker Commands

### View Logs
```bash
# Application logs
docker logs -f image_extractor_app

# MongoDB logs
docker logs -f image_extractor_mongodb

# Mongo Express logs
docker logs -f image_extractor_mongo_express
```

### Stop Services
```bash
docker-compose down
```

### Stop and Remove Data
```bash
docker-compose down -v
```

### Restart Services
```bash
docker-compose restart
```

### Rebuild and Restart
```bash
docker-compose up -d --build
```

### Check Container Status
```bash
docker ps | grep image_extractor
```

## Troubleshooting

### Container won't start
1. Check if ports are already in use:
   ```bash
   lsof -i :8005  # Application port
   lsof -i :27017 # MongoDB port
   lsof -i :8081  # Mongo Express port
   ```

2. View container logs:
   ```bash
   docker logs image_extractor_app
   docker logs image_extractor_mongodb
   ```

### API key issues
- Ensure `GOOGLE_API_KEY` is set correctly in `.env`
- Verify the API key is valid and has proper permissions

### MongoDB connection issues
- Verify MongoDB container is running: `docker ps | grep mongodb`
- Check MongoDB logs: `docker logs image_extractor_mongodb`
- Ensure `MONGODB_URL` in `.env` matches the docker-compose configuration

### Network issues
If containers can't connect to other services:
```bash
docker network inspect citi-intern-network
```

## Script Features

### build-and-run.sh Features:
- ✅ Pre-flight checks (Docker running, .env configured)
- ✅ Automatic network creation
- ✅ Multi-container cleanup
- ✅ Health monitoring for all services
- ✅ Colored output for better readability
- ✅ Detailed error messages
- ✅ Service information display

### quick-start.sh Features:
- ✅ Minimal configuration
- ✅ Fast startup
- ✅ Network auto-creation
- ✅ One-command deployment

## API Endpoints

### POST /extract
Extract data from documents using schema generation and classification.

**Request:**
- Content-Type: multipart/form-data
- Body: One or more document files (JPEG, PNG, PDF)

**Response:**
```json
{
  "status": "extracted",
  "data": { /* extracted fields */ },
  "classification": {
    "document_type": "passport",
    "country": "USA",
    "confidence": 0.95
  },
  "schema_used": {
    "document_type": "passport",
    "country": "USA",
    "version": 1
  }
}
```

### GET /schemas
Retrieve all document schemas.

**Response:**
```json
{
  "schemas": [...],
  "total_count": 10
}
```

### PUT /schemas/{schema_id}/approve
Approve a schema in review status.

### PUT /schemas/{schema_id}/modify
Modify an existing schema (creates new version).

### GET /
Health check endpoint.

## Database Structure

### DocumentSchema Collection
- `document_type`: Type of document (e.g., "passport", "license")
- `country`: Country code (e.g., "USA", "UK")
- `document_schema`: JSON schema definition
- `status`: ACTIVE | IN_REVIEW | DEPRECATED
- `version`: Schema version number
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

## Integration with Other Services

This service is part of the `citi-intern-network` Docker network and can communicate with:
- Analyzer Service (port 8001)
- Sentiment Service (port 8002)
- Summarizer Service (port 8003)
- Doc Classifier (port 8004)
- OCR Service (port 8006)
- CSV Analyzer (port 8501)
- UI Service (port 8500)

## MongoDB Access

### Via Mongo Express (Web UI)
1. Open http://localhost:8081
2. Login with: admin / admin123
3. Navigate to `image_extractor` database

### Via MongoDB Shell
```bash
docker exec -it image_extractor_mongodb mongosh -u admin -p password123 --authenticationDatabase admin
```

### Via Python Application
The application automatically connects using the MONGODB_URL from .env

## Support

For issues or questions:
1. Check the service logs
2. Verify environment configuration
3. Ensure all prerequisites are met
4. Check MongoDB connection
5. Review the main README.md in the project root
