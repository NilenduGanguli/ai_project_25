# KYC Ops Document Service Hub - Comprehensive Guide

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Services Overview](#services-overview)
4. [Service Details](#service-details)
5. [Web UI Guide](#web-ui-guide)
6. [API Reference](#api-reference)
7. [Common Workflows](#common-workflows)
8. [Technical Implementation](#technical-implementation)

---

## System Overview

The KYC Ops Document Service Hub is a comprehensive AI-powered document processing platform designed for Know Your Customer (KYC) operations. It provides multiple specialized microservices for document analysis, classification, extraction, and processing.

### Key Capabilities

- **Document Classification**: Automatically identify document types across multiple pages
- **Data Extraction**: Extract structured data from documents using dynamic schemas
- **Document Analysis**: Query and analyze PDF documents using AI
- **Sentiment Analysis**: Analyze sentiment in PDF documents
- **Text Summarization**: Generate summaries of varying detail levels
- **CSV Analysis**: Interactive CSV data analysis with natural language queries
- **Member Search**: Search and trace extracted fields across member documents

### Technology Stack

- **Backend**: FastAPI (Python)
- **AI/LLM**: Google Gemini 2.5 Flash
- **Vector Store**: FAISS (Facebook AI Similarity Search)
- **Database**: MongoDB (for schema management)
- **UI Framework**: Streamlit
- **Document Processing**: LangChain, PyPDF2, pdf2image
- **Embeddings**: Google Generative AI Embeddings

---

## Architecture

### Microservices Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Web UI (Port 8500)                       │
│                    Streamlit Application                     │
└───────────────┬─────────────────────────────────────────────┘
                │
                │ HTTP/REST APIs
                │
┌───────────────┴─────────────────────────────────────────────┐
│                      Service Layer                           │
├──────────────┬──────────────┬──────────────┬────────────────┤
│  Analyzer    │  Classifier  │  Extractor   │   Sentiment    │
│  (Port 8001) │  (Port 8004) │  (Port 8005) │  (Port 8002)   │
├──────────────┼──────────────┼──────────────┼────────────────┤
│  Summarizer  │  CSV Agent   │              │                │
│  (Port 8003) │  (Port 8501) │              │                │
└──────────────┴──────────────┴──────────────┴────────────────┘
                │              │
                │              │
┌───────────────┴──────────────┴──────────────────────────────┐
│              Data & Storage Layer                            │
├──────────────────────────────────────────────────────────────┤
│  FAISS Vector Store  │  MongoDB  │  File Storage (uploads/) │
└──────────────────────────────────────────────────────────────┘
                │
                │
┌───────────────┴──────────────────────────────────────────────┐
│                    AI/LLM Layer                              │
├──────────────────────────────────────────────────────────────┤
│            Google Gemini 2.5 Flash API                       │
│       (Text Analysis, Vision, Structured Outputs)            │
└──────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Document Upload** → User uploads through Web UI
2. **Service Selection** → UI routes to appropriate microservice
3. **AI Processing** → Service uses Gemini LLM for analysis
4. **Data Storage** → Results stored in vector store/database
5. **Response** → Formatted results returned to UI
6. **Display** → Interactive visualization in Web UI

---

## Services Overview

| Service                       | Port | Primary Function                       | Analysis Modes     |
| ----------------------------- | ---- | -------------------------------------- | ------------------ |
| **Analyzer**            | 8001 | Query and analyze PDF documents        | Vector, Multimodal |
| **Document Classifier** | 8004 | Classify document types by page        | Vision-based       |
| **Document Extractor**  | 8005 | Extract structured data from documents | Schema-based       |
| **Sentiment Analyzer**  | 8002 | Analyze sentiment in PDFs              | Vector, Multimodal |
| **Summarizer**          | 8003 | Generate PDF summaries                 | Vector, Multimodal |
| **CSV Analyzer**        | 8501 | Interactive CSV data analysis          | Agent-based        |
| **Web UI**              | 8500 | Unified interface for all services     | -                  |

---

## Service Details

### 1. Analyzer Service (Ops Document Query Tool)

**Port**: 8001
**Purpose**: Analyze PDF documents and query their content using vector search or multimodal AI

#### Features

- **Vector Mode**: Uses text embeddings for semantic search
- **Multimodal Mode**: Uses vision capabilities to analyze PDFs directly
- **Vector Store Management**: Ingest documents for persistent querying
- **Custom Queries**: Ask specific questions about document content

#### Analysis Modes

**Vector Mode**:

- Extracts text from PDF
- Splits into chunks (10,000 chars with 1,000 overlap)
- Creates embeddings using Google's text-embedding-004
- Stores in FAISS vector store
- Retrieves relevant chunks based on query
- Uses LLM to generate answer from retrieved context

**Multimodal Mode**:

- Converts PDF to base64
- Sends entire PDF to Gemini Vision model
- Analyzes visual and textual content
- Generates comprehensive response

#### API Endpoints

**POST /analyze**

- Parameters: `file`, `search_query`, `mode` (vector/multimodal)
- Returns: Analysis response with retrieved vectors (vector mode)

**POST /vectorstore/ingest**

- Parameters: `file`
- Returns: Confirmation with unique filename
- Purpose: Add documents to persistent vector store

**POST /vectorstore/query**

- Parameters: `query`, `k` (number of results)
- Returns: Relevant document chunks with metadata
- Purpose: Query the vector store without file upload

#### Use Cases

1. **Federal Criminal Record Search**: "List if any criminal activity is there by the person mentioned"
2. **Document Summarization**: "Summarize the key points of this document"
3. **Information Extraction**: "What is the person's employment history?"
4. **Multi-Document Search**: Ingest multiple docs, query across all

---

### 2. Document Classifier

**Port**: 8004
**Purpose**: Automatically classify document types page by page

#### Features

- Multi-page classification
- Confidence scoring (0-1 scale)
- Document type detection (40+ types)
- Detailed reasoning for each classification
- Handles mixed document PDFs

#### Supported Document Types

- Identity Documents: Aadhar Card, PAN Card, Passport, Driver's License, Voter ID
- Financial: Bank Statement, Salary Slip, Insurance Document
- Legal: Agreement/Contract, Property Deed
- Academic: Educational Certificate
- Utility: Bills (electricity, water, gas)
- Government: Various government-issued IDs
- Medical: Reports and prescriptions
- And more...

#### Classification Process

1. PDF converted to base64
2. Sent to Gemini Vision model
3. Each page analyzed for:
   - Document title/header
   - Logos and watermarks
   - Layout and structure
   - Text patterns
   - Official seals
4. Returns structured classification per page

#### API Endpoint

**POST /classify-pdf**

- Parameters: `file` (PDF)
- Returns: Array of page classifications

Response Structure:

```json
{
  "page_classifications": [
    {
      "page": 1,
      "document_type": "Aadhaar Card",
      "confidence": 0.95,
      "reasoning": "Page contains Aadhaar card layout..."
    }
  ]
}
```

#### Use Cases

1. **Batch Processing**: Classify multiple documents in one PDF
2. **Document Organization**: Automatically categorize uploaded documents
3. **Quality Control**: Verify document types before processing
4. **Workflow Routing**: Route documents to appropriate handlers

---

### 3. Document Extraction Service

**Port**: 8005
**Purpose**: Extract structured data from documents using dynamic schemas

#### Features

- **Dynamic Schema Generation**: Auto-generates extraction schemas
- **Schema Versioning**: Tracks schema changes over time
- **Multi-Document Support**: Handles multiple document pages
- **Schema Modification**: Edit and improve schemas
- **Approval Workflow**: Review schemas before activation

#### Schema Lifecycle

```
┌──────────────┐
│  Upload Doc  │
└──────┬───────┘
       │
       ▼
┌──────────────┐     ┌────────────────┐
│  Classify    │────▶│ Existing       │
│  Document    │     │ Schema?        │
└──────┬───────┘     └────┬────┬──────┘
       │                  │    │
       │ NO               │YES │
       │                  │    │
       ▼                  │    ▼
┌──────────────┐         │  ┌──────────┐
│  Generate    │         │  │ Extract  │
│  Schema      │         │  │ Data     │
└──────┬───────┘         │  └────┬─────┘
       │                 │       │
       ▼                 │       ▼
┌──────────────┐         │  ┌──────────┐
│ IN_REVIEW    │         │  │ Return   │
│ Status       │         │  │ Results  │
└──────┬───────┘         │  └──────────┘
       │                 │
       ▼                 │
┌──────────────┐         │
│ Approve or   │         │
│ Modify       │         │
└──────┬───────┘         │
       │                 │
       ▼                 │
┌──────────────┐         │
│   ACTIVE     │─────────┘
│   Status     │
└──────────────┘
```

#### Schema Fields Example

```json
{
  "document_number": {
    "type": "string",
    "description": "The unique document number",
    "required": false,
    "example": "DOC123456",
    "pattern": "^[A-Z]{3}\\d{6}$"
  },
  "surname": {
    "type": "string",
    "description": "The surname of the holder",
    "required": false,
    "example": "SURNAME"
  },
  "date_of_birth": {
    "type": "string",
    "description": "Date of birth in DD/MM/YYYY format",
    "required": false,
    "example": "01/01/2000",
    "pattern": "^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/(\\d{4})$"
  },
  "photo_present": {
    "type": "boolean",
    "description": "Indicates if photo is visible",
    "required": false,
    "example": true
  }
}
```

#### API Endpoints

**POST /extract`**

- Extracts data or generates schema
- Supports PDF, JPEG, PNG
- Returns extracted data or schema for review

**GET /schemas**

- Lists all schemas in the system
- Shows document type, country, version, status

**PUT /schemas/{schema_id}/approve**

- Activates a schema in review
- Deprecates previous active version

**PUT /schemas/{schema_id}/modify**

- Proposes modifications to schema
- Tracks changes with versioning
- Creates new IN_REVIEW version

#### Status Types

- **ACTIVE**: Currently used for extraction
- **IN_REVIEW**: Awaiting approval
- **DEPRECATED**: Old version, replaced by newer

#### Use Cases

1. **KYC Data Extraction**: Extract fields from identity documents
2. **Form Processing**: Parse structured forms
3. **Invoice Processing**: Extract invoice details
4. **Certificate Parsing**: Extract data from certificates

---

### 4. Sentiment Analysis Service

**Port**: 8002
**Purpose**: Analyze sentiment in PDF documents

#### Features

- Sentiment classification (positive/negative/neutral)
- Confidence scoring (0-1)
- Summary explanation
- Two analysis modes

#### Analysis Modes

**Vector Mode**:

- Extracts text from PDF
- Analyzes text content
- Fast and efficient

**Multimodal Mode**:

- Analyzes PDF visually
- Considers images and layout
- More comprehensive

#### API Endpoint

**POST /sentiment-pdf**

- Parameters: `file`, `mode` (vector/multimodal)
- Returns: Sentiment, score, summary

Response Structure:

```json
{
  "message": "PDF sentiment analyzed successfully",
  "mode": "multimodal",
  "filename": "document.pdf",
  "result": {
    "sentiment": "positive",
    "score": 0.85,
    "summary": "The document expresses predominantly positive sentiment..."
  }
}
```

#### Sentiment Values

- **positive**: Optimistic, constructive, favorable tone
- **negative**: Critical, unfavorable, pessimistic tone
- **neutral**: Balanced, factual, objective tone

#### Use Cases

1. **Customer Feedback**: Analyze feedback documents
2. **Report Analysis**: Assess tone of reports
3. **Content Review**: Review communication sentiment
4. **Quality Assessment**: Evaluate document tone

---

### 5. Summarizer Service

**Port**: 8003
**Purpose**: Generate summaries of PDF documents

#### Features

- Three summary types (brief/comprehensive/detailed)
- Key points extraction
- Two analysis modes
- Adjustable detail level

#### Summary Types

**Brief**:

- Concise overview
- 3-4 key points
- Quick reading

**Comprehensive**:

- Balanced summary
- 5-6 key points
- Good overview

**Detailed**:

- In-depth summary
- 8-10 key points
- Complete understanding

#### Analysis Modes

**Vector Mode**:

- Text-based analysis
- Efficient for text-heavy docs
- Uses embeddings

**Multimodal Mode**:

- Visual analysis
- Captures images/charts
- More comprehensive

#### API Endpoint

**POST /summarize**

- Parameters: `file`, `mode` (vector/multimodal), `summary_type`
- Returns: Summary and key points

Response Structure:

```json
{
  "message": "PDF summarized successfully",
  "mode": "vector",
  "summary_type": "comprehensive",
  "filename": "document.pdf",
  "summary": "This document discusses...",
  "key_points": [
    "Point 1",
    "Point 2",
    "Point 3"
  ]
}
```

#### Use Cases

1. **Document Review**: Quickly understand long documents
2. **Report Summaries**: Create executive summaries
3. **Research Papers**: Extract key findings
4. **Legal Documents**: Summarize complex agreements

---

### 6. CSV Analyzer Service

**Port**: 8501
**Purpose**: Interactive CSV data analysis using natural language

#### Features

- Natural language queries
- Multiple CSV file support
- Data visualization
- Statistical analysis
- Custom pandas operations

#### Available Tools

**load_csv_tool**:

- Loads CSV files for analysis
- Stores data in memory
- Returns shape and columns

**get_data_info_tool**:

- Shows dataset information
- Data types, null counts
- Memory usage

**describe_data_tool**:

- Statistical descriptions
- Numeric and categorical summaries
- Top values and frequencies

**create_visualization_tool**:

- Generate plots: histogram, scatter, bar, box, heatmap
- Saves as PNG
- Returns filename

**execute_pandas_code_tool**:

- Run custom pandas code
- Supports complex operations
- Safe execution environment

#### Analysis Capabilities

**Data Inspection**:

- View dataset structure
- Check for missing values
- Understand data types

**Statistical Analysis**:

- Descriptive statistics
- Correlations
- Aggregations

**Visualizations**:

- Distribution plots
- Relationship visualizations
- Categorical summaries
- Custom plots

**Data Transformations**:

- Filtering
- Grouping
- Calculations
- Custom operations

#### Usage Flow

```
┌──────────────┐
│ Upload CSV   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Load Files   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Ask Questions│ ←───┐
└──────┬───────┘     │
       │             │
       ▼             │
┌──────────────┐     │
│ Agent Selects│     │
│ Appropriate  │     │
│ Tools        │     │
└──────┬───────┘     │
       │             │
       ▼             │
┌──────────────┐     │
│ Generate     │     │
│ Response &   │     │
│ Plots        │     │
└──────┬───────┘     │
       │             │
       ▼             │
┌──────────────┐     │
│ Display      │     │
│ Results      │─────┘
└──────────────┘
```

#### Example Queries

- "Show me basic statistics for all columns"
- "Create a histogram of age distribution"
- "What's the correlation between price and quantity?"
- "Group by category and show average sales"
- "Find all rows where amount > 1000"

#### Use Cases

1. **Data Exploration**: Quickly understand datasets
2. **Sales Analysis**: Analyze sales data
3. **Report Generation**: Create data visualizations
4. **Trend Analysis**: Identify patterns and trends

---

## Web UI Guide

### Accessing the Web UI

**URL**: http://localhost:8500

The Web UI provides a unified interface for all services with an intuitive navigation system.

### Main Navigation

#### Overview Page

- Quick action buttons for all services
- Service descriptions
- Direct links to functionalities

#### Sidebar Navigation

- **Overview**: Return to home page
- **Document Classifier**: Classify documents
- **Document Extraction**: Extract structured data
- **Ops Document Query Tool**: Analyze and query PDFs
- **PDF Sentiment Analysis**: Analyze sentiment
- **PDF Summarizer**: Generate summaries
- **Member Document Search**: Search extracted fields
- **Document Workflow**: End-to-end processing
- **CSV Analyzer**: Link to CSV analysis (separate UI)

---

### Using Each Service in the UI

#### 1. Document Classifier UI

**Access**: Click "Document Classifier" in sidebar or quick action

**Steps**:

1. **Upload PDF**: Use file uploader to select document
2. **Classify**: Click "Classify Document" button
3. **Review Results**: Expand each page classification
   - View page preview image
   - See document type and confidence
   - Read classification reasoning
4. **Use Results**: Copy classification data for processing

**UI Features**:

- Visual page previews
- Confidence meters
- Detailed reasoning per page
- Expandable page sections

---

#### 2. Document Extraction UI

**Access**: Click "Document Extraction" in sidebar

**Steps**:

**Viewing Existing Schemas**:

1. Click "Refresh Schemas List" to load all schemas
2. Select schema from dropdown
3. View schema fields with properties
4. Click "Modify This Schema" to edit

**Extracting Data**:

1. **Upload Document**: PDF, JPEG, or PNG
2. **Extract**: Click "Extract Data" button
3. **Review Results**:
   - **If Active Schema Exists**: View extracted data immediately
   - **If No Schema**: Review generated schema
4. **For New Schemas**:
   - Review field definitions
   - Modify fields as needed
   - Add new fields using form
   - Mark fields for removal
   - Save modifications or approve

**Extracted Data Display**:

- Side-by-side view: Document preview + extracted fields
- PDF preview embedded in UI
- Scrollable field list with styling
- Boolean values shown with badges
- Code formatting for structured data

**Schema Modification**:

1. Expand field to edit
2. Modify description, type, example, required status
3. For string types, add regex patterns
4. Check "Remove this field" to delete
5. Add new fields using the form
6. Click "Save Modifications" or "Approve Schema"

**Schema Fields**:

- **Description**: Field purpose and meaning
- **Type**: string, boolean, integer, number
- **Example**: Sample value
- **Required**: Whether field is mandatory
- **Pattern**: Regex validation (for strings)

---

#### 3. Ops Document Query Tool (Analyzer) UI

**Access**: Click "Ops Document Query Tool" in sidebar

**Three Tabs Available**:

**Tab 1: Analyze**:

1. Upload PDF document
2. Select analysis mode (vector/multimodal)
3. Enter search query (e.g., "List criminal activities")
4. Click "Analyze Document"
5. View analysis results
6. Expand "Retrieved Vectors" to see source chunks
7. Click "View Source" to open original PDF

**Tab 2: Ingest**:

1. Upload PDF to add to vector store
2. Click "Ingest Document"
3. Receive confirmation with unique filename
4. Document now available for querying

**Tab 3: Query**:

1. Enter query string
2. Set number of results (k)
3. Click "Query Vector Store"
4. View results with metadata
5. Click "View Source" to open PDF

**Use Case Flow**:

```
Federal Criminal Search Example:
1. Ingest → Upload federal criminal records
2. Query → "Any criminal history for John Doe?"
3. View → Relevant records retrieved
4. Source → Click to see original document
```

---

#### 4. PDF Sentiment Analysis UI

**Access**: Click "Sentiment Analysis" in sidebar

**Steps**:

1. **Upload PDF**: Select document for analysis
2. **Select Mode**: Choose vector or multimodal
3. **Analyze**: Click "Analyze Sentiment"
4. **Review Results**:
   - Sentiment classification (positive/negative/neutral)
   - Confidence score (0-1)
   - Summary explanation
   - Analysis mode used
   - Filename

**Result Display**:

- Metric cards for sentiment and score
- Divider-separated sections
- Summary with HTML formatting
- Mode and filename metadata

---

#### 5. PDF Summarizer UI

**Access**: Click "PDF Summarizer" in sidebar

**Steps**:

1. **Upload PDF**: Select document
2. **Select Mode**: Vector or multimodal
3. **Select Summary Type**: Brief, comprehensive, or detailed
4. **Generate**: Click "Generate Summary"
5. **Review**:
   - Generated summary text
   - Bulleted list of key points

**Summary Types Explained**:

- **Brief**: Quick overview, 3-4 points
- **Comprehensive**: Balanced, 5-6 points
- **Detailed**: In-depth, 8-10 points

---

#### 6. Member Document Search UI

**Access**: Click "Member Document Search" in sidebar

**Features**:

- Pre-filled sample data for PAN, Passport, Aadhar
- Field-level source tracing
- PDF preview integration

**Steps**:

1. **Expand Document Section**: PAN Card, Passport, or Aadhar Card
2. **Review Fields**: See extracted data
3. **View Source**: Click "View Source" next to any field
4. **Query Executes**: System searches vector store
5. **PDF Displays**: Relevant source document shown inline
6. **Hide PDF**: Click "Hide PDF" to collapse

**Display Features**:

- Field name and value side-by-side
- Boolean values with colored badges
- Code-formatted text values
- Inline PDF viewer (600px height)
- Loading indicators during search

**Sample Data Included**:

- PAN Card with 12 fields
- Passport with 18+ fields
- Aadhar Card with 11 fields

---

#### 7. Document Workflow UI

**Access**: Click "Document Workflow" in sidebar

**Purpose**: Complete end-to-end document processing

**Steps**:

1. **Upload PDF**: Select multi-page document
2. **Start Workflow**: Click "Start Workflow" button

**Automatic Processing**:

**Step 1 - Classification**:

- All pages classified automatically
- Results shown in expandable sections
- Confidence and reasoning displayed

**Step 2 - Document Splitting**:

- PDF split by document type
- Consecutive pages of same type grouped
- Temporary files created for each group

**Step 3 - Parallel Extraction**:

- All document groups extracted simultaneously
- Real-time updates as results come in
- No waiting for sequential processing

**Step 4 - Results Display**:

- Each document group shown in expandable section
- Side-by-side: PDF preview + extracted data
- Download links for split PDFs
- Raw response available in expander

**Result Features**:

- **Confidence Display**: Shows classification confidence
- **PDF Preview**: Embedded 350x500 viewer
- **Extracted Data**: JSON formatted display
- **Status Indicators**: pending_review warnings
- **Raw Response**: Full API response viewable

**Example Workflow**:

```
Upload: 10-page PDF with mixed documents
  ↓
Classification: 
  - Pages 1-2: Aadhar Card (95% confidence)
  - Pages 3-5: Passport (92% confidence)
  - Pages 6-7: PAN Card (90% confidence)
  - Pages 8-10: Bank Statement (88% confidence)
  ↓
Split: 4 separate PDFs created
  ↓
Extract: All 4 processed in parallel
  ↓
Display: 4 expandable results with data
```

---

### CSV Analyzer UI (Separate Application)

**Access**: Click "CSV Analyzer" link or go to http://localhost:8501

**Layout**:

- **Sidebar**: File upload, loaded files list, clear history
- **Main Area**: Chat interface for queries
- **Plot Display**: Visualizations shown inline

**Steps**:

**Loading CSV Files**:

1. Click "Choose one or more CSV files" in sidebar
2. Select CSV file(s)
3. Click "Load CSV(s)"
4. Wait for confirmation
5. Files listed in sidebar

**Asking Questions**:

1. Type query in chat input at bottom
2. Press Enter or click send
3. Agent processes request
4. Response displayed with plots

**Example Queries**:

- "Show basic info about the data"
- "Describe the age column"
- "Create a histogram of salary"
- "What's the correlation between experience and salary?"
- "Group by department and show average salary"

**Plot Display**:

- Plots automatically displayed in chat
- Filenames shown in response
- Plots saved as PNG files

**Clearing Data**:

- Click "Clear Chat History" in sidebar
- Removes all loaded files
- Clears conversation
- Deletes temporary files

---

## Common Workflows

### Workflow 1: KYC Document Processing

**Goal**: Process identity documents for KYC verification

**Steps**:

1. **Upload Mixed PDF** (Workflow UI)

   - Contains: Aadhar, PAN, Passport, Bank Statement
2. **Classification** (Automatic)

   - System identifies each document type
   - Pages grouped by type
3. **Extraction** (Automatic)

   - Data extracted from each document
   - Schema-based extraction
4. **Review** (Manual)

   - Verify extracted data
   - Check confidence scores
   - Download split documents
5. **Member Search** (Optional)

   - Search across extracted fields
   - Trace back to source documents

**Result**: Structured data ready for KYC database

---

### Workflow 2: Federal Criminal Record Search

**Goal**: Search criminal records for a person

**Steps**:

1. **Ingest Documents** (Analyzer - Ingest Tab)

   - Upload federal criminal record PDFs
   - Build searchable vector store
2. **Query** (Analyzer - Query Tab)

   - Enter: "Criminal history for John Doe, DOB 01/01/1990"
   - Retrieve relevant records
3. **Review Results**

   - View matched records
   - Check source documents
   - Assess relevance
4. **Generate Report** (Summarizer)

   - Summarize findings
   - Extract key points

**Result**: Criminal background check completed

---

### Workflow 3: Document Sentiment Analysis

**Goal**: Analyze tone of customer feedback documents

**Steps**:

1. **Upload Documents** (Sentiment Analysis UI)

   - Customer feedback PDFs
2. **Analyze** (Multimodal Mode)

   - Get sentiment classification
   - Review confidence scores
3. **Summarize** (Summarizer)

   - Generate summary of feedback
   - Extract key points
4. **Report**

   - Compile sentiment trends
   - Identify areas for improvement

**Result**: Sentiment analysis report

---

### Workflow 4: CSV Data Analysis

**Goal**: Analyze sales data and create visualizations

**Steps**:

1. **Load Data** (CSV Analyzer UI)

   - Upload sales CSV file
2. **Explore**

   - "Show basic statistics"
   - "Describe the sales column"
3. **Visualize**

   - "Create histogram of sales"
   - "Show correlation heatmap"
4. **Analyze Trends**

   - "Group by month and show total sales"
   - "What product has highest sales?"
5. **Generate Insights**

   - Review plots
   - Extract conclusions

**Result**: Sales analysis with visualizations

---

### Workflow 5: Schema Management

**Goal**: Create and maintain extraction schemas

**Steps**:

1. **Generate Schema** (Extraction UI)

   - Upload sample document
   - System generates initial schema
2. **Review Schema**

   - Check field definitions
   - Verify types and patterns
3. **Modify**

   - Edit descriptions
   - Adjust validation patterns
   - Add/remove fields
4. **Test**

   - Extract from new document
   - Verify accuracy
5. **Approve**

   - Activate schema
   - Use for production
6. **Version Control**

   - Modify as needed
   - Track changes
   - Maintain history

**Result**: Production-ready extraction schema

---

## API Reference

### Quick Reference Table

| Service    | Endpoint              | Method | Purpose                 |
| ---------- | --------------------- | ------ | ----------------------- |
| Analyzer   | /analyze              | POST   | Analyze PDF with query  |
| Analyzer   | /vectorstore/ingest   | POST   | Add PDF to vector store |
| Analyzer   | /vectorstore/query    | POST   | Query vector store      |
| Classifier | /classify-pdf         | POST   | Classify document types |
| Extractor  | /extract              | POST   | Extract structured data |
| Extractor  | /schemas              | GET    | List all schemas        |
| Extractor  | /schemas/{id}/approve | PUT    | Approve schema          |
| Extractor  | /schemas/{id}/modify  | PUT    | Modify schema           |
| Sentiment  | /sentiment-pdf        | POST   | Analyze sentiment       |
| Summarizer | /summarize            | POST   | Generate summary        |

### Common Request Examples

#### Analyze PDF (Vector Mode)

```bash
curl -X POST http://localhost:8001/analyze \
  -F "file=@document.pdf" \
  -F "search_query=Summarize this document" \
  -F "mode=vector"
```

#### Classify Document

```bash
curl -X POST http://localhost:8004/classify-pdf \
  -F "file=@document.pdf"
```

#### Extract Data

```bash
curl -X POST http://localhost:8005/extract \
  -F "document=@identity.pdf"
```

#### Analyze Sentiment

```bash
curl -X POST http://localhost:8002/sentiment-pdf \
  -F "file=@feedback.pdf" \
  -F "mode=multimodal"
```

#### Generate Summary

```bash
curl -X POST http://localhost:8003/summarize \
  -F "file=@report.pdf" \
  -F "mode=vector" \
  -F "summary_type=comprehensive"
```

---

## Technical Implementation

### Core Technologies

#### LangChain Framework

- Document loaders (PyPDFLoader)
- Text splitters (RecursiveCharacterTextSplitter)
- Vector stores (FAISS)
- Agents and tools
- Message schemas

#### Google Gemini 2.5 Flash

- **Text Analysis**: Structured output generation
- **Vision**: Multimodal PDF analysis
- **Embeddings**: text-embedding-004 model
- **Structured Outputs**: Pydantic schema enforcement

#### FastAPI

- Async request handling
- CORS middleware
- File upload handling
- Structured responses
- API documentation (Swagger/ReDoc)

#### MongoDB (Beanie ODM)

- Schema storage
- Version tracking
- Status management
- Async operations

#### FAISS Vector Store

- Efficient similarity search
- Persistent storage
- Scalable indexing
- Fast retrieval

#### Streamlit

- Interactive UI components
- File uploaders
- Chat interface
- Real-time updates
- Session state management

---

### Code Architecture

#### Service Structure

```
service/
├── main.py                 # FastAPI app and endpoints
├── requirements.txt        # Dependencies
├── Dockerfile             # Container configuration
├── docker-compose.yml     # Service orchestration
├── README.md              # Service documentation
└── src/
    ├── __init__.py
    ├── config/
    │   ├── __init__.py
    │   ├── llm_config.py  # LLM configuration
    │   └── prompts.py     # System prompts
    ├── schemas/
    │   ├── __init__.py
    │   ├── llm_response_models.py  # Structured output schemas
    │   └── response_models.py       # API response models
    └── utils/
        ├── __init__.py
        └── [service-specific-utils].py
```

#### Key Patterns

**Async/Await**:

- All I/O operations async
- Concurrent processing where possible
- Non-blocking file operations

**Structured Outputs**:

- Pydantic models for LLM responses
- Type safety
- Validation

**Error Handling**:

- Try-except blocks
- HTTPException for API errors
- Fallback strategies

**Resource Management**:

- Temporary file cleanup
- Context managers
- Async file operations

---

### Environment Variables

Required for all services:

```bash
GOOGLE_API_KEY=your_api_key_here
PORT=service_specific_port
```

For Document Extractor:

```bash
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=document_extraction
```

---

### Deployment

#### Docker Compose

Each service includes docker-compose.yml:

```yaml
version: '3.8'
services:
  service-name:
    build: .
    ports:
      - "${PORT}:${PORT}"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    volumes:
      - ./uploads:/app/uploads
```

#### Running Services

```bash
# Start individual service
cd service-directory
docker-compose up

# Or run directly
python main.py

# Or with uvicorn
uvicorn main:app --host 0.0.0.0 --port 8001
```

---

### Data Flow Examples

#### Vector Search Flow

```
PDF Upload → Text Extraction → Chunking → Embedding → 
FAISS Store → Query → Similarity Search → Retrieve Chunks → 
LLM Analysis → Response
```

#### Multimodal Analysis Flow

```
PDF Upload → Base64 Encoding → Gemini Vision API → 
Structured Response → Format → Return
```

#### Schema Extraction Flow

```
Document Upload → Classification → Schema Lookup → 
[If Not Found] → Generate Schema → Store as IN_REVIEW → 
[If Found] → Extract with Schema → Return Data
```

---

## Best Practices

### Using the System

1. **Start Simple**: Use Summarizer to understand documents before detailed analysis
2. **Ingest First**: For repeated queries, ingest documents to vector store
3. **Choose Modes Wisely**:
   - Vector mode for text-heavy docs
   - Multimodal for visual content
4. **Schema Management**: Review and test schemas before approval
5. **Batch Processing**: Use Workflow UI for multiple documents

### Performance Tips

1. **Vector Store**: Pre-ingest frequently queried documents
2. **Chunk Size**: 10,000 chars works well for most documents
3. **Parallel Processing**: Workflow UI processes documents concurrently
4. **Caching**: Approved schemas cached for fast extraction

### Security Considerations

1. **API Keys**: Keep GOOGLE_API_KEY secure
2. **File Upload**: Validate file types
3. **Code Execution**: CSV analyzer uses safe execution environment
4. **Data Storage**: Clean up temporary files

---

## Troubleshooting

### Common Issues

**Service Not Responding**:

- Check if service is running: `docker ps`
- Check logs: `docker logs <container_name>`
- Verify port not in use: `lsof -i :<port>`

**API Key Errors**:

- Verify GOOGLE_API_KEY in .env
- Check API quota
- Ensure key has correct permissions

**Vector Store Errors**:

- Check if faiss_index exists
- Verify embeddings model access
- Clear and rebuild index

**Schema Not Found**:

- Check MongoDB connection
- Verify document type and country
- Review schema status (should be ACTIVE)

**PDF Processing Errors**:

- Ensure PDF is valid
- Check file size limits
- Verify PDF has extractable text

---

## Conclusion

The KYC Ops Document Service Hub provides a comprehensive solution for document processing with:

- Multiple specialized AI services
- Unified web interface
- Flexible APIs
- Dynamic schema management
- Real-time processing

Use this guide as your reference for understanding, deploying, and using the system effectively.

For additional support, refer to individual service README files and API documentation at `/docs` endpoints.

---

**Document Version**: 1.0
**Last Updated**: November 2025
**Maintained By**: Development Team
