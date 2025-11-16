# Quick Start Guide - Image Data Extractor Frontend

This guide will help you get the frontend up and running quickly.

## Option 1: Run Locally (Quickest for Development)

### Prerequisites
- Python 3.11+
- Backend API running at http://localhost:8005

### Steps

1. **Navigate to the frontend directory:**
```bash
cd image-data-extractor-frontend
```

2. **Install dependencies:**
```bash
./run.sh install
# OR manually:
pip3 install -r requirements.txt
```

3. **Start the frontend:**
```bash
./run.sh run
# OR manually:
streamlit run app.py
```

4. **Open your browser:**
```
http://localhost:8501
```

✅ **You're ready!** The frontend should now be connected to your backend API.

---

## Option 2: Run with Docker (Frontend Only)

### Prerequisites
- Docker installed
- Backend API running

### Steps

1. **Build the Docker image:**
```bash
cd image-data-extractor-frontend
./run.sh docker-build
```

2. **Run the container:**
```bash
# If backend is on localhost:
./run.sh docker-run

# If backend is on a different host:
API_BASE_URL=http://your-backend:8005 ./run.sh docker-run
```

3. **Access the frontend:**
```
http://localhost:8501
```

---

## Option 3: Run Complete Stack (Recommended for Testing)

This option runs frontend, backend, and MongoDB together.

### Prerequisites
- Docker and Docker Compose installed
- Google API Key for backend

### Steps

1. **Create environment file:**
```bash
cd image-data-extractor-frontend
cp .env.example .env
```

2. **Edit .env file:**
```bash
nano .env
# Add your Google API key:
GOOGLE_API_KEY=your_actual_google_api_key_here
```

3. **Start all services:**
```bash
./run.sh compose
```

4. **Wait for services to start (30-60 seconds):**
```bash
# Check status:
./run.sh status

# View logs:
./run.sh logs
```

5. **Access the services:**
- Frontend: http://localhost:8501
- Backend API: http://localhost:8005
- MongoDB: localhost:27017

---

## Common Commands

### Using run.sh script:

```bash
# Install dependencies
./run.sh install

# Run locally
./run.sh run

# Build Docker image
./run.sh docker-build

# Run in Docker
./run.sh docker-run

# Run full stack
./run.sh compose

# Stop all services
./run.sh stop

# View logs
./run.sh logs

# Check status
./run.sh status

# Show help
./run.sh help
```

---

## Testing the Frontend

Once running, test these workflows:

### 1. Upload Document
- Go to "📤 Upload Documents"
- Upload a sample document (PDF/JPEG/PNG)
- Click "Process Documents"
- Should see classification result

### 2. View Schemas
- Go to "📚 View All Schemas"
- Should see dashboard with statistics
- Filter and sort schemas
- Expand schema cards to view details

### 3. Approve Schema
- Go to "📚 View All Schemas"
- Find a schema with "In Review" status
- Click "Approve" button
- Schema should change to "Active" status

### 4. Modify Schema
- Go to "✏️ Modify Schemas"
- Select a schema
- Add/update/remove fields
- Submit modifications

### 5. Extract Data
- Go to "🔍 Extract & View"
- Upload a document
- Click "Extract Data"
- View results side-by-side with document

---

## Troubleshooting

### "Cannot connect to API server"

**Problem:** Frontend can't reach backend

**Solutions:**
```bash
# Check if backend is running:
curl http://localhost:8005/

# If using Docker, check network:
docker network ls
docker network inspect image-data-extractor-frontend_extractor-network

# Check backend logs:
cd ../image-data-extractor
docker logs image-data-extractor-api
```

### Port already in use

**Problem:** Port 8501 already in use

**Solution:**
```bash
# Use different port:
STREAMLIT_PORT=8502 ./run.sh run

# Or find and kill the process:
lsof -ti:8501 | xargs kill -9
```

### Dependencies not installing

**Problem:** pip install fails

**Solutions:**
```bash
# Upgrade pip:
pip3 install --upgrade pip

# Use virtual environment:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Docker build fails

**Problem:** Docker build errors

**Solutions:**
```bash
# Clear Docker cache:
docker builder prune -a

# Rebuild without cache:
docker build --no-cache -t image-extractor-frontend .

# Check Docker daemon:
docker info
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `API_BASE_URL` | `http://localhost:8005` | Backend API endpoint |
| `STREAMLIT_PORT` | `8501` | Port for frontend |
| `GOOGLE_API_KEY` | - | Required for backend (compose mode) |
| `MONGODB_HOST` | `mongodb` | MongoDB host (compose mode) |
| `MONGODB_PORT` | `27017` | MongoDB port (compose mode) |

---

## Next Steps

1. **Customize UI:** Edit colors and styling in `app.py`
2. **Add features:** Extend page functions as needed
3. **Configure:** Adjust settings in `.streamlit/config.toml`
4. **Deploy:** Use docker-compose for production deployment

---

## Need Help?

1. Check logs: `./run.sh logs`
2. Check status: `./run.sh status`
3. View README.md for detailed documentation
4. Check backend logs if API issues persist

---

**🎉 Enjoy your Document Extraction System!**
