"""
Pytest configuration and fixtures for Image Data Extractor tests
"""
import pytest
import asyncio
import os
from pathlib import Path
from typing import AsyncGenerator, Generator
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
import tempfile
import shutil

from fastapi.testclient import TestClient
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from mongomock_motor import AsyncMongoMockClient

# Import application components
from main import app
from src.db.models import (
    DocumentSchema,
    SchemaStatus,
    DocumentTypeClassification,
    FieldModification,
    SchemaChange
)
from src.extractors.classifier import classify_document_type
from src.extractors.schema_generator import generate_schema_from_documents
from src.extractors.universal import extract_with_db_schema


# ============================================================================
# Pytest Configuration
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Test Client Fixtures
# ============================================================================

@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """FastAPI test client"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
async def async_client():
    """Async test client for testing async endpoints"""
    from httpx import AsyncClient
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture
async def mock_mongodb():
    """Mock MongoDB database using mongomock"""
    client = AsyncMongoMockClient()
    
    # Initialize Beanie with mock database
    await init_beanie(
        database=client.get_database("test_document_extraction"),
        document_models=[DocumentSchema]
    )
    
    yield client
    
    # Cleanup
    await client.close()


@pytest.fixture
async def clean_db(mock_mongodb):
    """Ensure clean database state before each test"""
    await DocumentSchema.delete_all()
    yield
    await DocumentSchema.delete_all()


# ============================================================================
# Sample Data Fixtures
# ============================================================================

@pytest.fixture
def sample_passport_schema() -> dict:
    """Sample Indian passport schema"""
    return {
        "passport_number": {
            "type": "string",
            "description": "Passport number (alphanumeric)",
            "required": True,
            "example": "S0018565"
        },
        "surname": {
            "type": "string",
            "description": "Surname/Last name as shown on passport",
            "required": True,
            "example": "GANGULI"
        },
        "given_names": {
            "type": "string",
            "description": "Given names/First name and middle name",
            "required": True,
            "example": "NILENDU"
        },
        "nationality": {
            "type": "string",
            "description": "Nationality of passport holder",
            "required": True,
            "example": "INDIAN"
        },
        "sex": {
            "type": "string",
            "description": "Gender: M (Male), F (Female), or O (Other)",
            "required": True,
            "example": "M"
        },
        "date_of_birth": {
            "type": "date",
            "description": "Date of birth in DD/MM/YYYY format",
            "required": True,
            "example": "11/11/1999"
        },
        "place_of_birth": {
            "type": "string",
            "description": "Place of birth as mentioned on passport",
            "required": False,
            "example": "BIDHANNAGAR, WEST BENGAL"
        },
        "date_of_issue": {
            "type": "date",
            "description": "Date of issue in DD/MM/YYYY format",
            "required": True,
            "example": "16/03/2018"
        },
        "date_of_expiry": {
            "type": "date",
            "description": "Date of expiry in DD/MM/YYYY format",
            "required": True,
            "example": "15/03/2028"
        },
        "photo_present": {
            "type": "boolean",
            "description": "Whether passport photo is visible",
            "required": True,
            "example": True
        },
        "signature_present": {
            "type": "boolean",
            "description": "Whether signature is visible",
            "required": True,
            "example": True
        },
        "is_document_correct": {
            "type": "boolean",
            "description": "Whether document appears to be a valid passport",
            "required": True,
            "example": True
        }
    }


@pytest.fixture
def sample_pan_schema() -> dict:
    """Sample PAN card schema"""
    return {
        "pan_number": {
            "type": "string",
            "description": "Permanent Account Number (10 alphanumeric characters)",
            "required": True,
            "example": "ABCDE1234F"
        },
        "name": {
            "type": "string",
            "description": "Name as printed on PAN card",
            "required": True,
            "example": "NILENDU GANGULI"
        },
        "father_name": {
            "type": "string",
            "description": "Father's name",
            "required": True,
            "example": "LATE SHRI XXXXX GANGULI"
        },
        "date_of_birth": {
            "type": "date",
            "description": "Date of birth in DD/MM/YYYY format",
            "required": True,
            "example": "11/11/1999"
        },
        "photo_present": {
            "type": "boolean",
            "description": "Whether photo is visible on card",
            "required": True,
            "example": True
        },
        "signature_present": {
            "type": "boolean",
            "description": "Whether signature is visible",
            "required": True,
            "example": True
        },
        "is_document_correct": {
            "type": "boolean",
            "description": "Whether this appears to be a valid PAN card",
            "required": True,
            "example": True
        }
    }


@pytest.fixture
async def sample_document_schema(clean_db, sample_passport_schema) -> DocumentSchema:
    """Create and save a sample document schema"""
    schema = DocumentSchema(
        document_type="passport",
        country="IN",
        document_schema=sample_passport_schema,
        status=SchemaStatus.ACTIVE,
        version=1,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    await schema.insert()
    return schema


@pytest.fixture
def sample_classification() -> DocumentTypeClassification:
    """Sample document classification result"""
    return DocumentTypeClassification(
        document_type="passport",
        confidence=0.95,
        country="IN",
        alternative_types=[
            {"driver_license": 0.3},
            {"voter_id": 0.2}
        ]
    )


# ============================================================================
# File System Fixtures
# ============================================================================

@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create temporary directory for test files"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def test_pdf_path() -> Path:
    """Path to test passport PDF"""
    return Path("test/Passport.pdf")


@pytest.fixture
def mock_pdf_content() -> bytes:
    """Mock PDF file content"""
    # Minimal valid PDF structure
    return b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
>>
endobj
xref
0 4
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
trailer
<<
/Size 4
/Root 1 0 R
>>
startxref
190
%%EOF"""


@pytest.fixture
async def mock_pdf_file(temp_dir, mock_pdf_content) -> Path:
    """Create mock PDF file for testing"""
    pdf_path = temp_dir / "test_document.pdf"
    async with open(pdf_path, "wb") as f:
        await f.write(mock_pdf_content)
    return pdf_path


# ============================================================================
# LLM Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_llm_classification():
    """Mock LLM classification response"""
    mock_classification = DocumentTypeClassification(
        document_type="passport",
        confidence=0.92,
        country="IN",
        alternative_types=[{"driver_license": 0.25}]
    )
    
    with patch('src.extractors.classifier.get_llm') as mock_llm:
        mock_instance = AsyncMock()
        mock_instance.ainvoke.return_value = mock_classification
        mock_llm.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_llm_schema_generation():
    """Mock LLM schema generation response"""
    from src.extractors.schema_generator import GeneratedSchema
    
    mock_schema = GeneratedSchema(
        document_type="passport",
        country="IN",
        document_schema={
            "passport_number": {
                "type": "string",
                "description": "Passport number",
                "required": True,
                "example": "S0018565"
            },
            "name": {
                "type": "string",
                "description": "Full name",
                "required": True,
                "example": "NILENDU GANGULI"
            }
        },
        confidence=0.95
    )
    
    with patch('src.extractors.schema_generator.get_llm') as mock_llm:
        mock_instance = AsyncMock()
        mock_instance.ainvoke.return_value = mock_schema
        mock_llm.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_llm_extraction():
    """Mock LLM extraction response"""
    mock_data = {
        "passport_number": "S0018565",
        "surname": "GANGULI",
        "given_names": "NILENDU",
        "nationality": "INDIAN",
        "date_of_birth": "11/11/1999"
    }
    
    with patch('src.extractors.universal.get_llm') as mock_llm:
        mock_instance = AsyncMock()
        mock_instance.ainvoke.return_value = mock_data
        mock_llm.return_value = mock_instance
        yield mock_instance


# ============================================================================
# Environment Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment variables"""
    original_env = os.environ.copy()
    
    # Set test environment variables
    os.environ["GOOGLE_API_KEY"] = "test_api_key_12345"
    os.environ["MONGODB_URI"] = "mongodb://localhost:27017"
    os.environ["DATABASE_NAME"] = "test_document_extraction"
    os.environ["PORT"] = "8005"
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


# ============================================================================
# Helper Fixtures
# ============================================================================

@pytest.fixture
def sample_field_modification() -> FieldModification:
    """Sample field modification for testing"""
    return FieldModification(
        field_name="middle_name",
        action="add",
        old_definition=None,
        new_definition={
            "type": "string",
            "description": "Middle name",
            "required": False,
            "example": "Kumar"
        }
    )


@pytest.fixture
def sample_schema_change() -> SchemaChange:
    """Sample schema change for testing"""
    return SchemaChange(
        change_type="field_added",
        field_name="middle_name",
        old_value=None,
        new_value={
            "type": "string",
            "description": "Middle name",
            "required": False
        }
    )


@pytest.fixture
def sample_modification_request() -> dict:
    """Sample schema modification request"""
    return {
        "modifications": {
            "middle_name": {
                "type": "string",
                "description": "Middle name of the person",
                "required": False,
                "example": "Kumar"
            },
            "email": None  # This will remove the email field
        },
        "change_description": "Added middle_name field and removed email field"
    }
