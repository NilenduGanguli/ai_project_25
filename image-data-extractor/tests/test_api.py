"""
Integration tests for API endpoints
Tests complete API workflows and endpoint behavior
"""
import pytest
import json
from io import BytesIO
from unittest.mock import patch, AsyncMock

from src.db.models import DocumentSchema, SchemaStatus


@pytest.mark.integration
@pytest.mark.asyncio
class TestHealthCheckEndpoint:
    """Tests for health check endpoint"""
    
    def test_health_check_success(self, client):
        """Test health check returns 200"""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.requires_db
class TestExtractEndpoint:
    """Tests for document extraction endpoint"""
    
    async def test_extract_generates_new_schema(
        self,
        client,
        clean_db,
        mock_pdf_content,
        mock_llm_classification,
        mock_llm_schema_generation
    ):
        """Test extraction generates schema when none exists"""
        files = {"document": ("test.pdf", BytesIO(mock_pdf_content), "application/pdf")}
        
        response = client.post("/extract", files=files)
        
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "schema_generated"
        assert "schema_id" in data
        assert data["classification"]["document_type"] == "passport"
        
        # Verify schema was saved
        schemas = await DocumentSchema.find_all().to_list()
        assert len(schemas) == 1
        assert schemas[0].status == SchemaStatus.IN_REVIEW
    
    async def test_extract_with_active_schema(
        self,
        client,
        clean_db,
        sample_document_schema,
        mock_pdf_content,
        mock_llm_classification,
        mock_llm_extraction
    ):
        """Test extraction uses existing active schema"""
        files = {"document": ("test.pdf", BytesIO(mock_pdf_content), "application/pdf")}
        
        response = client.post("/extract", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "extracted"
        assert "data" in data
        assert data["schema_used"]["document_type"] == "passport"
        assert data["schema_used"]["version"] == 1
    
    async def test_extract_with_in_review_schema(
        self,
        client,
        clean_db,
        sample_passport_schema,
        mock_pdf_content,
        mock_llm_classification
    ):
        """Test extraction with schema in review status"""
        # Create schema in review
        schema = DocumentSchema(
            document_type="passport",
            country="IN",
            document_schema=sample_passport_schema,
            status=SchemaStatus.IN_REVIEW,
            version=1
        )
        await schema.insert()
        
        files = {"document": ("test.pdf", BytesIO(mock_pdf_content), "application/pdf")}
        
        response = client.post("/extract", files=files)
        
        assert response.status_code == 202
        data = response.json()
        assert data["status"] == "pending_review"
        assert "schema_id" in data
    
    def test_extract_invalid_file_type(self, client):
        """Test extraction with invalid file type"""
        files = {"document": ("test.txt", BytesIO(b"text content"), "text/plain")}
        
        response = client.post("/extract", files=files)
        
        assert response.status_code == 400
        assert "must be JPEG, PNG, or PDF" in response.json()["detail"]
    
    def test_extract_no_file(self, client):
        """Test extraction without uploading file"""
        response = client.post("/extract")
        
        assert response.status_code == 422  # FastAPI validation error
    
    async def test_extract_low_confidence_classification(
        self,
        client,
        clean_db,
        mock_pdf_content
    ):
        """Test extraction with low confidence classification"""
        with patch('src.extractors.classifier.get_llm') as mock_llm:
            mock_instance = AsyncMock()
            from src.db.models import DocumentTypeClassification
            mock_instance.ainvoke.return_value = DocumentTypeClassification(
                document_type="passport",
                confidence=0.60,  # Below threshold
                country="IN",
                alternative_types=[{"driver_license": 0.35}]
            )
            mock_llm.return_value = mock_instance
            
            files = {"document": ("test.pdf", BytesIO(mock_pdf_content), "application/pdf")}
            
            response = client.post("/extract", files=files)
            
            assert response.status_code == 422
            data = response.json()
            assert data["status"] == "classification_uncertain"
            assert "alternative_types" in data


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.requires_db
class TestSchemasEndpoint:
    """Tests for schemas retrieval endpoint"""
    
    async def test_get_all_schemas_empty(self, client, clean_db):
        """Test getting schemas when database is empty"""
        response = client.get("/schemas")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 0
        assert data["schemas"] == []
    
    async def test_get_all_schemas_with_data(
        self,
        client,
        clean_db,
        sample_document_schema
    ):
        """Test getting schemas with existing data"""
        # Create additional schema
        schema2 = DocumentSchema(
            document_type="pan_card",
            country="IN",
            document_schema={"test": "field"},
            status=SchemaStatus.ACTIVE,
            version=1
        )
        await schema2.insert()
        
        response = client.get("/schemas")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 2
        assert len(data["schemas"]) == 2
        
        # Verify schema structure
        schema = data["schemas"][0]
        assert "id" in schema
        assert "document_type" in schema
        assert "country" in schema
        assert "status" in schema
        assert "version" in schema
        assert "created_at" in schema
        assert "schema" in schema
    
    async def test_get_schemas_returns_all_statuses(self, client, clean_db):
        """Test that all schema statuses are returned"""
        statuses = [SchemaStatus.ACTIVE, SchemaStatus.IN_REVIEW, SchemaStatus.DEPRECATED]
        
        for i, status in enumerate(statuses):
            schema = DocumentSchema(
                document_type=f"doc_{i}",
                country="IN",
                document_schema={"test": "field"},
                status=status,
                version=1
            )
            await schema.insert()
        
        response = client.get("/schemas")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 3
        
        returned_statuses = {s["status"] for s in data["schemas"]}
        assert len(returned_statuses) == 3


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.requires_db
class TestApproveSchemaEndpoint:
    """Tests for schema approval endpoint"""
    
    async def test_approve_schema_success(self, client, clean_db, sample_passport_schema):
        """Test successfully approving a schema"""
        # Create schema in review
        schema = DocumentSchema(
            document_type="passport",
            country="IN",
            document_schema=sample_passport_schema,
            status=SchemaStatus.IN_REVIEW,
            version=1
        )
        await schema.insert()
        schema_id = str(schema.id)
        
        response = client.put(f"/schemas/{schema_id}/approve")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Schema approved successfully"
        assert data["schema"]["status"] == SchemaStatus.ACTIVE
        
        # Verify in database
        updated_schema = await DocumentSchema.get(schema_id)
        assert updated_schema.status == SchemaStatus.ACTIVE
    
    async def test_approve_deprecates_existing_active(
        self,
        client,
        clean_db,
        sample_passport_schema
    ):
        """Test that approving new schema deprecates old active one"""
        # Create existing active schema
        old_schema = DocumentSchema(
            document_type="passport",
            country="IN",
            document_schema=sample_passport_schema,
            status=SchemaStatus.ACTIVE,
            version=1
        )
        await old_schema.insert()
        
        # Create new schema in review
        new_schema = DocumentSchema(
            document_type="passport",
            country="IN",
            document_schema=sample_passport_schema,
            status=SchemaStatus.IN_REVIEW,
            version=2
        )
        await new_schema.insert()
        new_schema_id = str(new_schema.id)
        
        response = client.put(f"/schemas/{new_schema_id}/approve")
        
        assert response.status_code == 200
        data = response.json()
        assert data["deprecated_schema"] is not None
        assert data["deprecated_schema"]["version"] == 1
        
        # Verify old schema is deprecated
        old_updated = await DocumentSchema.get(str(old_schema.id))
        assert old_updated.status == SchemaStatus.DEPRECATED
    
    async def test_approve_nonexistent_schema(self, client, clean_db):
        """Test approving non-existent schema"""
        fake_id = "507f1f77bcf86cd799439011"  # Valid ObjectId format
        
        response = client.put(f"/schemas/{fake_id}/approve")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    async def test_approve_already_active_schema(
        self,
        client,
        clean_db,
        sample_document_schema
    ):
        """Test approving an already active schema"""
        schema_id = str(sample_document_schema.id)
        
        response = client.put(f"/schemas/{schema_id}/approve")
        
        assert response.status_code == 400
        assert "IN_REVIEW status" in response.json()["detail"]
    
    def test_approve_invalid_schema_id(self, client):
        """Test approving with invalid schema ID format"""
        response = client.put("/schemas/invalid_id/approve")
        
        assert response.status_code in [400, 500]


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.requires_db
class TestModifySchemaEndpoint:
    """Tests for schema modification endpoint"""
    
    async def test_modify_schema_success(
        self,
        client,
        clean_db,
        sample_document_schema,
        sample_modification_request
    ):
        """Test successfully modifying a schema"""
        schema_id = str(sample_document_schema.id)
        
        response = client.put(
            f"/schemas/{schema_id}/modify",
            json=sample_modification_request
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "schema_modified"
        assert "new_schema_info" in data
        assert data["new_schema_info"]["version"] == 2
        
        # Verify old schema is deprecated
        old_schema = await DocumentSchema.get(schema_id)
        assert old_schema.status == SchemaStatus.DEPRECATED
        
        # Verify new schema exists
        new_schema_id = data["new_schema_info"]["id"]
        new_schema = await DocumentSchema.get(new_schema_id)
        assert new_schema.status == SchemaStatus.IN_REVIEW
        assert new_schema.version == 2
    
    async def test_modify_schema_no_changes(
        self,
        client,
        clean_db,
        sample_document_schema
    ):
        """Test modifying schema with no actual changes"""
        schema_id = str(sample_document_schema.id)
        
        # Request with no changes
        request = {
            "modifications": {},
            "change_description": "No changes"
        }
        
        response = client.put(f"/schemas/{schema_id}/modify", json=request)
        
        # Should detect no changes
        assert response.status_code in [200, 400]
    
    async def test_modify_only_latest_version(
        self,
        client,
        clean_db,
        sample_passport_schema
    ):
        """Test that only the latest version can be modified"""
        # Create version 1 (deprecated)
        old_schema = DocumentSchema(
            document_type="passport",
            country="IN",
            document_schema=sample_passport_schema,
            status=SchemaStatus.DEPRECATED,
            version=1
        )
        await old_schema.insert()
        old_schema_id = str(old_schema.id)
        
        # Create version 2 (active/latest)
        latest_schema = DocumentSchema(
            document_type="passport",
            country="IN",
            document_schema=sample_passport_schema,
            status=SchemaStatus.ACTIVE,
            version=2
        )
        await latest_schema.insert()
        
        # Try to modify old version
        request = {
            "modifications": {"new_field": {"type": "string"}},
            "change_description": "Test"
        }
        
        response = client.put(f"/schemas/{old_schema_id}/modify", json=request)
        
        assert response.status_code == 400
        assert "only the latest version" in response.json()["detail"]
    
    async def test_modify_invalid_modifications(
        self,
        client,
        clean_db,
        sample_document_schema
    ):
        """Test modifying schema with invalid modifications"""
        schema_id = str(sample_document_schema.id)
        
        # Invalid modification (string instead of dict)
        request = {
            "modifications": {"new_field": "invalid_string"},
            "change_description": "Test"
        }
        
        response = client.put(f"/schemas/{schema_id}/modify", json=request)
        
        assert response.status_code == 400
        assert "Invalid modifications" in response.json()["detail"]


@pytest.mark.integration
@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.requires_db
@pytest.mark.requires_llm
class TestCompleteWorkflow:
    """End-to-end workflow tests"""
    
    async def test_complete_extraction_workflow(
        self,
        client,
        clean_db,
        mock_pdf_content,
        mock_llm_classification,
        mock_llm_schema_generation,
        mock_llm_extraction
    ):
        """Test complete workflow: upload -> generate -> approve -> extract"""
        files = {"document": ("test.pdf", BytesIO(mock_pdf_content), "application/pdf")}
        
        # Step 1: Upload document (generates schema)
        response1 = client.post("/extract", files=files)
        assert response1.status_code == 201
        schema_id = response1.json()["schema_id"]
        
        # Step 2: Approve schema
        response2 = client.put(f"/schemas/{schema_id}/approve")
        assert response2.status_code == 200
        
        # Step 3: Extract with approved schema
        files = {"document": ("test.pdf", BytesIO(mock_pdf_content), "application/pdf")}
        response3 = client.post("/extract", files=files)
        assert response3.status_code == 200
        assert response3.json()["status"] == "extracted"
    
    async def test_schema_modification_workflow(
        self,
        client,
        clean_db,
        sample_document_schema,
        sample_modification_request
    ):
        """Test schema modification and re-approval workflow"""
        schema_id = str(sample_document_schema.id)
        
        # Step 1: Modify schema
        response1 = client.put(
            f"/schemas/{schema_id}/modify",
            json=sample_modification_request
        )
        assert response1.status_code == 201
        new_schema_id = response1.json()["new_schema_info"]["id"]
        
        # Step 2: Approve modified schema
        response2 = client.put(f"/schemas/{new_schema_id}/approve")
        assert response2.status_code == 200
        
        # Verify version increment
        approved_schema = await DocumentSchema.get(new_schema_id)
        assert approved_schema.version == 2
        assert approved_schema.status == SchemaStatus.ACTIVE
