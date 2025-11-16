# Frontend Demo Script

This script provides a guided demonstration of all frontend features.

## Prerequisites
- Backend API running at http://localhost:8005
- MongoDB connected and accessible
- Sample documents ready (PDF/JPEG/PNG)

---

## Demo Flow

### Part 1: Initial Setup (5 minutes)

#### 1.1 Start the Frontend
```bash
cd image-data-extractor-frontend
./run.sh run
```

**Expected:** Browser opens to http://localhost:8501

#### 1.2 Verify Connection
- Look for green "API Status: 🟢 Connected" in sidebar
- If red, check backend: `curl http://localhost:8005/`

---

### Part 2: Upload & Schema Generation (10 minutes)

#### 2.1 Navigate to Upload Page
- Click "📤 Upload Documents" in sidebar
- Read the instructions box

#### 2.2 Upload First Document (New Schema)
1. Click "Choose document(s)"
2. Select a passport or PAN card image/PDF
3. Review the upload summary (count, size)
4. Click document expander to preview
5. Click "🚀 Process Documents"

**Expected Response:** Schema Generated (201)
- Green success box appears
- Schema ID displayed
- Document type and country shown
- Classification confidence shown
- Schema fields preview (first 5 fields)

**Demo Points:**
- "System automatically classified the document"
- "Generated a schema with X fields"
- "Schema is now pending review"

#### 2.3 Upload Same Type Again (Pending)
1. Upload another document of same type
2. Click "Process Documents"

**Expected Response:** Pending Review (202)
- Yellow warning box
- Message about existing schema awaiting approval
- Schema ID of pending schema

**Demo Points:**
- "System recognizes existing schema"
- "Won't create duplicates"
- "Need to approve first"

---

### Part 3: View & Approve Schemas (10 minutes)

#### 3.1 Navigate to Schemas Page
- Click "📚 View All Schemas" in sidebar

#### 3.2 Explore Dashboard
**Show Statistics:**
- Total Schemas count
- Active (green card)
- Pending Review (pink card)
- Deprecated (gray card)

**Demo Points:**
- "Real-time statistics"
- "Color-coded for quick visual reference"

#### 3.3 Use Filters
1. Filter by Status: "in_review"
2. Show filtered results
3. Filter by Document Type
4. Sort by different criteria

**Demo Points:**
- "Powerful filtering for large datasets"
- "Multiple sort options"

#### 3.4 Inspect Schema
1. Click on a schema card to expand
2. Show schema details:
   - ID, type, country, version
   - Status badge
   - Created/updated timestamps
3. Scroll through schema fields
4. Point out field properties:
   - Type, description
   - Required flag
   - Example values

**Demo Points:**
- "Complete schema visibility"
- "Every field documented"
- "Easy to understand structure"

#### 3.5 Approve Schema
1. Find schema with "In Review" status
2. Click "✅ Approve" button
3. Wait for success message
4. **Page auto-refreshes**
5. Show schema now has "Active" status

**Demo Points:**
- "One-click approval"
- "Status updated in real-time"
- "Now ready for extraction"

---

### Part 4: Data Extraction (10 minutes)

#### 4.1 Navigate to Extract Page
- Click "🔍 Extract & View" in sidebar

#### 4.2 Extract Data
1. Upload document of approved type
2. Click "🚀 Extract Data"
3. Wait for processing

**Expected Response:** Data Extracted (200)
- Success message
- Two-column layout appears

#### 4.3 Explore Results
**Left Column - Original Documents:**
1. Expand document viewer
2. Show document preview

**Right Column - Extracted Data:**
1. Expand "Extraction Metadata"
   - Show document type, country
   - Show confidence score
   - Show schema version used
2. Expand "Extracted Fields"
   - Show all extracted values
   - Highlight field organization
   - Point out data types

**Demo Points:**
- "Side-by-side comparison"
- "Structured data from unstructured documents"
- "Confidence scores for quality assurance"

#### 4.4 Download Results
1. Click "📥 Download JSON" button
2. Open downloaded file
3. Show JSON structure

**Demo Points:**
- "Export for integration"
- "Standard JSON format"
- "Timestamped filename"

---

### Part 5: Schema Modification (15 minutes)

#### 5.1 Navigate to Modify Page
- Click "✏️ Modify Schemas" in sidebar

#### 5.2 Demo: Add New Field
1. Select an active schema
2. Choose "Add New Field"
3. Fill in details:
   - Field name: `middle_name`
   - Type: `string`
   - Description: `Middle name of the document holder`
   - Required: `unchecked`
   - Example: `Kumar`
4. Change description: `Adding middle name field for better identification`
5. Click "💾 Submit Modifications"

**Expected:**
- Success message
- New schema info displayed
- Version number incremented
- Status: "In Review"

**Demo Points:**
- "Version control built-in"
- "Original schema preserved"
- "Change tracking with descriptions"

#### 5.3 Demo: Update Existing Field
1. Select the newly created schema (still in review)
2. Choose "Update Existing Field"
3. Select a field to update
4. Show current vs new comparison
5. Modify description or type
6. Submit with description

**Demo Points:**
- "Side-by-side comparison"
- "Non-destructive editing"
- "Audit trail maintained"

#### 5.4 Demo: Remove Field
1. Choose "Remove Field"
2. Select field to remove
3. Show warning message
4. Show field details being removed
5. Submit with description

**Demo Points:**
- "Confirmation required"
- "Clear about what's being removed"
- "Safety mechanisms in place"

---

### Part 6: Complete Workflow Demo (10 minutes)

Demonstrate the entire cycle:

#### 6.1 Upload New Document Type
- Upload document of new type (e.g., driver's license)
- Show schema generation

#### 6.2 Go to Schemas Page
- Show new schema in "Pending" status
- Review schema fields
- Approve schema

#### 6.3 Extract Data
- Upload same document type again
- Show data extraction with active schema
- Download results

#### 6.4 Modify Schema
- Add field based on "missing data"
- Show version increment
- Explain review process

**Demo Points:**
- "End-to-end workflow"
- "From upload to extraction"
- "Continuous improvement cycle"

---

## Advanced Features Demo (5 minutes)

### Show UI Features
1. **Responsive Design**
   - Resize browser window
   - Show mobile-friendly layout

2. **Status Indicators**
   - Point out color coding
   - Explain badge meanings

3. **Error Handling**
   - Try uploading wrong file type
   - Show user-friendly error message

4. **Navigation**
   - Show sidebar always accessible
   - Demonstrate page switching

5. **Real-time Updates**
   - Approve a schema
   - Show immediate status change

---

## Q&A Preparation

### Common Questions

**Q: How long does schema generation take?**
A: Typically 30-60 seconds depending on document complexity.

**Q: Can I modify deprecated schemas?**
A: No, only Active and In Review schemas can be modified.

**Q: What happens to old data when schema changes?**
A: Old schemas are deprecated but preserved. Old extractions remain valid.

**Q: How many documents can I upload at once?**
A: Multiple documents up to 200MB total.

**Q: What document formats are supported?**
A: PDF, JPEG, and PNG files.

**Q: Can I delete a schema?**
A: Currently no, schemas are deprecated rather than deleted for audit trail.

**Q: How accurate is the classification?**
A: Confidence scores are displayed. Threshold is configurable (default: 0.7).

**Q: Can I export schemas?**
A: Currently via API or MongoDB. Export feature planned for future.

---

## Demo Tips

### Before Demo
- [ ] Clear any test data from MongoDB
- [ ] Prepare sample documents (various types)
- [ ] Test backend connection
- [ ] Have browser dev tools ready
- [ ] Prepare backup API endpoint if needed

### During Demo
- Explain what you're doing before clicking
- Highlight key UI elements
- Point out auto-refresh behaviors
- Show error handling
- Demonstrate filters and sorting
- Use real-world examples

### After Demo
- Summarize key features
- Discuss integration possibilities
- Show documentation
- Provide quick start guide
- Answer questions

---

## Troubleshooting During Demo

### If API connection fails:
```bash
# Quick check
curl http://localhost:8005/

# Restart backend
cd ../image-data-extractor
docker-compose restart

# Check logs
docker logs image-data-extractor-api
```

### If frontend crashes:
```bash
# Restart frontend
Ctrl+C
./run.sh run

# Or force kill
lsof -ti:8501 | xargs kill -9
./run.sh run
```

### If upload fails:
- Check file size (< 200MB)
- Verify file format
- Check backend logs
- Try smaller file

### If schema not appearing:
- Refresh page (Ctrl+R)
- Check MongoDB connection
- Verify schema was created (check API response)

---

## Demo Variations

### Quick Demo (5 minutes)
1. Upload document → Show schema generation
2. Approve schema → Show activation
3. Extract data → Show results

### Full Demo (30 minutes)
- All sections above

### Technical Demo (45 minutes)
- All sections
- Show docker-compose setup
- Explain architecture
- Demonstrate API calls
- Show MongoDB data
- Discuss integration options

### Executive Demo (10 minutes)
1. Show dashboard statistics
2. Quick upload → extract workflow
3. Highlight business value:
   - Automation
   - Accuracy
   - Scalability
   - Audit trail

---

## Post-Demo Resources

Provide attendees with:
1. QUICKSTART.md
2. README.md
3. GitHub repository link
4. API documentation
5. Sample documents
6. Docker compose file
7. Contact information

---

**Good luck with your demo! 🎉**
