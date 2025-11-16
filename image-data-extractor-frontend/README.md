# Image Data Extractor - Frontend

A modern, intuitive Streamlit-based frontend for the Document Extraction System. This frontend provides a user-friendly interface for document upload, schema management, and data extraction visualization.

## Features

### 📤 Document Upload & Schema Generation
- Upload multiple documents (PDF, JPEG, PNG)
- Automatic document type classification
- Real-time schema generation for new document types
- Visual document preview

### 📚 Schema Management
- View all schemas with filtering and sorting options
- Beautiful card-based layout with status badges
- Detailed schema field inspection
- Real-time statistics dashboard

### ✏️ Schema Modification
- Add new fields to existing schemas
- Update field properties (type, description, required, example)
- Remove fields from schemas
- Change tracking with descriptions

### 🔍 Data Extraction & Viewing
- Extract data using active schemas
- Side-by-side view of document and extracted data
- Download extracted data as JSON
- Extraction metadata and confidence scores

## Quick Start

### Prerequisites
- Python 3.11+
- Backend API running (image-data-extractor service)
- MongoDB instance (if using docker-compose)

### Local Development

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure API endpoint:**
Edit `app.py` and set the API_BASE_URL:
```python
API_BASE_URL = "http://localhost:8005"
```

Or set environment variable:
```bash
export API_BASE_URL=http://localhost:8005
```

3. **Run the application:**
```bash
streamlit run app.py
```

The frontend will be available at `http://localhost:8501`

### Docker Deployment

1. **Create .env file:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

2. **Build and run with docker-compose:**
```bash
# Build the frontend image
docker-compose build frontend

# Start all services (frontend, backend, MongoDB)
docker-compose up -d

# Or start only frontend (if backend is running separately)
docker-compose up -d frontend
```

3. **Access the application:**
- Frontend: http://localhost:8501
- Backend API: http://localhost:8005
- MongoDB: localhost:27017

### Docker Commands

```bash
# View logs
docker-compose logs -f frontend

# Stop services
docker-compose down

# Rebuild after changes
docker-compose up -d --build frontend

# Remove all containers and volumes
docker-compose down -v
```

## Application Structure

```
image-data-extractor-frontend/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Multi-service orchestration
├── .streamlit/
│   └── config.toml            # Streamlit configuration
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## User Guide

### 1. Upload Documents for Schema Generation

Navigate to "📤 Upload Documents" page:

1. Upload one or more documents (PDF/JPEG/PNG)
2. Review uploaded documents in the preview pane
3. Click "Process Documents" button
4. System will:
   - Classify document type automatically
   - Generate schema if none exists
   - Extract data if schema is active
   - Notify if schema is pending review

**Possible Outcomes:**
- ✅ **Schema Generated**: New schema created, needs approval
- ⏳ **Pending Review**: Schema already exists for this type
- ✅ **Data Extracted**: Active schema found, data extracted

### 2. View All Schemas

Navigate to "📚 View All Schemas" page:

**Features:**
- Dashboard with schema statistics (Total, Active, Pending, Deprecated)
- Filter by status and document type
- Sort by date, type, or version
- Expandable schema cards showing:
  - Schema metadata (ID, type, country, version)
  - All fields with types and descriptions
  - Quick actions (Approve/Modify)

**Quick Actions:**
- Click "Approve" for schemas in review status
- Click "Modify" to edit active/review schemas

### 3. Modify Schemas

Navigate to "✏️ Modify Schemas" page:

**Modification Types:**

**Add New Field:**
1. Select schema to modify
2. Choose "Add New Field"
3. Enter field details:
   - Field name
   - Type (string, integer, boolean, date, number)
   - Description
   - Required flag
   - Example value
4. Add change description
5. Submit modifications

**Update Existing Field:**
1. Select schema and field to update
2. View current values
3. Modify properties as needed
4. Submit with description

**Remove Field:**
1. Select schema and field to remove
2. Review field details
3. Confirm removal
4. Submit with description

**Note:** Modified schemas are saved as new versions in "In Review" status.

### 4. Extract & View Results

Navigate to "🔍 Extract & View" page:

1. Upload document(s) for extraction
2. Click "Extract Data"
3. View results:
   - **Left panel**: Original document(s)
   - **Right panel**: Extracted data and metadata
4. Download results as JSON

**Metadata includes:**
- Document type and country
- Classification confidence
- Schema version used

## API Integration

The frontend communicates with the backend API at these endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Health check |
| `/extract` | POST | Upload documents & extract data |
| `/schemas` | GET | Get all schemas |
| `/schemas/{id}/approve` | PUT | Approve schema |
| `/schemas/{id}/modify` | PUT | Modify schema |

## Configuration

### Streamlit Settings

Edit `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#667eea"        # Main accent color
backgroundColor = "#ffffff"     # Background
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"

[server]
maxUploadSize = 200            # Max file size in MB
```

### API Configuration

Set API endpoint in `app.py` or via environment variable:

```python
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8005")
```

## Styling & Customization

The frontend uses custom CSS for enhanced visuals:

- **Gradient headers**: Purple gradient for main headers
- **Status badges**: Color-coded schema status indicators
- **Metric cards**: Gradient cards for statistics
- **Field rows**: Styled field display with left border
- **Extraction results**: Highlighted result boxes

To customize colors, edit the `<style>` block in `app.py`.

## Troubleshooting

### Cannot Connect to API

**Error:** "Cannot connect to API server"

**Solutions:**
1. Check if backend is running: `curl http://localhost:8005/`
2. Verify API_BASE_URL in app.py
3. Check network connectivity (especially in Docker)
4. Review backend logs: `docker logs image-data-extractor-api`

### Upload Failures

**Error:** Upload fails or times out

**Solutions:**
1. Check file size (max 200MB by default)
2. Verify file format (PDF, JPEG, PNG only)
3. Check backend logs for processing errors
4. Increase timeout in docker-compose.yml

### Schema Not Appearing

**Error:** Schemas not loading

**Solutions:**
1. Verify MongoDB connection
2. Check if schemas exist in database
3. Review API response in browser console
4. Restart frontend: `docker-compose restart frontend`

## Development

### Adding New Features

1. **New Page:**
   - Create a new function `page_your_feature()`
   - Add to sidebar navigation
   - Add routing in `main()`

2. **New API Call:**
   - Add function in "Helper Functions" section
   - Handle errors appropriately
   - Update API Integration section in README

3. **Custom Styling:**
   - Add CSS in the `st.markdown()` style block
   - Use consistent class naming
   - Test on different screen sizes

### Code Structure

```python
# 1. Imports & Configuration
# 2. Custom CSS Styling
# 3. Helper Functions
# 4. Page Functions
# 5. Main App Logic
```

## Performance Optimization

- **Caching**: Streamlit caching for API calls (future enhancement)
- **Lazy Loading**: Schemas loaded on demand
- **Pagination**: Consider for large schema lists
- **Image Optimization**: Resize large images before display

## Security Considerations

- API endpoint should use HTTPS in production
- File upload validation on both frontend and backend
- CORS configuration in backend
- Environment variables for sensitive data
- Regular security updates for dependencies

## Browser Compatibility

Tested and supported:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

When contributing:
1. Follow Python PEP 8 style guide
2. Add docstrings to functions
3. Update README for new features
4. Test all user flows
5. Ensure Docker build succeeds

## License

Same as parent project.

## Support

For issues:
1. Check backend logs
2. Review Streamlit logs
3. Verify API connectivity
4. Check MongoDB connection
5. Review browser console for errors

---

**Built with ❤️ using Streamlit**
