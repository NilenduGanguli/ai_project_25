# Testing UUID Implementation

## Quick Test Commands

### PostgreSQL Module (document-extraction)

#### 1. Start the service
```bash
cd document-extraction
docker-compose up -d
```

#### 2. Check health
```bash
curl http://localhost:8005/
```

#### 3. Test schema creation (upload a document)
```bash
curl -X POST http://localhost:8005/extract \
  -F "document=@/path/to/test/document.pdf"
```

Expected response should include:
```json
{
  "schema_id": "550e8400-e29b-41d4-a716-446655440000",  // UUID format
  "status": "schema_generated"
}
```

#### 4. Test GET /schemas
```bash
curl http://localhost:8005/schemas
```

Verify response includes:
- `id` field with UUID string
- Complete `schema` object for each entry

#### 5. Test schema approval (use UUID from step 3)
```bash
curl -X PUT http://localhost:8005/schemas/550e8400-e29b-41d4-a716-446655440000/approve
```

Should return:
```json
{
  "schema": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "schema_id": "...",
    "schema": { ... },  // Complete schema definition
    "created_at": "...",
    "updated_at": "..."
  }
}
```

#### 6. Test extraction with active schema
```bash
curl -X POST http://localhost:8005/extract \
  -F "document=@/path/to/test/document.pdf"
```

Should return:
```json
{
  "status": "extracted",
  "data": { ... },
  "schema_used": {
    "schema_id": "550e8400-e29b-41d4-a716-446655440000",
    "schema": { ... },  // Complete schema
    "version": 1,
    "status": "active"
  }
}
```

---

### Oracle Module (document-extraction-oracle)

#### 1. Set environment variables
```bash
cd document-extraction-oracle
export ORACLE_USER=your_username
export ORACLE_PASSWORD=your_password
export ORACLE_DSN=host:port/service_name
```

#### 2. Start the service
```bash
docker-compose up -d
```

#### 3. Check logs for Oracle connection
```bash
docker-compose logs -f document-extraction-oracle
```

Look for:
- "Connected to Oracle database successfully"
- "Tables created successfully"
- UUID generation working

#### 4. Test schema creation
```bash
curl -X POST http://localhost:8006/extract \
  -F "document=@/path/to/test/document.pdf"
```

Verify:
- `schema_id` is UUID string (converted from RAW(16) bytes)
- Schema saved to Oracle database

#### 5. Verify UUID storage in Oracle
Connect to Oracle and run:
```sql
SELECT 
  RAWTOHEX(id) as uuid_hex,
  document_type,
  country,
  status,
  version
FROM document_schemas;
```

UUID should be stored as 16-byte RAW value.

#### 6. Test all CRUD operations
Same curl commands as PostgreSQL, but use port 8006:
- GET http://localhost:8006/schemas
- PUT http://localhost:8006/schemas/{uuid}/approve
- PUT http://localhost:8006/schemas/{uuid}/modify
- DELETE http://localhost:8006/schemas/{uuid}

---

## Validation Checklist

### PostgreSQL Module
- [ ] UUID auto-generated on schema creation
- [ ] UUID format: 8-4-4-4-12 (e.g., 550e8400-e29b-41d4-a716-446655440000)
- [ ] All endpoints accept UUID strings as schema_id parameter
- [ ] All responses include schema_id as UUID string
- [ ] Complete schema definition in all responses
- [ ] No integer ID references remain

### Oracle Module
- [ ] UUID bytes stored in RAW(16) column
- [ ] UUID to bytes conversion working on save
- [ ] Bytes to UUID conversion working on read
- [ ] All responses return UUID strings (not bytes)
- [ ] Synchronous query helpers working
- [ ] No async PostgreSQL session patterns
- [ ] Complete schema information in responses
- [ ] UUID string parsing working in all endpoints

### Response Structure Validation

All endpoints should return schema info with:
```json
{
  "schema_id": "uuid-string",
  "document_type": "string",
  "country": "string",
  "version": 1,
  "status": "active|in_review|deprecated",
  "created_at": "ISO-8601-timestamp",
  "updated_at": "ISO-8601-timestamp",
  "schema": {
    "field1": { "type": "...", "description": "..." },
    "field2": { "type": "...", "description": "..." }
  }
}
```

---

## Common Issues and Solutions

### Issue: "UUID is not a valid UUID string"
**Solution**: Ensure schema_id parameter is a valid UUID format. Check frontend/client code.

### Issue: Oracle "ORA-01722: invalid number"
**Solution**: Make sure UUID is converted to bytes before Oracle query. Check queries.py.

### Issue: PostgreSQL "column 'id' is of type uuid but expression is of type integer"
**Solution**: Database migration needed. Run migration script to convert integer IDs to UUIDs.

### Issue: "TypeError: Object of type bytes is not JSON serializable"
**Solution**: Oracle RAW(16) bytes must be converted to UUID string before JSON response. Check all response builders.

### Issue: Frontend shows "[object Object]" for schema_id
**Solution**: Frontend expects string, not object. Ensure str(uuid) conversion in backend.

---

## Performance Testing

### UUID Index Performance
```sql
-- PostgreSQL
EXPLAIN ANALYZE 
SELECT * FROM document_schemas WHERE id = '550e8400-e29b-41d4-a716-446655440000';

-- Oracle
SET AUTOTRACE ON
SELECT * FROM document_schemas WHERE id = HEXTORAW('550e8400e29b41d4a716446655440000');
```

Should use index scan, not sequential/full table scan.

### Bulk Insert Performance
Test schema creation with multiple documents to verify UUID generation doesn't slow down inserts.

---

## Rollback Plan (if needed)

If UUID implementation causes issues:

1. Keep UUID branch for future
2. Revert to integer ID version
3. Document specific issues encountered
4. Plan fixes for next attempt

Rollback commands:
```bash
cd document-extraction
git checkout <previous-commit-hash>
docker-compose down -v
docker-compose up -d --build
```

Same for Oracle module.
