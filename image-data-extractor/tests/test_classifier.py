"""
Unit tests for document classifier module
Tests classification of documents by type and country
"""
import pytest
from pathlib import Path
from unittest.mock import patch, AsyncMock

from src.extractors.classifier import (
    classify_document_type,
    calculate_similarity,
    find_best_matching_document_type,
    get_existing_document_types
)
from src.db.models import DocumentTypeClassification, DocumentSchema, SchemaStatus


@pytest.mark.unit
@pytest.mark.asyncio
class TestCalculateSimilarity:
    """Tests for similarity calculation function"""
    
    def test_identical_strings(self):
        """Test similarity of identical strings"""
        assert calculate_similarity("passport", "passport") == 1.0
    
    def test_case_insensitive(self):
        """Test that comparison is case insensitive"""
        assert calculate_similarity("Passport", "PASSPORT") == 1.0
        assert calculate_similarity("pan_card", "PAN_CARD") == 1.0
    
    def test_similar_strings(self):
        """Test similarity of similar strings"""
        similarity = calculate_similarity("passport", "passports")
        assert 0.8 < similarity < 1.0
    
    def test_different_strings(self):
        """Test similarity of completely different strings"""
        similarity = calculate_similarity("passport", "pan_card")
        assert similarity < 0.5
    
    def test_empty_strings(self):
        """Test with empty strings"""
        assert calculate_similarity("", "") == 1.0
        assert calculate_similarity("passport", "") < 0.5


@pytest.mark.unit
@pytest.mark.asyncio
class TestFindBestMatchingDocumentType:
    """Tests for document type matching function"""
    
    def test_exact_match(self):
        """Test exact match returns the document type"""
        existing = ["passport", "pan_card", "driver_license"]
        result = find_best_matching_document_type("passport", existing)
        assert result == "passport"
    
    def test_case_insensitive_match(self):
        """Test case insensitive matching"""
        existing = ["passport", "pan_card"]
        result = find_best_matching_document_type("PASSPORT", existing)
        assert result == "passport"
    
    def test_similar_match_above_threshold(self):
        """Test matching similar document types"""
        existing = ["passport", "pan_card"]
        result = find_best_matching_document_type("passports", existing, threshold=0.8)
        assert result == "passport"
    
    def test_no_match_below_threshold(self):
        """Test no match when similarity below threshold"""
        existing = ["passport", "pan_card"]
        result = find_best_matching_document_type("driver_license", existing, threshold=0.9)
        assert result is None
    
    def test_substring_match_boosts_similarity(self):
        """Test that substring matches get higher similarity"""
        existing = ["pan_card", "passport"]
        result = find_best_matching_document_type("pan", existing, threshold=0.8)
        assert result == "pan_card"
    
    def test_empty_existing_types(self):
        """Test with no existing document types"""
        result = find_best_matching_document_type("passport", [])
        assert result is None
    
    def test_best_of_multiple_matches(self):
        """Test selecting best match from multiple similar types"""
        existing = ["passport", "passports", "pass"]
        result = find_best_matching_document_type("passport", existing)
        assert result == "passport"


@pytest.mark.unit
@pytest.mark.asyncio
class TestGetExistingDocumentTypes:
    """Tests for retrieving existing document types from database"""
    
    async def test_get_existing_types_success(self, clean_db, sample_document_schema):
        """Test retrieving existing document types"""
        # Create additional schema
        schema2 = DocumentSchema(
            document_type="pan_card",
            country="IN",
            document_schema={"test": "field"},
            status=SchemaStatus.ACTIVE,
            version=1
        )
        await schema2.insert()
        
        result = await get_existing_document_types("IN")
        assert len(result) == 2
        assert "passport" in result
        assert "pan_card" in result
    
    async def test_get_existing_types_empty(self, clean_db):
        """Test with no existing schemas"""
        result = await get_existing_document_types("US")
        assert result == []
    
    async def test_get_existing_types_filters_by_country(self, clean_db):
        """Test that results are filtered by country"""
        # Create schemas for different countries
        schema_in = DocumentSchema(
            document_type="passport",
            country="IN",
            document_schema={"test": "field"},
            status=SchemaStatus.ACTIVE,
            version=1
        )
        schema_us = DocumentSchema(
            document_type="passport",
            country="US",
            document_schema={"test": "field"},
            status=SchemaStatus.ACTIVE,
            version=1
        )
        await schema_in.insert()
        await schema_us.insert()
        
        result_in = await get_existing_document_types("IN")
        assert len(result_in) == 1
        assert "passport" in result_in
    
    async def test_get_existing_types_deduplicates(self, clean_db):
        """Test that duplicate document types are removed"""
        # Create multiple versions of same type
        for version in [1, 2, 3]:
            schema = DocumentSchema(
                document_type="passport",
                country="IN",
                document_schema={"test": "field"},
                status=SchemaStatus.ACTIVE if version == 3 else SchemaStatus.DEPRECATED,
                version=version
            )
            await schema.insert()
        
        result = await get_existing_document_types("IN")
        assert len(result) == 1
        assert "passport" in result


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.requires_llm
class TestClassifyDocumentType:
    """Tests for main document classification function"""
    
    async def test_classify_single_pdf(self, mock_pdf_file, mock_llm_classification):
        """Test classifying a single PDF document"""
        result = await classify_document_type(
            document_paths=[mock_pdf_file],
            content_types=["application/pdf"]
        )
        
        assert result is not None
        assert isinstance(result, DocumentTypeClassification)
        assert result.document_type == "passport"
        assert result.country == "IN"
        assert 0 <= result.confidence <= 1
    
    async def test_classify_multiple_documents(self, temp_dir, mock_llm_classification):
        """Test classifying multiple documents"""
        # Create multiple test files
        paths = []
        for i in range(3):
            path = temp_dir / f"doc_{i}.pdf"
            path.write_bytes(b"mock pdf content")
            paths.append(path)
        
        content_types = ["application/pdf"] * 3
        
        result = await classify_document_type(paths, content_types)
        
        assert result is not None
        assert result.document_type == "passport"
    
    async def test_classify_empty_paths(self):
        """Test with empty document paths"""
        result = await classify_document_type([], [])
        assert result is None
    
    async def test_classify_nonexistent_file(self, temp_dir):
        """Test with non-existent file path"""
        fake_path = temp_dir / "nonexistent.pdf"
        result = await classify_document_type(
            [fake_path],
            ["application/pdf"]
        )
        assert result is None
    
    async def test_classify_with_retry(self, mock_pdf_file):
        """Test retry mechanism on failure"""
        with patch('src.extractors.classifier.get_llm') as mock_llm:
            mock_instance = AsyncMock()
            # First two calls fail, third succeeds
            mock_instance.ainvoke.side_effect = [
                Exception("API Error"),
                Exception("API Error"),
                DocumentTypeClassification(
                    document_type="passport",
                    confidence=0.90,
                    country="IN",
                    alternative_types=[]
                )
            ]
            mock_llm.return_value = mock_instance
            
            result = await classify_document_type(
                [mock_pdf_file],
                ["application/pdf"],
                max_retries=3
            )
            
            assert result is not None
            assert result.document_type == "passport"
            assert mock_instance.ainvoke.call_count == 3
    
    async def test_classify_matches_existing_type(self, clean_db, mock_pdf_file, sample_document_schema):
        """Test that classification matches existing document types"""
        with patch('src.extractors.classifier.get_llm') as mock_llm:
            mock_instance = AsyncMock()
            # Return slightly different name
            mock_instance.ainvoke.return_value = DocumentTypeClassification(
                document_type="passports",  # Slightly different
                confidence=0.92,
                country="IN",
                alternative_types=[]
            )
            mock_llm.return_value = mock_instance
            
            result = await classify_document_type(
                [mock_pdf_file],
                ["application/pdf"]
            )
            
            # Should match to existing "passport" type
            assert result.document_type == "passport"
    
    async def test_classify_image_document(self, temp_dir):
        """Test classifying image documents"""
        img_path = temp_dir / "test.jpg"
        img_path.write_bytes(b"mock image content")
        
        with patch('src.extractors.classifier.get_llm') as mock_llm:
            mock_instance = AsyncMock()
            mock_instance.ainvoke.return_value = DocumentTypeClassification(
                document_type="pan_card",
                confidence=0.88,
                country="IN",
                alternative_types=[]
            )
            mock_llm.return_value = mock_instance
            
            result = await classify_document_type(
                [img_path],
                ["image/jpeg"]
            )
            
            assert result is not None
            assert result.document_type == "pan_card"
    
    async def test_classify_returns_alternatives(self, mock_pdf_file):
        """Test that alternative document types are returned"""
        with patch('src.extractors.classifier.get_llm') as mock_llm:
            mock_instance = AsyncMock()
            mock_instance.ainvoke.return_value = DocumentTypeClassification(
                document_type="passport",
                confidence=0.85,
                country="IN",
                alternative_types=[
                    {"driver_license": 0.30},
                    {"voter_id": 0.20}
                ]
            )
            mock_llm.return_value = mock_instance
            
            result = await classify_document_type(
                [mock_pdf_file],
                ["application/pdf"]
            )
            
            assert result is not None
            assert len(result.alternative_types) == 2
            assert result.alternative_types[0] == {"driver_license": 0.30}
