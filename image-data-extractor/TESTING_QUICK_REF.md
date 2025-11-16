# Image Data Extractor - Quick Reference Card

## 🚀 Quick Start

```bash
# Install dependencies
cd image-data-extractor
pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# View coverage
open htmlcov/index.html
```

## 📁 Key Files

| File | Purpose |
|------|---------|
| `pytest.ini` | Pytest configuration |
| `tests/conftest.py` | Shared fixtures |
| `tests/test_classifier.py` | Classifier tests |
| `tests/test_schema_operations.py` | Schema utils tests |
| `tests/test_api.py` | API & E2E tests |
| `SCHEMA_DOCUMENTATION.md` | Complete schema reference |
| `PYTEST_README.md` | Detailed testing guide |
| `TESTING_FRAMEWORK_SUMMARY.md` | Overview & summary |

## 🧪 Run Tests By Category

```bash
pytest -m unit                    # Unit tests only
pytest -m integration             # Integration tests only
pytest -m e2e                     # End-to-end tests only
pytest -m "not slow"              # Fast tests only
pytest -m "not requires_llm"      # No LLM API calls
pytest -m "not requires_db"       # No database needed
```

## 📊 Coverage Commands

```bash
pytest --cov=src                           # Basic coverage
pytest --cov=src --cov-report=term-missing # Show missing lines
pytest --cov=src --cov-report=html         # HTML report
pytest --cov=src --cov-fail-under=70       # Fail if <70%
```

## 🔍 Useful Options

```bash
pytest -v                         # Verbose output
pytest -vv                        # Extra verbose
pytest -s                         # Show print statements
pytest -x                         # Stop on first failure
pytest -k "test_name"            # Run tests matching name
pytest --durations=10            # Show 10 slowest tests
pytest --pdb                     # Debug on failure
pytest -n auto                   # Parallel execution
```

## 🏷️ Test Markers

| Marker | Description |
|--------|-------------|
| `@pytest.mark.unit` | Unit tests |
| `@pytest.mark.integration` | Integration tests |
| `@pytest.mark.e2e` | End-to-end tests |
| `@pytest.mark.slow` | Tests >5 seconds |
| `@pytest.mark.requires_llm` | Needs LLM API |
| `@pytest.mark.requires_db` | Needs MongoDB |
| `@pytest.mark.asyncio` | Async tests |

## 🛠️ Common Fixtures

```python
# Database
clean_db                  # Fresh database
sample_document_schema    # Sample schema in DB

# Data
sample_passport_schema    # Passport schema dict
sample_pan_schema        # PAN card schema dict

# Files
temp_dir                 # Temporary directory
mock_pdf_file           # Mock PDF file

# Mocks
mock_llm_classification  # Mock classification
mock_llm_extraction     # Mock extraction
```

## 📖 Documentation Quick Links

### SCHEMA_DOCUMENTATION.md
- Indian Passport schema (30+ fields)
- Indian PAN Card schema
- Field types & validation
- Schema versioning
- Sample extractions

### PYTEST_README.md
- Installation guide
- Running tests
- Writing new tests
- Fixtures reference
- CI/CD integration

### TESTING_FRAMEWORK_SUMMARY.md
- Complete overview
- Test coverage metrics
- Best practices
- Quick start guide

## 🎯 Coverage Targets

| Module | Target |
|--------|--------|
| `classifier.py` | 85% |
| `schema_operations.py` | 90% |
| `universal.py` | 80% |
| `main.py` | 75% |
| **Overall** | **70%+** |

## 📊 Test Statistics

- **Total Tests:** 45+
- **Test Files:** 3
- **Fixtures:** 20+
- **Lines of Test Code:** 1200+
- **Documentation Lines:** 2200+

## 🔧 Troubleshooting

```bash
# Import errors
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Mock database (no MongoDB needed)
pytest -m "not requires_db"

# Skip LLM tests
pytest -m "not requires_llm"

# Debug failing test
pytest tests/test_file.py::test_name --pdb -s
```

## 📝 Test Template

```python
import pytest

@pytest.mark.unit
@pytest.mark.asyncio
async def test_my_feature(clean_db):
    """Test description"""
    # Arrange
    input_data = ...
    
    # Act
    result = await my_function(input_data)
    
    # Assert
    assert result == expected
```

## 🚦 CI/CD Example

```yaml
# .github/workflows/test.yml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements.txt
      - run: pytest --cov=src --cov-fail-under=70
```

## 💡 Pro Tips

1. **Run fast tests during development**
   ```bash
   pytest -m "not slow"
   ```

2. **Test one module at a time**
   ```bash
   pytest tests/test_classifier.py -v
   ```

3. **Use fixtures for clean tests**
   ```python
   def test_with_fixtures(clean_db, sample_schema):
       # Clean state guaranteed
   ```

4. **Mock external services**
   ```python
   def test_with_mocks(mock_llm_classification):
       # No real API calls
   ```

5. **Check coverage for specific file**
   ```bash
   pytest --cov=src/extractors/classifier --cov-report=term-missing
   ```

## 📞 Quick Help

```bash
pytest --help                    # All options
pytest --markers                 # List all markers
pytest --fixtures               # List all fixtures
pytest --collect-only           # Show what would run
```

---

**Quick Reference Version:** 1.0
**Last Updated:** November 2025
**Framework:** pytest 8.0+ | Python 3.12+
