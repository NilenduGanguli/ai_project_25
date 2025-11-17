# Frontend Module - Visual Overview

## 📊 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE                                 │
│                      Browser: localhost:8501                             │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    STREAMLIT FRONTEND (app.py)                           │
│ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ │
│ ┃                           Navigation                                ┃ │
│ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ │
│                                                                           │
│ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│ │   📤 Upload  │  │ 📚 View      │  │ ✏️ Modify    │  │ 🔍 Extract   │ │
│ │   Documents  │  │   Schemas    │  │   Schemas    │  │   & View     │ │
│ │              │  │              │  │              │  │              │ │
│ │ • Multi-file │  │ • Dashboard  │  │ • Add Field  │  │ • Upload     │ │
│ │ • Preview    │  │ • Filters    │  │ • Update     │  │ • Side-by-   │ │
│ │ • Process    │  │ • Sort       │  │ • Remove     │  │   side View  │ │
│ │              │  │ • Approve    │  │ • Versions   │  │ • Download   │ │
│ └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                                           │
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │                    Helper Functions                                  │ │
│ │  • check_api_health()    • upload_document_for_schema()             │ │
│ │  • get_all_schemas()     • approve_schema()                         │ │
│ │  • modify_schema()       • display_document()                       │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ REST API
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    BACKEND API (FastAPI)                                 │
│                      Port: 8005                                          │
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │  GET  /                    → Health Check                            │ │
│ │  POST /extract             → Upload & Extract Documents              │ │
│ │  GET  /schemas             → Get All Schemas                         │ │
│ │  PUT  /schemas/{id}/approve → Approve Schema                         │ │
│ │  PUT  /schemas/{id}/modify  → Modify Schema                          │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         MONGODB DATABASE                                 │
│                      Port: 27017                                         │
│                   Collection: document_schemas                           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📱 User Interface Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        LANDING PAGE (Upload)                             │
│                                                                           │
│  Instructions Box                                                        │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │ • Upload documents                                              │    │
│  │ • System classifies automatically                               │    │
│  │ • Generates schema if needed                                    │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │  📎 File Uploader                                               │    │
│  │  [Choose Files] (PDF, JPEG, PNG)                                │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                                                           │
│  ┌───────────────────┬─────────────────┐                               │
│  │  Document 1       │   Upload        │                               │
│  │  [Preview]        │   Summary       │                               │
│  │                   │   • Count: 2    │                               │
│  │  Document 2       │   • Size: 5MB   │                               │
│  │  [Preview]        │                 │                               │
│  └───────────────────┴─────────────────┘                               │
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │           [🚀 Process Documents]                                │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                                                           │
│  Response (201 - Schema Generated):                                     │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │ ✅ Schema Generated Successfully!                               │    │
│  │                                                                  │    │
│  │ Schema ID: 507f1f77bcf86cd799439011                            │    │
│  │ Document Type: passport                                         │    │
│  │ Country: USA                                                    │    │
│  │ Confidence: 95.3%                                               │    │
│  │                                                                  │    │
│  │ Generated Fields (showing 5 of 23):                             │    │
│  │ • full_name: string                                             │    │
│  │ • passport_number: string                                       │    │
│  │ • date_of_birth: date                                           │    │
│  │ • nationality: string                                           │    │
│  │ • expiry_date: date                                             │    │
│  └────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 View Schemas Page

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      📚 ALL SCHEMAS                                      │
│                                                                           │
│  Statistics Dashboard:                                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │    15    │  │    8     │  │    5     │  │    2     │               │
│  │  Total   │  │  Active  │  │  Review  │  │  Deprecated│              │
│  │ Schemas  │  │          │  │          │  │          │               │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘               │
│                                                                           │
│  ┌──────────────────┬──────────────────┬────────────────────────┐      │
│  │ Filter: Status ▼ │ Filter: Type   ▼ │ Sort: Created Date   ▼ │      │
│  │ [In Review]      │ [All]            │ [Newest First]         │      │
│  └──────────────────┴──────────────────┴────────────────────────┘      │
│                                                                           │
│  Showing 5 of 15 schemas                                                │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ ▶ PASSPORT (USA) - Version 2 - [In Review]                      │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ ▼ PASSPORT (USA) - Version 1 - [Active]                         │   │
│  │                                                                   │   │
│  │   Schema Details                 Quick Actions                   │   │
│  │   ├─ ID: 507f...                 ┌──────────────┐               │   │
│  │   ├─ Type: passport               │ ✅ Approve   │               │   │
│  │   ├─ Country: USA                 └──────────────┘               │   │
│  │   ├─ Version: 1                   ┌──────────────┐               │   │
│  │   ├─ Status: Active               │ ✏️ Modify    │               │   │
│  │   ├─ Created: 2024-01-15          └──────────────┘               │   │
│  │   └─ Updated: 2024-01-15                                         │   │
│  │                                                                   │   │
│  │   Schema Fields (23 total):                                      │   │
│  │   ┌───────────────────────────────────────────────────────────┐ │   │
│  │   │ full_name (string)                                         │ │   │
│  │   │ Full legal name as appears on document                     │ │   │
│  │   │ Required: Yes  Example: John Michael Smith                 │ │   │
│  │   └───────────────────────────────────────────────────────────┘ │   │
│  │   ┌───────────────────────────────────────────────────────────┐ │   │
│  │   │ passport_number (string)                                   │ │   │
│  │   │ Unique passport identification number                      │ │   │
│  │   │ Required: Yes  Example: 123456789                          │ │   │
│  │   └───────────────────────────────────────────────────────────┘ │   │
│  │   ... 21 more fields                                             │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## ✏️ Modify Schema Page

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      ✏️ MODIFY SCHEMA                                    │
│                                                                           │
│  Select Schema: [PASSPORT (USA) - v1  ▼]                                │
│                                                                           │
│  ┌───────────────────────────┬────────────────────────────────────┐    │
│  │   Current Schema          │    Modification Type               │    │
│  │   ├─ ID: 507f...          │    ○ Add New Field                 │    │
│  │   ├─ Type: passport       │    ● Update Existing Field         │    │
│  │   ├─ Country: USA         │    ○ Remove Field                  │    │
│  │   ├─ Version: 1           │                                     │    │
│  │   └─ Status: Active       │                                     │    │
│  └───────────────────────────┴────────────────────────────────────┘    │
│                                                                           │
│  ── Update Existing Field ──────────────────────────────────────────    │
│                                                                           │
│  Select Field: [full_name  ▼]                                           │
│                                                                           │
│  ┌────────────────────────────┬────────────────────────────────────┐   │
│  │   Current Values           │    New Values                       │   │
│  │   {                        │                                     │   │
│  │     "type": "string",      │    Type: [string  ▼]               │   │
│  │     "description": "Full   │    Required: [✓]                   │   │
│  │       legal name",         │    Description:                     │   │
│  │     "required": true,      │    ┌──────────────────────────┐    │   │
│  │     "example": "John..."   │    │ Full legal name as shown │    │   │
│  │   }                        │    │ on the passport document │    │   │
│  │                            │    └──────────────────────────┘    │   │
│  │                            │    Example:                         │   │
│  │                            │    [John Michael Smith]             │   │
│  └────────────────────────────┴────────────────────────────────────┘   │
│                                                                           │
│  Change Description:                                                     │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ Updated description to be more specific about source            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │              [💾 Submit Modifications]                           │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🔍 Extract & View Page

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    🔍 EXTRACT & VIEW RESULTS                             │
│                                                                           │
│  Instructions:                                                           │
│  • Upload document(s) for data extraction                                │
│  • System uses active schema to extract structured data                  │
│  • View extracted data alongside the original document                   │
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │  [Choose Files]                                                 │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │           [🚀 Extract Data]                                     │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                                                           │
│  ✅ Data extracted successfully!                                         │
│                                                                           │
│  ┌──────────────────────────────┬──────────────────────────────────┐   │
│  │   📄 Original Document       │   📊 Extracted Data              │   │
│  │                              │                                   │   │
│  │  ┌────────────────────────┐ │   ▼ Extraction Metadata          │   │
│  │  │                        │ │   ├─ Type: passport               │   │
│  │  │   [Document Image]     │ │   ├─ Country: USA                │   │
│  │  │                        │ │   ├─ Confidence: 95.3%           │   │
│  │  │   PASSPORT             │ │   └─ Schema Version: 1           │   │
│  │  │   United States        │ │                                   │   │
│  │  │   [Photo]              │ │   ▼ Extracted Fields             │   │
│  │  │                        │ │   ┌────────────────────────────┐ │   │
│  │  │   Name: JOHN SMITH     │ │   │ Full Name:                 │ │   │
│  │  │   Passport No: 123...  │ │   │ JOHN MICHAEL SMITH         │ │   │
│  │  │                        │ │   └────────────────────────────┘ │   │
│  │  └────────────────────────┘ │   ┌────────────────────────────┐ │   │
│  │                              │   │ Passport Number:           │ │   │
│  │                              │   │ 123456789                  │ │   │
│  │                              │   └────────────────────────────┘ │   │
│  │                              │   ┌────────────────────────────┐ │   │
│  │                              │   │ Date of Birth:             │ │   │
│  │                              │   │ 1990-01-15                 │ │   │
│  │                              │   └────────────────────────────┘ │   │
│  │                              │   ... 20 more fields             │   │
│  │                              │                                   │   │
│  │                              │   ┌────────────────────────────┐ │   │
│  │                              │   │  [📥 Download JSON]        │ │   │
│  │                              │   └────────────────────────────┘ │   │
│  └──────────────────────────────┴──────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🗂️ File Structure Diagram

```
image-data-extractor-frontend/
│
├── 📄 Core Application
│   ├── app.py (700+ lines)          ← Main Streamlit application
│   └── requirements.txt             ← Python dependencies
│
├── 🐳 Docker Support
│   ├── Dockerfile                   ← Container build config
│   ├── docker-compose.yml           ← Multi-service orchestration
│   ├── .dockerignore                ← Build exclusions
│   └── .env.example                 ← Environment template
│
├── ⚙️ Configuration
│   ├── .streamlit/
│   │   └── config.toml              ← Streamlit theme & settings
│   └── .gitignore                   ← Git exclusions
│
├── 🛠️ Automation
│   └── run.sh (400+ lines)          ← Management script
│
└── 📚 Documentation (2500+ lines)
    ├── README.md (500+ lines)       ← Complete guide
    ├── QUICKSTART.md (300+ lines)   ← Quick start guide
    ├── FRONTEND_SUMMARY.md (700+)   ← Technical overview
    ├── DEMO_SCRIPT.md (600+ lines)  ← Demo walkthrough
    └── SETUP_COMPLETE.md (400+)     ← Post-setup guide
```

---

## 🔄 Data Flow Diagram

```
┌────────────┐
│   User     │
└─────┬──────┘
      │
      │ 1. Upload Document
      ▼
┌────────────────────┐
│  Frontend (8501)   │
│  • Validate file   │
│  • Show preview    │
└─────┬──────────────┘
      │
      │ 2. POST /extract
      │    (multipart/form-data)
      ▼
┌────────────────────────────┐
│  Backend API (8005)        │
│  • Classify document       │
│  • Check for schema        │
│  • Generate if needed      │
│  • Extract data if active  │
└─────┬──────────────────────┘
      │
      │ 3. Save/Query
      ▼
┌────────────────────┐
│  MongoDB (27017)   │
│  • document_schemas│
└─────┬──────────────┘
      │
      │ 4. JSON Response
      ▼
┌────────────────────┐
│  Backend API       │
└─────┬──────────────┘
      │
      │ 5. Render UI
      ▼
┌────────────────────┐
│  Frontend          │
│  • Parse response  │
│  • Display result  │
│  • Show document   │
└─────┬──────────────┘
      │
      │ 6. View Result
      ▼
┌────────────┐
│   User     │
└────────────┘
```

---

## 🎨 Color Scheme Visual

```
┌──────────────────────────────────────────────────┐
│  Primary Gradient (Purple)                       │
│  #667eea ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #764ba2 │
│  Used for: Headers, buttons, accents             │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│  Success Gradient (Green)                        │
│  #11998e ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #38ef7d │
│  Used for: Active schemas, success messages      │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│  Warning Gradient (Pink)                         │
│  #f093fb ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #f5576c │
│  Used for: Pending review, warnings              │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│  Neutral (Gray)                                  │
│  #6c757d ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #495057 │
│  Used for: Deprecated items, disabled states     │
└──────────────────────────────────────────────────┘
```

---

## 📊 Component Hierarchy

```
App (main)
│
├── Header
│   └── Title + Divider
│
├── Sidebar
│   ├── Navigation Radio
│   ├── Divider
│   └── Status Info
│
└── Main Content (Router)
    │
    ├── Page: Upload Documents
    │   ├── Instructions Box
    │   ├── File Uploader
    │   ├── Document Previews
    │   ├── Upload Summary
    │   ├── Process Button
    │   └── Result Display
    │
    ├── Page: View All Schemas
    │   ├── Statistics Dashboard
    │   ├── Filter Controls
    │   ├── Schema Count
    │   └── Schema Cards (expandable)
    │       ├── Metadata
    │       ├── Quick Actions
    │       └── Field List
    │
    ├── Page: Modify Schemas
    │   ├── Schema Selector
    │   ├── Current Schema Info
    │   ├── Modification Type Radio
    │   ├── Field Input Form
    │   ├── Change Description
    │   └── Submit Button
    │
    └── Page: Extract & View
        ├── Instructions
        ├── File Uploader
        ├── Extract Button
        └── Results (2-column)
            ├── Document Viewer
            └── Extracted Data
                ├── Metadata
                ├── Fields
                └── Download Button
```

---

**This visual overview provides a comprehensive view of the frontend architecture, UI flow, and component structure.**
