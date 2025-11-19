# InsurSpeak Backend Tests

Comprehensive test suite for the InsurSpeak backend API.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures and configuration
├── test_document_processor.py  # Document processing tests
├── test_summary_generator.py   # Summary generation tests
├── test_auth.py               # Authentication tests
├── test_claims_engine.py      # Claims analysis tests
└── test_main.py               # API integration tests
```

## Running Tests

### Run All Tests

```bash
cd backend
pytest
```

### Run Specific Test File

```bash
pytest tests/test_auth.py
```

### Run Specific Test Class

```bash
pytest tests/test_auth.py::TestPasswordHashing
```

### Run Specific Test Function

```bash
pytest tests/test_auth.py::TestPasswordHashing::test_hash_password
```

### Run Tests with Coverage Report

```bash
pytest --cov=. --cov-report=html
```

Then open `htmlcov/index.html` in your browser to see detailed coverage.

### Run Tests in Verbose Mode

```bash
pytest -v
```

### Run Tests with Output

```bash
pytest -s
```

### Run Only Fast Tests (exclude slow tests)

```bash
pytest -m "not slow"
```

## Test Categories

### Unit Tests

Test individual functions and methods in isolation:

```bash
pytest -m unit
```

### Integration Tests

Test API endpoints and interactions between components:

```bash
pytest -m integration tests/test_main.py
```

### Async Tests

```bash
pytest -m asyncio
```

## Key Test Fixtures

Defined in `conftest.py`:

- `client` - FastAPI test client
- `mock_openai` - Mocked OpenAI API (avoids costs during testing)
- `mock_mongodb` - Mocked MongoDB database
- `sample_health_policy_text` - Sample health insurance policy
- `sample_auto_policy_text` - Sample auto insurance policy
- `sample_user_data` - Sample user data
- `authenticated_headers` - Auth headers with valid JWT

## Writing New Tests

### Example Test

```python
import pytest

def test_my_feature(client, mock_mongodb):
    """Test description."""
    # Arrange
    mock_mongodb.users.find_one.return_value = {"email": "test@test.com"}

    # Act
    response = client.get("/my-endpoint")

    # Assert
    assert response.status_code == 200
    assert "expected_key" in response.json()
```

### Async Test

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    """Test async function."""
    result = await my_async_function()
    assert result is not None
```

## Test Coverage

Current test coverage:

- **document_processor.py**: Entity extraction, insurance type detection, PDF parsing
- **summary_generator.py**: AI summary generation, fallback logic
- **auth.py**: Password hashing, JWT tokens, user authentication
- **claims_engine.py**: Situation analysis, claim recommendations
- **main.py**: All API endpoints (auth, document processing, Q&A, policy management, claims)

## Mocking Strategy

### OpenAI API

All OpenAI API calls are mocked to:
- Avoid rate limits
- Reduce test costs
- Ensure consistent test results
- Speed up test execution

### MongoDB

MongoDB is mocked to:
- Avoid requiring a running database
- Speed up tests
- Isolate tests from data changes

## Continuous Integration

These tests run automatically on every commit via GitHub Actions (see `.github/workflows/test.yml`).

## Troubleshooting

### Import Errors

Make sure you're in the backend directory:

```bash
cd backend
pytest
```

### Module Not Found

Install dependencies:

```bash
pip install -r requirements.txt
```

### Async Warnings

If you see warnings about async, ensure `asyncio_mode = auto` is in `pytest.ini`.

## Test Best Practices

1. **Arrange-Act-Assert**: Structure tests clearly
2. **One assertion per test**: Keep tests focused
3. **Descriptive names**: Test names should describe what they test
4. **Use fixtures**: Reuse common setup code
5. **Mock external dependencies**: Don't call real APIs or databases
6. **Test edge cases**: Empty inputs, long inputs, special characters
7. **Test error handling**: Ensure errors are handled gracefully

## Next Steps

- Add E2E tests with real PDF files in `tests/fixtures/`
- Add performance tests for large documents
- Add security tests (SQL injection, XSS, etc.)
- Increase code coverage to 90%+
