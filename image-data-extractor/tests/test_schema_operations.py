"""
Unit tests for schema operations and utilities
Tests schema modification, versioning, and comparison functions
"""
import pytest
from datetime import datetime, timezone

from src.utils.schema_operations import (
    compare_schemas,
    apply_schema_modifications,
    calculate_next_version,
    generate_change_summary,
    validate_schema_modifications,
    get_modification_metadata,
    find_latest_schema_version
)
from src.db.models import DocumentSchema, SchemaStatus, SchemaChange


@pytest.mark.unit
@pytest.mark.asyncio
class TestCompareSchemas:
    """Tests for schema comparison function"""
    
    def test_no_changes(self):
        """Test comparing identical schemas"""
        schema = {"field1": {"type": "string", "required": True}}
        changes = compare_schemas(schema, schema)
        assert len(changes) == 0
    
    def test_field_added(self):
        """Test detecting added fields"""
        original = {"field1": {"type": "string"}}
        modified = {
            "field1": {"type": "string"},
            "field2": {"type": "integer"}
        }
        
        changes = compare_schemas(original, modified)
        assert len(changes) == 1
        assert changes[0].change_type == "field_added"
        assert changes[0].field_name == "field2"
        assert changes[0].new_value == {"type": "integer"}
    
    def test_field_removed(self):
        """Test detecting removed fields"""
        original = {
            "field1": {"type": "string"},
            "field2": {"type": "integer"}
        }
        modified = {"field1": {"type": "string"}}
        
        changes = compare_schemas(original, modified)
        assert len(changes) == 1
        assert changes[0].change_type == "field_removed"
        assert changes[0].field_name == "field2"
        assert changes[0].old_value == {"type": "integer"}
    
    def test_field_updated(self):
        """Test detecting updated fields"""
        original = {"field1": {"type": "string", "required": True}}
        modified = {"field1": {"type": "string", "required": False}}
        
        changes = compare_schemas(original, modified)
        assert len(changes) == 1
        assert changes[0].change_type == "field_updated"
        assert changes[0].field_name == "field1"
        assert changes[0].old_value == {"type": "string", "required": True}
        assert changes[0].new_value == {"type": "string", "required": False}
    
    def test_multiple_changes(self):
        """Test detecting multiple changes"""
        original = {
            "field1": {"type": "string"},
            "field2": {"type": "integer"}
        }
        modified = {
            "field1": {"type": "boolean"},  # Updated
            "field3": {"type": "date"}      # Added
            # field2 removed
        }
        
        changes = compare_schemas(original, modified)
        assert len(changes) == 3
        
        change_types = {c.change_type for c in changes}
        assert "field_added" in change_types
        assert "field_removed" in change_types
        assert "field_updated" in change_types


@pytest.mark.unit
@pytest.mark.asyncio
class TestApplySchemaModifications:
    """Tests for applying schema modifications"""
    
    def test_add_new_field(self):
        """Test adding a new field"""
        original = {"field1": {"type": "string"}}
        modifications = {
            "field2": {"type": "integer", "description": "New field"}
        }
        
        result = apply_schema_modifications(original, modifications)
        assert "field1" in result
        assert "field2" in result
        assert result["field2"]["type"] == "integer"
    
    def test_update_existing_field(self):
        """Test updating an existing field"""
        original = {"field1": {"type": "string", "required": True}}
        modifications = {
            "field1": {"type": "string", "required": False, "description": "Updated"}
        }
        
        result = apply_schema_modifications(original, modifications)
        assert result["field1"]["required"] is False
        assert result["field1"]["description"] == "Updated"
    
    def test_remove_field(self):
        """Test removing a field (None value)"""
        original = {
            "field1": {"type": "string"},
            "field2": {"type": "integer"}
        }
        modifications = {"field2": None}
        
        result = apply_schema_modifications(original, modifications)
        assert "field1" in result
        assert "field2" not in result
    
    def test_multiple_modifications(self):
        """Test applying multiple modifications at once"""
        original = {
            "field1": {"type": "string"},
            "field2": {"type": "integer"},
            "field3": {"type": "boolean"}
        }
        modifications = {
            "field1": {"type": "string", "description": "Updated"},  # Update
            "field2": None,  # Remove
            "field4": {"type": "date"}  # Add
        }
        
        result = apply_schema_modifications(original, modifications)
        assert len(result) == 3
        assert "field1" in result
        assert "field2" not in result
        assert "field3" in result
        assert "field4" in result
    
    def test_empty_modifications(self):
        """Test with no modifications"""
        original = {"field1": {"type": "string"}}
        modifications = {}
        
        result = apply_schema_modifications(original, modifications)
        assert result == original


@pytest.mark.unit
@pytest.mark.asyncio
class TestValidateSchemaModifications:
    """Tests for schema modification validation"""
    
    def test_valid_modifications(self):
        """Test validating correct modifications"""
        modifications = {
            "field1": {"type": "string", "description": "Test field"},
            "field2": None
        }
        
        is_valid, error = validate_schema_modifications(modifications)
        assert is_valid is True
        assert error is None
    
    def test_invalid_field_type_string(self):
        """Test invalid field type (string instead of dict)"""
        modifications = {
            "field1": "invalid_string"
        }
        
        is_valid, error = validate_schema_modifications(modifications)
        assert is_valid is False
        assert "must be a dictionary or None" in error
    
    def test_invalid_field_type_list(self):
        """Test invalid field type (list instead of dict)"""
        modifications = {
            "field1": ["invalid", "list"]
        }
        
        is_valid, error = validate_schema_modifications(modifications)
        assert is_valid is False
        assert "must be a dictionary or None" in error
    
    def test_empty_modifications_invalid(self):
        """Test that empty modifications are invalid"""
        is_valid, error = validate_schema_modifications({})
        assert is_valid is False
        assert "at least one modification" in error.lower()


@pytest.mark.unit
@pytest.mark.asyncio
class TestCalculateNextVersion:
    """Tests for version calculation"""
    
    async def test_first_version(self, clean_db):
        """Test calculating version for first schema"""
        schema = DocumentSchema(
            document_type="passport",
            country="IN",
            document_schema={"test": "field"},
            status=SchemaStatus.ACTIVE,
            version=1
        )
        await schema.insert()
        
        next_version = await calculate_next_version(schema)
        assert next_version == 2
    
    async def test_subsequent_version(self, clean_db):
        """Test calculating next version with existing versions"""
        # Create version 1
        schema_v1 = DocumentSchema(
            document_type="passport",
            country="IN",
            document_schema={"test": "field"},
            status=SchemaStatus.DEPRECATED,
            version=1
        )
        await schema_v1.insert()
        
        # Create version 2
        schema_v2 = DocumentSchema(
            document_type="passport",
            country="IN",
            document_schema={"test": "field"},
            status=SchemaStatus.ACTIVE,
            version=2
        )
        await schema_v2.insert()
        
        next_version = await calculate_next_version(schema_v2)
        assert next_version == 3


@pytest.mark.unit
@pytest.mark.asyncio
class TestFindLatestSchemaVersion:
    """Tests for finding latest schema version"""
    
    async def test_find_latest_active(self, clean_db):
        """Test finding the latest active schema"""
        # Create multiple versions
        for v in [1, 2, 3]:
            schema = DocumentSchema(
                document_type="passport",
                country="IN",
                document_schema={"test": f"v{v}"},
                status=SchemaStatus.ACTIVE if v == 3 else SchemaStatus.DEPRECATED,
                version=v
            )
            await schema.insert()
        
        latest = await find_latest_schema_version("passport", "IN")
        assert latest is not None
        assert latest.version == 3
        assert latest.status == SchemaStatus.ACTIVE
    
    async def test_find_latest_in_review(self, clean_db):
        """Test finding latest when multiple statuses exist"""
        schema_active = DocumentSchema(
            document_type="passport",
            country="IN",
            document_schema={"test": "v1"},
            status=SchemaStatus.ACTIVE,
            version=1
        )
        schema_review = DocumentSchema(
            document_type="passport",
            country="IN",
            document_schema={"test": "v2"},
            status=SchemaStatus.IN_REVIEW,
            version=2
        )
        await schema_active.insert()
        await schema_review.insert()
        
        latest = await find_latest_schema_version("passport", "IN")
        assert latest is not None
        assert latest.version == 2
        assert latest.status == SchemaStatus.IN_REVIEW
    
    async def test_find_latest_no_schemas(self, clean_db):
        """Test when no schemas exist"""
        latest = await find_latest_schema_version("passport", "IN")
        assert latest is None


@pytest.mark.unit
class TestGenerateChangeSummary:
    """Tests for change summary generation"""
    
    def test_summary_with_additions(self):
        """Test summary for added fields"""
        changes = [
            SchemaChange(
                change_type="field_added",
                field_name="field1",
                new_value={"type": "string"}
            )
        ]
        
        summary = generate_change_summary(changes)
        assert "Added: field1" in summary
    
    def test_summary_with_updates(self):
        """Test summary for updated fields"""
        changes = [
            SchemaChange(
                change_type="field_updated",
                field_name="field1",
                old_value={"type": "string"},
                new_value={"type": "integer"}
            )
        ]
        
        summary = generate_change_summary(changes)
        assert "Updated: field1" in summary
    
    def test_summary_with_removals(self):
        """Test summary for removed fields"""
        changes = [
            SchemaChange(
                change_type="field_removed",
                field_name="field1",
                old_value={"type": "string"}
            )
        ]
        
        summary = generate_change_summary(changes)
        assert "Removed: field1" in summary
    
    def test_summary_with_multiple_changes(self):
        """Test summary with all types of changes"""
        changes = [
            SchemaChange(change_type="field_added", field_name="field1", new_value={}),
            SchemaChange(change_type="field_updated", field_name="field2", old_value={}, new_value={}),
            SchemaChange(change_type="field_removed", field_name="field3", old_value={})
        ]
        
        summary = generate_change_summary(changes)
        assert "Added: field1" in summary
        assert "Updated: field2" in summary
        assert "Removed: field3" in summary


@pytest.mark.unit
class TestGetModificationMetadata:
    """Tests for modification metadata generation"""
    
    def test_metadata_basic(self):
        """Test basic metadata generation"""
        changes = [
            SchemaChange(
                change_type="field_added",
                field_name="field1",
                new_value={"type": "string"}
            )
        ]
        
        metadata = get_modification_metadata(changes, "Test modification")
        
        assert "total_changes" in metadata
        assert metadata["total_changes"] == 1
        assert "change_description" in metadata
        assert metadata["change_description"] == "Test modification"
    
    def test_metadata_counts(self):
        """Test change count breakdown in metadata"""
        changes = [
            SchemaChange(change_type="field_added", field_name="f1", new_value={}),
            SchemaChange(change_type="field_added", field_name="f2", new_value={}),
            SchemaChange(change_type="field_updated", field_name="f3", old_value={}, new_value={}),
            SchemaChange(change_type="field_removed", field_name="f4", old_value={})
        ]
        
        metadata = get_modification_metadata(changes, None)
        
        assert metadata["total_changes"] == 4
        assert "fields_added" in metadata
        assert "fields_updated" in metadata
        assert "fields_removed" in metadata
