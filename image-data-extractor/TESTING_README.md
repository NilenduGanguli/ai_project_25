# Testing Script for Image Data Extractor

This script demonstrates the complete workflow for the Image Data Extractor service.

## Overview

The `testing.py` script performs the following steps:

1. **Health Check**: Verifies the service is running
2. **Schema Generation**: Uploads a passport PDF to generate a schema
3. **Schema Retrieval**: Fetches all schemas from the database
4. **Schema Approval**: Approves the generated schema
5. **Data Extraction**: Tests extraction using the approved schema

## Prerequisites

- Service must be running: `docker-compose up -d`
- Python 3.x installed
- `requests` library installed: `pip install requests`

## Usage

### Run the Complete Test

```bash
cd /Users/neelu/dev/ai_project_25/image-data-extractor
python3 testing.py
```

### Expected Output

The script will display color-coded output:
- 🟢 **Green (✓)**: Success messages
- 🟡 **Yellow (→)**: Info messages
- 🔴 **Red (✗)**: Error messages
- 🔵 **Blue**: Section headers

## Test Workflow

### Step 1: Schema Generation
- Uploads `test/Passport.pdf` to `/extract` endpoint
- Service classifies document type (passport, IN)
- Generates schema with 30+ fields specific to Indian passports
- Returns schema ID for approval

### Step 2: Schema Approval
- Calls `/schemas/{schema_id}/approve` endpoint
- Changes schema status from `in_review` to `active`
- Schema becomes available for data extraction

### Step 3: Data Extraction
- Re-uploads the same passport PDF
- Service uses the approved schema
- Extracts structured data including:
  - Personal information (name, DOB, nationality)
  - Passport details (number, issue/expiry dates)
  - MRZ lines (Machine Readable Zone)
  - Address information
  - Verification flags (photo, signature, barcode present)

## Generated Schema Fields

The Indian passport schema includes:

| Field | Type | Description |
|-------|------|-------------|
| passport_number | string | Unique passport number |
| surname | string | Last name of holder |
| given_names | string | First/middle names |
| nationality | string | Holder's nationality |
| sex | string | M/F/O |
| date_of_birth | date | DOB in DD/MM/YYYY format |
| place_of_birth | string | Birth location |
| date_of_issue | date | Issue date |
| date_of_expiry | date | Expiry date |
| mrz_line_1 | string | Machine readable zone line 1 |
| mrz_line_2 | string | Machine readable zone line 2 |
| name_of_father_legal_guardian | string | Father's name |
| name_of_mother | string | Mother's name |
| address_line_1 | string | Address line 1 |
| pin_code | string | Postal code |
| photo_present | boolean | Photo visibility check |
| signature_present | boolean | Signature visibility check |
| is_document_correct | boolean | Document validity check |

...and more fields for complete data capture.

## Sample Extracted Data

```json
{
  "passport_number": "S0018565",
  "surname": "GANGULI",
  "given_names": "NILENDU",
  "nationality": "INDIAN",
  "sex": "M",
  "date_of_birth": "11/11/1999",
  "place_of_birth": "BIDHANNAGAR, WEST BENGAL",
  "date_of_issue": "16/03/2018",
  "date_of_expiry": "15/03/2028",
  "photo_present": true,
  "signature_present": true,
  "is_document_correct": true
}
```

## API Endpoints Tested

### POST /extract
- Uploads document for classification and extraction
- If no schema exists: generates one and returns status 201
- If schema exists (active): extracts data and returns status 200
- If schema exists (in_review): returns status 202

### GET /schemas
- Retrieves all schemas from database
- Returns schema metadata (ID, type, status, version)

### PUT /schemas/{schema_id}/approve
- Approves a schema in `in_review` status
- Changes status to `active`
- Deprecates any existing active schema

## Troubleshooting

### Service Not Running
```bash
Error: Cannot connect to service
Solution: docker-compose up -d
```

### Test File Not Found
```bash
Error: Test file not found: test/Passport.pdf
Solution: Ensure test/Passport.pdf exists in the directory
```

### Timeout Errors
- Schema generation can take 2-5 minutes
- Script has 5-minute timeout
- Check service logs: `docker logs image_extractor_app`

### Schema Already Exists
If you run the test multiple times, the schema may already be approved:
- The script will detect this and skip to extraction test
- To reset: delete schemas via MongoDB or Mongo Express

## Cleanup

To remove generated schemas and test again:

```bash
# Via Docker
docker exec -it image_extractor_mongodb mongosh -u admin -p password123 --authenticationDatabase admin

# In MongoDB shell
use image_extractor
db.DocumentSchema.deleteMany({ document_type: "passport", country: "IN" })
exit
```

Or use Mongo Express at http://localhost:8081

## Customization

### Test Different Documents

Modify the script to test other document types:

```python
TEST_PDF_PATH = Path("test/your_document.pdf")
```

### Adjust Timeouts

Increase timeout for large documents:

```python
response = requests.post(
    f"{BASE_URL}/extract",
    files=files,
    timeout=600  # 10 minutes
)
```

### Change Base URL

For different environments:

```python
BASE_URL = "http://your-server:8005"
```

## Notes

- First run: Generates schema (takes 2-5 minutes)
- Subsequent runs: Uses existing schema (faster)
- Schema versioning: Each modification creates a new version
- MongoDB stores all schema versions with status tracking

## Related Files

- `main.py`: Main API application
- `src/extractors/classifier.py`: Document classification
- `src/extractors/schema_generator.py`: Schema generation
- `src/extractors/universal.py`: Data extraction
- `src/db/models.py`: MongoDB schema models
- `test/Passport.pdf`: Test document

## Support

For issues:
1. Check service logs: `docker logs image_extractor_app`
2. Check MongoDB logs: `docker logs image_extractor_mongodb`
3. Verify service health: `curl http://localhost:8005/`
4. Check schemas: `curl http://localhost:8005/schemas`
