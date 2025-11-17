# Database Schema Specification for Document Extraction Service

## Table Overview

**Table Name**: `document_schemas`

**Purpose**: Stores document schema definitions for various document types across different countries, including version control and approval workflow status.

---

## Schema Columns Specification

### 1. Primary Key

#### `id` - Unique Schema Identifier

**PostgreSQL Implementation:**
- **Data Type**: `UUID`
- **Constraint**: `PRIMARY KEY`
- **Index**: `CREATE INDEX idx_document_schemas_id ON document_schemas(id)`
- **Default Value**: Auto-generated using `uuid_generate_v4()` or application-level `uuid.uuid4()`
- **Nullable**: `NOT NULL`
- **Description**: Universally unique identifier for each schema record
- **Format**: Standard UUID format (e.g., `550e8400-e29b-41d4-a716-446655440000`)
- **Storage Size**: 16 bytes
- **Notes**: 
  - PostgreSQL native UUID type provides optimal performance
  - Automatically indexed as primary key
  - Case-insensitive for queries

**Oracle Implementation:**
- **Data Type**: `RAW(16)`
- **Constraint**: `PRIMARY KEY`
- **Index**: Automatically created with primary key constraint
- **Default Value**: Generated using `SYS_GUID()` or application-level `uuid.uuid4().bytes`
- **Nullable**: `NOT NULL`
- **Description**: UUID stored as 16-byte raw binary data
- **Storage Size**: 16 bytes
- **Notes**:
  - RAW(16) stores UUID in compact binary format
  - Convert to/from hex for human-readable display: `RAWTOHEX(id)` and `HEXTORAW(uuid_string)`
  - Application layer handles UUID generation and conversion

**SQL Examples:**
```sql
-- PostgreSQL
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
ALTER TABLE document_schemas 
  ALTER COLUMN id SET DEFAULT uuid_generate_v4();

-- Oracle
ALTER TABLE document_schemas 
  MODIFY id DEFAULT SYS_GUID();
```

---

### 2. Document Classification Fields

#### `document_type` - Document Type Classification

- **Data Type**: 
  - PostgreSQL: `VARCHAR(100)`
  - Oracle: `VARCHAR2(100)`
- **Constraint**: `NOT NULL`
- **Index**: `CREATE INDEX idx_document_type ON document_schemas(document_type)`
- **Description**: Classification of the document (e.g., "passport", "drivers_license", "utility_bill")
- **Example Values**: 
  - `"us_passport"`
  - `"us_drivers_license"`
  - `"utility_bill"`
  - `"bank_statement"`
  - `"tax_return"`
- **Validation**: Should match predefined document types in application configuration
- **Character Set**: 
  - PostgreSQL: UTF-8 (default)
  - Oracle: Depends on database character set (typically AL32UTF8)
- **Case Sensitivity**: Store in lowercase with underscores
- **Max Length Rationale**: 100 characters sufficient for descriptive names with country prefix

#### `country` - Country Code

- **Data Type**: 
  - PostgreSQL: `VARCHAR(2)` or `CHAR(2)`
  - Oracle: `VARCHAR2(2)` or `CHAR(2)`
- **Constraint**: `NOT NULL`
- **Index**: Composite index (see below)
- **Description**: ISO 3166-1 alpha-2 country code
- **Format**: Two uppercase letters (e.g., "US", "CA", "GB", "IN")
- **Example Values**: `"US"`, `"GB"`, `"CA"`, `"AU"`, `"IN"`
- **Validation**: Must be valid ISO 3166-1 alpha-2 code
- **Character Set**: ASCII uppercase letters only
- **Notes**: 
  - Use CHAR(2) for fixed-length storage optimization if all values are exactly 2 characters
  - Use VARCHAR(2) if some values might be shorter (though ISO standard is always 2 chars)

**Composite Index:**
```sql
-- Both PostgreSQL and Oracle
CREATE INDEX idx_document_type_country 
ON document_schemas(document_type, country);
```
**Rationale**: Most queries filter by document_type AND country together

---

### 3. Schema Definition

#### `document_schema` - Schema Definition (JSON)

- **Data Type**: 
  - PostgreSQL: `JSONB` (recommended) or `JSON`
  - Oracle: `CLOB` with JSON validation constraint (Oracle 12c+) or `JSON` type (Oracle 21c+)
- **Constraint**: `NOT NULL`
- **Description**: Complete schema definition including field names, types, descriptions, validation rules
- **Storage Considerations**:
  - PostgreSQL JSONB: Binary format, faster queries, supports indexing, slightly larger storage
  - PostgreSQL JSON: Text format, slower queries, smaller storage
  - Oracle CLOB: Character Large Object, up to 4GB
  - Oracle JSON: Native JSON type (21c+), optimized storage and queries
- **Recommended**: 
  - PostgreSQL: Use `JSONB` for better performance
  - Oracle 12c-20c: Use `CLOB` with `IS JSON` constraint
  - Oracle 21c+: Use native `JSON` type

**Schema Structure Example:**
```json
{
  "full_name": {
    "type": "string",
    "description": "Full legal name as appears on document",
    "required": true,
    "max_length": 200,
    "example": "John Michael Doe"
  },
  "date_of_birth": {
    "type": "date",
    "description": "Date of birth in YYYY-MM-DD format",
    "required": true,
    "format": "YYYY-MM-DD",
    "example": "1990-05-15"
  },
  "document_number": {
    "type": "string",
    "description": "Unique document identification number",
    "required": true,
    "pattern": "^[A-Z0-9]{6,20}$",
    "example": "AB1234567"
  },
  "address": {
    "type": "object",
    "description": "Physical address",
    "required": false,
    "properties": {
      "street": {"type": "string"},
      "city": {"type": "string"},
      "state": {"type": "string"},
      "zip_code": {"type": "string"}
    }
  }
}
```

**Storage Size Estimates**:
- Typical schema: 2-10 KB
- Complex schema with many fields: 10-50 KB
- Maximum recommended: 100 KB
- PostgreSQL JSONB overhead: ~15% larger than JSON text
- Oracle CLOB: Stores inline if < 4000 bytes, otherwise in separate segment

**Indexing (Optional for Performance):**
```sql
-- PostgreSQL: Index specific JSON fields
CREATE INDEX idx_schema_fields 
ON document_schemas USING GIN (document_schema);

-- Or index specific paths
CREATE INDEX idx_schema_full_name 
ON document_schemas ((document_schema->>'full_name'));

-- Oracle 12c+: JSON search index
CREATE SEARCH INDEX idx_schema_json 
ON document_schemas (document_schema) 
FOR JSON;
```

**Oracle JSON Validation Constraint:**
```sql
-- Oracle 12c-20c
ALTER TABLE document_schemas 
ADD CONSTRAINT ensure_json 
CHECK (document_schema IS JSON);

-- Oracle 21c+ (native JSON type)
-- No constraint needed, type enforces JSON validity
```

---

### 4. Workflow and Status Fields

#### `status` - Schema Status

- **Data Type**: 
  - PostgreSQL: `VARCHAR(20)` with CHECK constraint or ENUM type
  - Oracle: `VARCHAR2(20)` with CHECK constraint
- **Constraint**: `NOT NULL`
- **Index**: `CREATE INDEX idx_status ON document_schemas(status)`
- **Default Value**: `'in_review'`
- **Allowed Values**:
  - `'active'` - Approved and currently in use for extractions
  - `'in_review'` - Newly generated, awaiting approval
  - `'deprecated'` - Previously active, replaced by newer version
- **Description**: Current approval status of the schema in the workflow
- **Max Length**: 20 characters (sufficient for longest value "deprecated")

**Implementation Options:**

**Option 1 - ENUM Type (PostgreSQL Only):**
```sql
-- PostgreSQL
CREATE TYPE schema_status AS ENUM ('active', 'in_review', 'deprecated');

ALTER TABLE document_schemas 
ALTER COLUMN status TYPE schema_status 
USING status::schema_status;
```
**Advantages**: Type safety, smaller storage, faster queries
**Disadvantages**: Adding new values requires ALTER TYPE

**Option 2 - VARCHAR with CHECK Constraint (Both Databases):**
```sql
-- PostgreSQL
ALTER TABLE document_schemas 
ADD CONSTRAINT check_status 
CHECK (status IN ('active', 'in_review', 'deprecated'));

-- Oracle
ALTER TABLE document_schemas 
ADD CONSTRAINT check_status 
CHECK (status IN ('active', 'in_review', 'deprecated'));
```
**Advantages**: Easier to modify allowed values
**Disadvantages**: Slightly larger storage

**Recommended**: Use ENUM for PostgreSQL, CHECK constraint for Oracle

#### `version` - Schema Version Number

- **Data Type**: 
  - PostgreSQL: `INTEGER`
  - Oracle: `NUMBER(10)` or `INTEGER`
- **Constraint**: `NOT NULL`
- **Default Value**: `1`
- **Range**: 1 to 2,147,483,647 (PostgreSQL INTEGER) or 1 to 9,999,999,999 (Oracle NUMBER(10))
- **Description**: Incremental version number for schema revisions
- **Behavior**:
  - First schema for a document_type/country combination: version = 1
  - Each modification creates new record with version = previous_max + 1
  - Only latest version can be modified
- **Index**: Composite index recommended (see below)

**Versioning Index:**
```sql
-- Both databases
CREATE INDEX idx_type_country_version 
ON document_schemas(document_type, country, version DESC);
```
**Purpose**: Quickly find latest version for a document_type/country

**Query Example:**
```sql
-- Get latest version
SELECT * FROM document_schemas
WHERE document_type = 'us_passport' 
  AND country = 'US'
ORDER BY version DESC
LIMIT 1;  -- PostgreSQL
-- FETCH FIRST 1 ROW ONLY;  -- Oracle 12c+
```

---

### 5. Timestamp Fields

#### `created_at` - Creation Timestamp

- **Data Type**:
  - PostgreSQL: `TIMESTAMP WITH TIME ZONE` (recommended) or `TIMESTAMPTZ`
  - Oracle: `TIMESTAMP WITH TIME ZONE`
- **Constraint**: `NOT NULL`
- **Default Value**: Current timestamp at time of insertion
- **Precision**: Microseconds (6 decimal places)
- **Time Zone**: UTC recommended for consistency
- **Description**: When the schema record was first created
- **Format**: ISO 8601 format in responses (`2025-11-17T10:30:00.123456Z`)

**Default Value Setup:**
```sql
-- PostgreSQL
ALTER TABLE document_schemas 
ALTER COLUMN created_at SET DEFAULT CURRENT_TIMESTAMP;
-- Or for explicit UTC
ALTER COLUMN created_at SET DEFAULT (NOW() AT TIME ZONE 'UTC');

-- Oracle
ALTER TABLE document_schemas 
MODIFY created_at DEFAULT SYSTIMESTAMP AT TIME ZONE 'UTC';
```

**Storage Size**: 
- PostgreSQL: 8 bytes
- Oracle: 13 bytes (TIMESTAMP WITH TIME ZONE)

**Notes**:
- Always store in UTC to avoid time zone confusion
- Application layer converts to user's local time zone for display
- WITH TIME ZONE stores both timestamp and time zone offset

#### `updated_at` - Last Update Timestamp

- **Data Type**:
  - PostgreSQL: `TIMESTAMP WITH TIME ZONE`
  - Oracle: `TIMESTAMP WITH TIME ZONE`
- **Constraint**: `NOT NULL`
- **Default Value**: Current timestamp at time of insertion
- **Update Behavior**: Automatically updated on any record modification
- **Precision**: Microseconds (6 decimal places)
- **Time Zone**: UTC recommended
- **Description**: When the schema record was last modified (status change, etc.)

**Auto-Update Trigger (PostgreSQL):**
```sql
-- Create function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger
CREATE TRIGGER update_document_schemas_updated_at 
BEFORE UPDATE ON document_schemas
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
```

**Auto-Update Trigger (Oracle):**
```sql
CREATE OR REPLACE TRIGGER trg_document_schemas_updated_at
BEFORE UPDATE ON document_schemas
FOR EACH ROW
BEGIN
    :NEW.updated_at := SYSTIMESTAMP AT TIME ZONE 'UTC';
END;
/
```

---

## Complete Table Creation Scripts

### PostgreSQL Table Creation

```sql
-- Create UUID extension if not exists
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create ENUM type for status
CREATE TYPE schema_status AS ENUM ('active', 'in_review', 'deprecated');

-- Create table
CREATE TABLE document_schemas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_type VARCHAR(100) NOT NULL,
    country VARCHAR(2) NOT NULL,
    document_schema JSONB NOT NULL,
    status schema_status NOT NULL DEFAULT 'in_review',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    version INTEGER NOT NULL DEFAULT 1,
    
    -- Constraints
    CONSTRAINT check_country_format CHECK (country ~ '^[A-Z]{2}$'),
    CONSTRAINT check_version_positive CHECK (version > 0)
);

-- Create indexes
CREATE INDEX idx_document_type ON document_schemas(document_type);
CREATE INDEX idx_document_type_country ON document_schemas(document_type, country);
CREATE INDEX idx_status ON document_schemas(status);
CREATE INDEX idx_type_country_version ON document_schemas(document_type, country, version DESC);
CREATE INDEX idx_created_at ON document_schemas(created_at);

-- Optional: GIN index for JSONB queries
CREATE INDEX idx_schema_fields ON document_schemas USING GIN (document_schema);

-- Create trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_document_schemas_updated_at 
BEFORE UPDATE ON document_schemas
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Add comments for documentation
COMMENT ON TABLE document_schemas IS 'Stores document extraction schema definitions with version control';
COMMENT ON COLUMN document_schemas.id IS 'Unique UUID identifier for schema';
COMMENT ON COLUMN document_schemas.document_type IS 'Type of document (e.g., us_passport, drivers_license)';
COMMENT ON COLUMN document_schemas.country IS 'ISO 3166-1 alpha-2 country code';
COMMENT ON COLUMN document_schemas.document_schema IS 'Complete JSON schema definition with field specifications';
COMMENT ON COLUMN document_schemas.status IS 'Workflow status: active, in_review, or deprecated';
COMMENT ON COLUMN document_schemas.version IS 'Version number for schema revisions';
COMMENT ON COLUMN document_schemas.created_at IS 'Timestamp when schema was created (UTC)';
COMMENT ON COLUMN document_schemas.updated_at IS 'Timestamp when schema was last modified (UTC)';
```

### Oracle Table Creation

```sql
-- Create table
CREATE TABLE document_schemas (
    id RAW(16) DEFAULT SYS_GUID() PRIMARY KEY,
    document_type VARCHAR2(100) NOT NULL,
    country VARCHAR2(2) NOT NULL,
    document_schema CLOB NOT NULL,
    status VARCHAR2(20) DEFAULT 'in_review' NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP AT TIME ZONE 'UTC' NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP AT TIME ZONE 'UTC' NOT NULL,
    version NUMBER(10) DEFAULT 1 NOT NULL,
    
    -- Constraints
    CONSTRAINT check_status CHECK (status IN ('active', 'in_review', 'deprecated')),
    CONSTRAINT check_country_format CHECK (REGEXP_LIKE(country, '^[A-Z]{2}$')),
    CONSTRAINT check_version_positive CHECK (version > 0),
    CONSTRAINT ensure_json CHECK (document_schema IS JSON)
);

-- Create indexes
CREATE INDEX idx_document_type ON document_schemas(document_type);
CREATE INDEX idx_document_type_country ON document_schemas(document_type, country);
CREATE INDEX idx_status ON document_schemas(status);
CREATE INDEX idx_type_country_version ON document_schemas(document_type, country, version DESC);
CREATE INDEX idx_created_at ON document_schemas(created_at);

-- Optional: JSON search index for better query performance
CREATE SEARCH INDEX idx_schema_json ON document_schemas(document_schema) FOR JSON;

-- Create trigger for updated_at
CREATE OR REPLACE TRIGGER trg_document_schemas_updated_at
BEFORE UPDATE ON document_schemas
FOR EACH ROW
BEGIN
    :NEW.updated_at := SYSTIMESTAMP AT TIME ZONE 'UTC';
END;
/

-- Add comments for documentation
COMMENT ON TABLE document_schemas IS 'Stores document extraction schema definitions with version control';
COMMENT ON COLUMN document_schemas.id IS 'Unique UUID identifier stored as RAW(16)';
COMMENT ON COLUMN document_schemas.document_type IS 'Type of document (e.g., us_passport, drivers_license)';
COMMENT ON COLUMN document_schemas.country IS 'ISO 3166-1 alpha-2 country code';
COMMENT ON COLUMN document_schemas.document_schema IS 'Complete JSON schema definition stored as CLOB';
COMMENT ON COLUMN document_schemas.status IS 'Workflow status: active, in_review, or deprecated';
COMMENT ON COLUMN document_schemas.version IS 'Version number for schema revisions';
COMMENT ON COLUMN document_schemas.created_at IS 'Timestamp when schema was created (UTC)';
COMMENT ON COLUMN document_schemas.updated_at IS 'Timestamp when schema was last modified (UTC)';
```

---

## Storage and Performance Considerations

### Storage Size Estimates

**Per Record:**
- UUID/RAW(16): 16 bytes
- document_type (avg): 30 bytes
- country: 2 bytes
- document_schema (avg): 5 KB
- status: 20 bytes
- created_at: 8-13 bytes
- updated_at: 8-13 bytes
- version: 4 bytes
- **Total per record (estimate)**: ~5 KB + overhead

**Database Overhead:**
- PostgreSQL: ~24 bytes per row (tuple header)
- Oracle: ~20 bytes per row + 3 bytes per column

**Storage Growth Estimates:**
- 100 schemas: ~500 KB
- 1,000 schemas: ~5 MB
- 10,000 schemas: ~50 MB
- 100,000 schemas: ~500 MB

**Recommendation**: Plan for 1 GB of storage initially, which provides capacity for ~200,000 schemas with growth buffer.

### Index Storage

Each index adds overhead:
- PostgreSQL B-tree index: ~50-60% of indexed column size
- Oracle B-tree index: ~50-70% of indexed column size
- GIN/JSON index: Can be 2-3x the data size for JSONB columns

**Total index storage estimate**: ~2-3 MB per 10,000 records

### Query Performance

**Expected Query Performance (with proper indexes):**

1. **Find active schema by document_type and country:**
   - Target: < 5ms
   - Uses: `idx_document_type_country`

2. **Get latest version:**
   - Target: < 10ms
   - Uses: `idx_type_country_version`

3. **List all schemas (paginated):**
   - Target: < 50ms for 100 records
   - Uses: Sequential scan or `idx_status` if filtered

4. **Update schema status:**
   - Target: < 10ms
   - Uses: Primary key index

5. **JSON field queries (PostgreSQL with GIN):**
   - Target: < 20ms
   - Uses: `idx_schema_fields`

**Optimization Tips:**
- Keep indexes on high-cardinality columns (document_type, country, version)
- Use composite indexes for common query patterns
- Regularly ANALYZE/UPDATE STATISTICS
- Monitor query plans for sequential scans on large tables

---

## Data Integrity Rules

### Uniqueness Constraints

**Business Rule**: Only one ACTIVE schema per document_type/country combination

**Implementation Options:**

**Option 1 - Partial Unique Index (PostgreSQL):**
```sql
CREATE UNIQUE INDEX idx_unique_active_schema 
ON document_schemas(document_type, country) 
WHERE status = 'active';
```

**Option 2 - Function-Based Unique Index (Oracle):**
```sql
CREATE UNIQUE INDEX idx_unique_active_schema 
ON document_schemas(
    CASE WHEN status = 'active' 
    THEN document_type || '~' || country 
    END
);
```

**Option 3 - Application-Level Enforcement:**
- Check for existing active schema before approving new one
- Automatically deprecate old active schema when approving new one
- Current implementation uses this approach

### Referential Integrity

**Current Design**: No foreign keys (standalone table)

**Future Considerations** (if adding related tables):
- `extraction_results` table could reference `document_schemas.id`
- `schema_modification_history` table could track changes
- Use `ON DELETE CASCADE` or `ON DELETE RESTRICT` based on business needs

### Data Validation

**Application-Level Validations:**
- document_type matches supported types list
- country is valid ISO 3166-1 alpha-2 code
- document_schema is valid JSON with required fields
- version increments properly
- Status transitions follow workflow rules (in_review → active/deprecated)

**Database-Level Validations:**
- CHECK constraints on status values
- CHECK constraint on country format (2 uppercase letters)
- CHECK constraint on version > 0
- NOT NULL constraints on all required fields
- JSON validation constraint (Oracle)

---

## Backup and Maintenance

### Backup Strategy

**PostgreSQL:**
```bash
# Full database backup
pg_dump -h localhost -U postgres -d document_extraction > backup.sql

# Table-only backup
pg_dump -h localhost -U postgres -d document_extraction -t document_schemas > schemas_backup.sql

# Binary backup (faster, smaller)
pg_dump -h localhost -U postgres -d document_extraction -Fc -f backup.dump
```

**Oracle:**
```sql
-- Export table
expdp system/password DIRECTORY=backup_dir TABLES=document_schemas DUMPFILE=schemas.dmp

-- Or using SQL*Plus
CREATE TABLE document_schemas_backup AS SELECT * FROM document_schemas;
```

**Backup Frequency:**
- Full backup: Daily
- Incremental backup: Every 6 hours (if supported)
- Point-in-time recovery: WAL archiving (PostgreSQL) or Archive Log (Oracle)

### Maintenance Tasks

**PostgreSQL:**
```sql
-- Vacuum and analyze (weekly)
VACUUM ANALYZE document_schemas;

-- Reindex (monthly or after bulk operations)
REINDEX TABLE document_schemas;

-- Check table bloat
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE tablename = 'document_schemas';
```

**Oracle:**
```sql
-- Gather statistics (weekly)
EXEC DBMS_STATS.GATHER_TABLE_STATS('SCHEMA_NAME', 'DOCUMENT_SCHEMAS');

-- Rebuild indexes (monthly)
ALTER INDEX idx_document_type REBUILD ONLINE;
ALTER INDEX idx_document_type_country REBUILD ONLINE;

-- Check table size
SELECT segment_name, bytes/1024/1024 as size_mb
FROM user_segments
WHERE segment_name = 'DOCUMENT_SCHEMAS';
```

### Monitoring Queries

**PostgreSQL:**
```sql
-- Row count by status
SELECT status, COUNT(*) FROM document_schemas GROUP BY status;

-- Latest schema versions
SELECT document_type, country, MAX(version) as latest_version
FROM document_schemas
GROUP BY document_type, country;

-- Growth over time
SELECT DATE(created_at), COUNT(*) 
FROM document_schemas 
GROUP BY DATE(created_at) 
ORDER BY DATE(created_at) DESC 
LIMIT 30;

-- Index usage
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read
FROM pg_stat_user_indexes
WHERE tablename = 'document_schemas';
```

**Oracle:**
```sql
-- Row count by status
SELECT status, COUNT(*) FROM document_schemas GROUP BY status;

-- Latest schema versions
SELECT document_type, country, MAX(version) as latest_version
FROM document_schemas
GROUP BY document_type, country;

-- Growth over time
SELECT TRUNC(created_at), COUNT(*) 
FROM document_schemas 
GROUP BY TRUNC(created_at) 
ORDER BY TRUNC(created_at) DESC 
FETCH FIRST 30 ROWS ONLY;

-- Index usage
SELECT index_name, num_rows, distinct_keys, leaf_blocks
FROM user_indexes
WHERE table_name = 'DOCUMENT_SCHEMAS';
```

---

## Security Considerations

### Access Control

**PostgreSQL:**
```sql
-- Create roles
CREATE ROLE doc_extraction_admin;
CREATE ROLE doc_extraction_app;
CREATE ROLE doc_extraction_readonly;

-- Grant privileges
GRANT ALL ON document_schemas TO doc_extraction_admin;
GRANT SELECT, INSERT, UPDATE ON document_schemas TO doc_extraction_app;
GRANT SELECT ON document_schemas TO doc_extraction_readonly;

-- Row-level security (if needed)
ALTER TABLE document_schemas ENABLE ROW LEVEL SECURITY;
CREATE POLICY app_access ON document_schemas FOR ALL TO doc_extraction_app USING (true);
```

**Oracle:**
```sql
-- Create users/roles
CREATE ROLE doc_extraction_admin;
CREATE ROLE doc_extraction_app;
CREATE ROLE doc_extraction_readonly;

-- Grant privileges
GRANT ALL ON document_schemas TO doc_extraction_admin;
GRANT SELECT, INSERT, UPDATE ON document_schemas TO doc_extraction_app;
GRANT SELECT ON document_schemas TO doc_extraction_readonly;

-- Virtual Private Database (VPD) for row-level security (if needed)
-- Implementation depends on specific requirements
```

### Data Encryption

**At Rest:**
- PostgreSQL: Use Transparent Data Encryption (TDE) extensions or OS-level encryption
- Oracle: Use Transparent Data Encryption (TDE) feature

**In Transit:**
- PostgreSQL: SSL/TLS connections (require ssl = on in postgresql.conf)
- Oracle: SQL*Net encryption (SQLNET.ENCRYPTION_SERVER = REQUIRED)

**Sensitive Data:**
- document_schema CLOB/JSONB may contain PII in examples
- Consider encrypting sensitive fields at application level
- Implement field-level encryption for highly sensitive data

### Audit Logging

**PostgreSQL:**
```sql
-- Enable pgaudit extension
CREATE EXTENSION pgaudit;

-- Configure auditing
SET pgaudit.log = 'write, ddl';
SET pgaudit.log_relation = on;
```

**Oracle:**
```sql
-- Enable unified auditing
AUDIT SELECT, INSERT, UPDATE, DELETE ON document_schemas BY ACCESS;

-- Create audit policy
CREATE AUDIT POLICY schema_access_policy
ACTIONS SELECT, INSERT, UPDATE, DELETE ON document_schemas;

AUDIT POLICY schema_access_policy;
```

---

## Migration and Versioning

### Schema Version History

Track database schema changes separate from document schema versions:

```sql
-- Create migration tracking table
CREATE TABLE schema_migrations (
    version INTEGER PRIMARY KEY,
    description VARCHAR(200),
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Record each migration
INSERT INTO schema_migrations (version, description)
VALUES (1, 'Initial document_schemas table creation');

INSERT INTO schema_migrations (version, description)
VALUES (2, 'Added UUID support and indexes');
```

### Upgrade Path (Integer to UUID)

If migrating from integer IDs:

**PostgreSQL:**
```sql
-- Step 1: Add new UUID column
ALTER TABLE document_schemas ADD COLUMN new_id UUID DEFAULT uuid_generate_v4();

-- Step 2: Generate UUIDs for existing rows
UPDATE document_schemas SET new_id = uuid_generate_v4() WHERE new_id IS NULL;

-- Step 3: Create new indexes
CREATE UNIQUE INDEX idx_new_id ON document_schemas(new_id);

-- Step 4: Drop old primary key and rename
ALTER TABLE document_schemas DROP CONSTRAINT document_schemas_pkey;
ALTER TABLE document_schemas DROP COLUMN id;
ALTER TABLE document_schemas RENAME COLUMN new_id TO id;
ALTER TABLE document_schemas ADD PRIMARY KEY (id);

-- Step 5: Recreate dependent indexes
-- (Already done in step 3)
```

**Oracle:**
```sql
-- Step 1: Add new RAW column
ALTER TABLE document_schemas ADD new_id RAW(16) DEFAULT SYS_GUID();

-- Step 2: Generate UUIDs
UPDATE document_schemas SET new_id = SYS_GUID() WHERE new_id IS NULL;

-- Step 3: Drop old PK constraint
ALTER TABLE document_schemas DROP PRIMARY KEY;

-- Step 4: Drop old ID column
ALTER TABLE document_schemas DROP COLUMN id;

-- Step 5: Rename new column
ALTER TABLE document_schemas RENAME COLUMN new_id TO id;

-- Step 6: Add primary key
ALTER TABLE document_schemas ADD PRIMARY KEY (id);
```

---

## Testing and Validation

### Data Validation Queries

```sql
-- Check for NULL values
SELECT COUNT(*) FROM document_schemas WHERE id IS NULL;
SELECT COUNT(*) FROM document_schemas WHERE document_type IS NULL;
SELECT COUNT(*) FROM document_schemas WHERE country IS NULL;
SELECT COUNT(*) FROM document_schemas WHERE document_schema IS NULL;

-- Check for invalid status values
SELECT COUNT(*) FROM document_schemas 
WHERE status NOT IN ('active', 'in_review', 'deprecated');

-- Check for invalid country codes (not 2 uppercase letters)
SELECT country, COUNT(*) FROM document_schemas 
WHERE country !~ '^[A-Z]{2}$'  -- PostgreSQL
-- WHERE NOT REGEXP_LIKE(country, '^[A-Z]{2}$')  -- Oracle
GROUP BY country;

-- Check for version gaps
WITH version_check AS (
    SELECT document_type, country, version,
           LAG(version) OVER (PARTITION BY document_type, country ORDER BY version) as prev_version
    FROM document_schemas
)
SELECT * FROM version_check 
WHERE version - prev_version > 1;

-- Check for multiple active schemas (should be 0)
SELECT document_type, country, COUNT(*) 
FROM document_schemas 
WHERE status = 'active'
GROUP BY document_type, country
HAVING COUNT(*) > 1;
```

### Performance Testing

```sql
-- Test index usage
EXPLAIN ANALYZE 
SELECT * FROM document_schemas 
WHERE document_type = 'us_passport' AND country = 'US' AND status = 'active';

-- Test JSON queries (PostgreSQL)
EXPLAIN ANALYZE
SELECT * FROM document_schemas 
WHERE document_schema @> '{"full_name": {"type": "string"}}';

-- Test version ordering
EXPLAIN ANALYZE
SELECT * FROM document_schemas 
WHERE document_type = 'us_passport' AND country = 'US'
ORDER BY version DESC
LIMIT 1;
```

---

## Quick Reference

### Column Summary Table

| Column | PostgreSQL Type | Oracle Type | Length | Nullable | Default | Indexed |
|--------|----------------|-------------|--------|----------|---------|---------|
| id | UUID | RAW(16) | 16 bytes | NOT NULL | uuid_generate_v4() / SYS_GUID() | PRIMARY KEY |
| document_type | VARCHAR(100) | VARCHAR2(100) | 100 chars | NOT NULL | - | Yes (composite) |
| country | VARCHAR(2) | VARCHAR2(2) | 2 chars | NOT NULL | - | Yes (composite) |
| document_schema | JSONB | CLOB | Variable | NOT NULL | - | Optional (GIN/JSON) |
| status | schema_status ENUM / VARCHAR(20) | VARCHAR2(20) | 20 chars | NOT NULL | 'in_review' | Yes |
| created_at | TIMESTAMP WITH TIME ZONE | TIMESTAMP WITH TIME ZONE | 8-13 bytes | NOT NULL | CURRENT_TIMESTAMP | Yes |
| updated_at | TIMESTAMP WITH TIME ZONE | TIMESTAMP WITH TIME ZONE | 8-13 bytes | NOT NULL | CURRENT_TIMESTAMP | No |
| version | INTEGER | NUMBER(10) | 4 bytes | NOT NULL | 1 | Yes (composite) |

### Index Summary

| Index Name | Columns | Type | Purpose |
|------------|---------|------|---------|
| PRIMARY KEY | id | B-tree | Unique identifier lookup |
| idx_document_type | document_type | B-tree | Filter by document type |
| idx_document_type_country | document_type, country | B-tree | Find schemas by type and country |
| idx_status | status | B-tree | Filter by workflow status |
| idx_type_country_version | document_type, country, version DESC | B-tree | Get latest version |
| idx_created_at | created_at | B-tree | Time-based queries |
| idx_schema_fields | document_schema | GIN/JSON Search | JSON field queries (optional) |
| idx_unique_active_schema | document_type, country WHERE status='active' | Unique (partial/functional) | Ensure single active schema |

---

## Contacts and Support

For questions or issues related to this database schema:
- **Database Team**: [database-team@company.com]
- **Application Team**: [doc-extraction-team@company.com]
- **Documentation**: See `DATABASE_SCHEMA_SPECIFICATION.md`
- **Code Repository**: https://github.com/NilenduGanguli/ai_project_25

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-17  
**Author**: AI Project Team  
**Status**: Production Ready
