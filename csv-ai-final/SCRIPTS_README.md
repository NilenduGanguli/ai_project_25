# CSV Analysis Agent - Build Scripts

This directory contains scripts to build and run the CSV Analysis Agent (Streamlit application).

## Available Scripts

### 1. `build-and-run.sh` (Recommended)
Comprehensive build and deployment script with validation and health checks.

**Features:**
- Environment validation
- Docker network setup
- Container cleanup
- Image building with progress
- Health monitoring
- Detailed service information

**Usage:**
```bash
chmod +x build-and-run.sh
./build-and-run.sh
```

### 2. `quick-start.sh`
Fast deployment script for development.

**Usage:**
```bash
chmod +x quick-start.sh
./quick-start.sh
```

## Service Information

- **Container Name:** `csv-analysis-streamlit`
- **Port:** `8501`
- **Network:** `citi-intern-network`
- **Health Check:** `http://localhost:8501/_stcore/health`

## Features

### 📊 CSV Analysis Tools

1. **Load CSV Tool**
   - Upload and load CSV files
   - View shape and columns
   - Get basic info

2. **Data Info Tool**
   - Dataset shape and structure
   - Column data types
   - Null counts and memory usage

3. **Describe Data Tool**
   - Numeric column statistics
   - Categorical column analysis
   - Top values and frequencies

4. **Create Visualization Tool**
   - Histogram
   - Scatter plot
   - Bar chart
   - Box plot
   - Heatmap

5. **Execute Pandas Code Tool**
   - Run custom pandas operations
   - Generate custom plots
   - Secure execution environment

## Using the Application

### 1. Upload CSV File
- Click "Upload CSV file" in the sidebar
- Select your CSV file
- File is loaded and ready for analysis

### 2. Chat with Your Data
Example prompts:
```
"Show me the first 10 rows"
"What are the column names and data types?"
"Create a histogram of the age column"
"Show correlation heatmap"
"Calculate the mean of all numeric columns"
"Plot sales by region as a bar chart"
```

### 3. View Generated Plots
- Plots are automatically displayed in the chat
- Saved to `/app/plots/` directory
- PNG format for easy sharing

## Environment Variables

Required in `.env`:
```properties
GOOGLE_API_KEY=your_api_key_here
```

Optional (LangSmith tracing):
```properties
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=your_langsmith_key
LANGSMITH_PROJECT=your_project_name
```

## Docker Commands

### View Logs
```bash
docker logs -f csv-analysis-streamlit
```

### Stop Service
```bash
docker stop csv-analysis-streamlit
```

### Restart Service
```bash
docker restart csv-analysis-streamlit
```

### Remove Container
```bash
docker rm -f csv-analysis-streamlit
```

### Rebuild Image
```bash
docker build -t csv-analysis-agent .
```

## Troubleshooting

### Service Not Starting
1. Check environment file exists: `ls -la .env`
2. Verify API key is set: `grep GOOGLE_API_KEY .env`
3. Check logs: `docker logs csv-analysis-streamlit`

### Port Already in Use
```bash
# Find process using port 8501
lsof -i :8501

# Kill the process
kill -9 <PID>

# Or change PORT in docker-compose.yml
```

### Health Check Failing
```bash
# Check service status
docker ps | grep csv-analysis-streamlit

# View detailed logs
docker logs --tail 100 csv-analysis-streamlit

# Test health endpoint
curl http://localhost:8501/_stcore/health
```

### Network Issues
```bash
# Verify network exists
docker network inspect citi-intern-network

# Recreate network if needed
docker network rm citi-intern-network
docker network create citi-intern-network
```

### Streamlit Issues

**White screen or loading forever:**
```bash
# Clear browser cache
# Check logs for errors
docker logs csv-analysis-streamlit

# Restart container
docker restart csv-analysis-streamlit
```

**File upload not working:**
```bash
# Check permissions
docker exec csv-analysis-streamlit ls -la /app/temp

# Verify volume mounts (if using)
```

## Development Tips

1. **Fast Iteration:** Use `quick-start.sh` for quick rebuilds during development
2. **Production Deploy:** Use `build-and-run.sh` for thorough validation
3. **Monitor Logs:** Keep logs open during testing: `docker logs -f csv-analysis-streamlit`
4. **Browser DevTools:** Use browser console to debug Streamlit issues

## Security Features

- **Non-root user:** App runs as `appuser` with limited permissions
- **Secure pandas execution:** Blocks dangerous operations (eval, exec, os commands)
- **File isolation:** Temporary files stored in app-specific directories
- **Network isolation:** Runs in dedicated Docker network

## Tool Examples

### Basic Analysis
```
User: "Load the sales.csv file"
Agent: Uses load_csv_tool → Shows shape and columns

User: "Describe the data"
Agent: Uses describe_data_tool → Shows statistics
```

### Visualizations
```
User: "Create a histogram of prices"
Agent: Uses create_visualization_tool → Generates plot

User: "Show correlation heatmap"
Agent: Uses create_visualization_tool → Generates heatmap
```

### Custom Analysis
```
User: "Show the top 5 products by revenue"
Agent: Uses execute_pandas_code_tool → Runs pandas code

User: "Calculate average sales per month"
Agent: Uses execute_pandas_code_tool → Computes result
```

## Architecture

```
┌─────────────────────────────────────────┐
│         Streamlit UI (Port 8501)        │
│  - File upload                          │
│  - Chat interface                       │
│  - Plot display                         │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│    LangChain Agent (Gemini 2.5 Flash)   │
│  - Natural language understanding       │
│  - Tool selection and orchestration     │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│             Tool Suite                   │
│  - load_csv_tool                        │
│  - get_data_info_tool                   │
│  - describe_data_tool                   │
│  - create_visualization_tool            │
│  - execute_pandas_code_tool             │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│      CSV Analyzer & DataFrame           │
│  - In-memory data storage               │
│  - Pandas operations                    │
│  - Matplotlib plotting                  │
└─────────────────────────────────────────┘
```

## Integration Notes

This service runs independently but can be part of a larger document processing pipeline:
- Upload CSV exports from other services
- Analyze extracted data from image-data-extractor
- Process results from analyzer or sentiment services

All services share the `citi-intern-network` for potential future integrations.
