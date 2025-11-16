# Image Data Extractor - Pytest Framework

## Overview

Comprehensive pytest test suite for the Image Data Extractor service with unit tests, integration tests, and end-to-end workflows.

---

## Table of Contents

1. [Installation](#installation)
2. [Test Structure](#test-structure)
3. [Running Tests](#running-tests)
4. [Test Categories](#test-categories)
5. [Test Coverage](#test-coverage)
6. [Writing Tests](#writing-tests)
7. [Fixtures](#fixtures)
8. [Mocking](#mocking)
9. [CI/CD Integration](#cicd-integration)
10. [Troubleshooting](#troubleshooting)

---

## Installation

### Install Test Dependencies

```bash
# Install all dependencies including test packages
pip install -r requirements.txt

# Or install test dependencies separately
pip install pytest pytest-asyncio pytest-cov pytest-mock httpx mongomock-motor
```

### Verify Installation

```bash
pytest --version
# Should show: pytest 8.0.0 or higher
```

---

## Test Structure

```
tests/
├── __init__.py                    # Test package initialization
├── conftest.py                    # Shared fixtures and configuration
├── test_classifier.py             # Document classifier tests
├── test_schema_operations.py     # Schema utility tests
└── test_api.py                    # API endpoint and E2E tests
```

### Test File Organization

- **`conftest.py`**: Shared fixtures, mock data, test configuration
- **`test_classifier.py`**: Unit tests for document classification
- **`test_schema_operations.py`**: Unit tests for schema operations
- **`test_api.py`**: Integration and E2E API tests

---

## Running Tests

### Run All Tests

```bash
# From project root
cd /Users/neelu/dev/ai_project_25/image-data-extractor

# Run all tests with verbose output
pytest

# Run with coverage report
pytest --cov=src --cov-report=html
```

### Run Specific Test Files

```bash
# Run only classifier tests
pytest tests/test_classifier.py

# Run only API tests
pytest tests/test_api.py

# Run only schema operation tests
pytest tests/test_schema_operations.py
```

### Run Specific Test Classes

```bash
# Run specific test class
pytest tests/test_classifier.py::TestCalculateSimilarity

# Run specific test method
pytest tests/test_classifier.py::TestCalculateSimilarity::test_identical_strings
```

### Run Tests by Markers

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only E2E tests
pytest -m e2e

# Run tests that don't require LLM
pytest -m "not requires_llm"

# Run tests that don't require database
pytest -m "not requires_db"

# Combine markers
pytest -m "unit and not requires_llm"
```

---

## Test Categories

### Test Markers

Tests are categorized using pytest markers:

| Marker | Description | Example |
|--------|-------------|---------|
| `@pytest.mark.unit` | Unit tests for individual functions | Testing similarity calculation |
| `@pytest.mark.integration` | Integration tests for API endpoints | Testing `/extract` endpoint |
| `@pytest.mark.e2e` | End-to-end workflow tests | Full extraction workflow |
| `@pytest.mark.slow` | Tests taking >5 seconds | Schema generation tests |
| `@pytest.mark.requires_llm` | Tests requiring LLM API calls | Real classification tests |
| `@pytest.mark.requires_db` | Tests requiring MongoDB | Database operations |
| `@pytest.mark.asyncio` | Async tests | All async functions |

### Run Tests by Category

```bash
# Fast tests only (skip slow tests)
pytest -m "not slow"

# Tests that work offline (no LLM or DB)
pytest -m "not requires_llm and not requires_db"

# All unit tests
pytest -m unit

# All integration tests  
pytest -m integration
```

---

## Test Coverage

### Generate Coverage Report

```bash
# HTML coverage report
pytest --cov=src --cov-report=html

# View report
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux

# Terminal coverage report
pytest --cov=src --cov-report=term-missing

# Fail if coverage below threshold
pytest --cov=src --cov-fail-under=70
```

### Coverage Targets

| Module | Target Coverage | Current |
|--------|----------------|---------|
| `src/extractors/classifier.py` | 85% | - |
| `src/extractors/schema_generator.py` | 80% | - |
| `src/extractors/universal.py` | 80% | - |
| `src/utils/schema_operations.py` | 90% | - |
| `src/db/models.py` | 95% | - |
| `main.py` | 75% | - |

---

## Writing Tests

### Test Template

```python
import pytest

@pytest.mark.unit  # Add appropriate markers
@pytest.mark.asyncio  # For async tests
class TestMyFeature:
    """Test suite for my feature"""
    
    def test_basic_functionality(self):
        """Test basic functionality"""
        result = my_function()
        assert result == expected_value
    
    async def test_async_functionality(self, clean_db):
        """Test async functionality with database"""
        result = await my_async_function()
        assert result is not None
    
    def test_error_handling(self):
        """Test error handling"""
        with pytest.raises(ValueError):
            my_function(invalid_input)
```

### Testing Best Practices

1. **Use Descriptive Names**
   ```python
   # Good
   def test_classify_returns_none_for_empty_paths(self):
   
   # Bad
   def test1(self):
   ```

2. **One Assertion Per Test** (when possible)
   ```python
   # Good
   def test_passport_number_extracted(self):
       assert result["passport_number"] == "S0018565"
   
   def test_surname_extracted(self):
       assert result["surname"] == "GANGULI"
   ```

3. **Use Fixtures**
   ```python
   def test_with_sample_schema(self, sample_passport_schema):
       # Fixture provides clean test data
       assert "passport_number" in sample_passport_schema
   ```

4. **Mock External Dependencies**
   ```python
   async def test_classification(self, mock_llm_classification):
       # LLM is mocked, no real API calls
       result = await classify_document_type(...)
   ```

---

## Fixtures

### Available Fixtures

#### Database Fixtures

```python
@pytest.fixture
async def mock_mongodb():
    """Mock MongoDB database"""
    # Provides: In-memory MongoDB for testing

@pytest.fixture
async def clean_db(mock_mongodb):
    """Clean database before/after test"""
    # Provides: Fresh database state

@pytest.fixture
async def sample_document_schema(clean_db):
    """Sample document schema in database"""
    # Provides: Pre-populated schema for testing
```

#### Test Data Fixtures

```python
@pytest.fixture
def sample_passport_schema() -> dict:
    """Sample passport schema structure"""
    # Provides: Complete passport schema

@pytest.fixture
def sample_pan_schema() -> dict:
    """Sample PAN card schema structure"""
    # Provides: Complete PAN card schema

@pytest.fixture
def sample_classification() -> DocumentTypeClassification:
    """Sample classification result"""
    # Provides: Mock classification response
```

#### File System Fixtures

```python
@pytest.fixture
def temp_dir() -> Path:
    """Temporary directory for test files"""
    # Provides: Clean temp directory, auto cleanup

@pytest.fixture
def test_pdf_path() -> Path:
    """Path to test passport PDF"""
    # Provides: Path to test/Passport.pdf

@pytest.fixture
def mock_pdf_content() -> bytes:
    """Mock PDF file content"""
    # Provides: Valid minimal PDF bytes

@pytest.fixture
async def mock_pdf_file(temp_dir) -> Path:
    """Mock PDF file in temp directory"""
    # Provides: Actual file on filesystem
```

#### LLM Mock Fixtures

```python
@pytest.fixture
def mock_llm_classification():
    """Mock LLM classification response"""
    # Provides: Mocked classification without API calls

@pytest.fixture
def mock_llm_schema_generation():
    """Mock LLM schema generation"""
    # Provides: Mocked schema generation

@pytest.fixture
def mock_llm_extraction():
    """Mock LLM extraction response"""
    # Provides: Mocked data extraction
```

### Using Fixtures

```python
# Single fixture
def test_with_schema(sample_passport_schema):
    assert "passport_number" in sample_passport_schema

# Multiple fixtures
async def test_with_db_and_schema(clean_db, sample_document_schema):
    result = await DocumentSchema.find_all().to_list()
    assert len(result) == 1

# Fixture composition
@pytest.fixture
async def approved_schema(clean_db, sample_passport_schema):
    schema = DocumentSchema(
        document_type="passport",
        country="IN",
        document_schema=sample_passport_schema,
        status=SchemaStatus.ACTIVE
    )
    await schema.insert()
    return schema
```

---

## Mocking

### Mock LLM Responses

```python
from unittest.mock import patch, AsyncMock

async def test_with_mock_llm():
    """Test with mocked LLM"""
    with patch('src.extractors.classifier.get_llm') as mock_llm:
        mock_instance = AsyncMock()
        mock_instance.ainvoke.return_value = DocumentTypeClassification(
            document_type="passport",
            confidence=0.95,
            country="IN",
            alternative_types=[]
        )
        mock_llm.return_value = mock_instance
        
        result = await classify_document_type([...])
        assert result.document_type == "passport"
```

### Mock Database Operations

```python
# Database is automatically mocked via mongomock_motor
async def test_database_operation(clean_db):
    """Test uses in-memory mock database"""
    schema = DocumentSchema(...)
    await schema.insert()
    
    # Query mock database
    found = await DocumentSchema.get(schema.id)
    assert found is not None
```

### Mock File Operations

```python
async def test_with_mock_file(temp_dir):
    """Test with temporary file"""
    test_file = temp_dir / "test.pdf"
    test_file.write_bytes(b"mock content")
    
    # Use test file
    assert test_file.exists()
    # Auto cleanup after test
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Run Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      env:
        GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
      run: |
        pytest -m "not requires_llm" --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

### GitLab CI Example

```yaml
test:
  image: python:3.12
  stage: test
  script:
    - pip install -r requirements.txt
    - pytest -m "not requires_llm" --cov=src --cov-report=term
  coverage: '/TOTAL.*\s+(\d+%)$/'
```

---

## Troubleshooting

### Common Issues

#### 1. Import Errors

```
ModuleNotFoundError: No module named 'src'
```

**Solution:**
```bash
# Ensure PYTHONPATH is set
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Or use pytest.ini (already configured)
pytest
```

#### 2. Async Test Errors

```
RuntimeError: Event loop is closed
```

**Solution:**
Already configured in `pytest.ini`:
```ini
[pytest]
asyncio_mode = auto
```

#### 3. Database Connection Errors

```
ConnectionFailure: could not connect to MongoDB
```

**Solution:**
Tests use mock database automatically. No real MongoDB needed.

#### 4. LLM API Errors

```
google.api_core.exceptions.PermissionDenied: API key not valid
```

**Solution:**
```bash
# Run tests without LLM calls
pytest -m "not requires_llm"

# Or set dummy API key for mocked tests
export GOOGLE_API_KEY="test_key"
```

#### 5. Fixture Not Found

```
fixture 'sample_passport_schema' not found
```

**Solution:**
Ensure `conftest.py` is in the tests directory and properly named.

### Debug Mode

```bash
# Run with verbose output
pytest -vv

# Show print statements
pytest -s

# Show local variables on failure
pytest -l

# Drop into debugger on failure
pytest --pdb

# Stop at first failure
pytest -x

# Show slowest tests
pytest --durations=10
```

### Selective Test Execution

```bash
# Run specific test by name pattern
pytest -k "test_classify"

# Run tests matching multiple patterns
pytest -k "test_classify or test_extract"

# Run tests NOT matching pattern
pytest -k "not slow"
```

---

## Test Examples

### Unit Test Example

```python
@pytest.mark.unit
class TestCalculateSimilarity:
    def test_identical_strings(self):
        """Test that identical strings return 1.0 similarity"""
        result = calculate_similarity("passport", "passport")
        assert result == 1.0
    
    def test_case_insensitive(self):
        """Test case-insensitive comparison"""
        result = calculate_similarity("Passport", "PASSPORT")
        assert result == 1.0
```

### Integration Test Example

```python
@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.requires_db
class TestExtractEndpoint:
    async def test_extract_with_active_schema(
        self,
        client,
        clean_db,
        sample_document_schema
    ):
        """Test extraction uses existing schema"""
        files = {"document": ("test.pdf", BytesIO(b"..."), "application/pdf")}
        response = client.post("/extract", files=files)
        
        assert response.status_code == 200
        assert response.json()["status"] == "extracted"
```

### E2E Test Example

```python
@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.asyncio
class TestCompleteWorkflow:
    async def test_full_extraction_workflow(self, client, clean_db):
        """Test: upload -> generate -> approve -> extract"""
        
        # Step 1: Upload (generates schema)
        files = {"document": ("test.pdf", ...)}
        r1 = client.post("/extract", files=files)
        assert r1.status_code == 201
        schema_id = r1.json()["schema_id"]
        
        # Step 2: Approve
        r2 = client.put(f"/schemas/{schema_id}/approve")
        assert r2.status_code == 200
        
        # Step 3: Extract with approved schema
        files = {"document": ("test.pdf", ...)}
        r3 = client.post("/extract", files=files)
        assert r3.status_code == 200
        assert "data" in r3.json()
```

---

## Performance Testing

### Benchmarking Tests

```bash
# Install pytest-benchmark
pip install pytest-benchmark

# Run benchmark tests
pytest --benchmark-only
```

### Example Benchmark Test

```python
@pytest.mark.benchmark
def test_similarity_calculation_performance(benchmark):
    """Benchmark similarity calculation"""
    result = benchmark(calculate_similarity, "passport", "passports")
    assert 0.8 < result < 1.0
```

---

## Test Metrics

### Success Criteria

- ✅ All tests pass
- ✅ Code coverage > 70%
- ✅ No critical security issues
- ✅ All API endpoints tested
- ✅ Error handling validated

### Run Summary

```bash
pytest --tb=line -v

# Example output:
=============== test session starts ================
collected 45 items

tests/test_classifier.py::TestCalculateSimilarity::test_identical_strings PASSED [ 2%]
tests/test_classifier.py::TestCalculateSimilarity::test_case_insensitive PASSED [ 4%]
...
tests/test_api.py::TestCompleteWorkflow::test_full_workflow PASSED [100%]

=============== 45 passed in 12.34s ================
```

---

## Resources

### Documentation
- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)

### Related Files
- `pytest.ini` - Pytest configuration
- `conftest.py` - Shared fixtures
- `SCHEMA_DOCUMENTATION.md` - Schema reference
- `TESTING_README.md` - Manual testing guide

---

**Last Updated:** November 2025
**Framework Version:** pytest 8.0+
**Python Version:** 3.12+
