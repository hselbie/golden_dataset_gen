# Test Suite for Query Expansion Project

This directory contains comprehensive unit and integration tests for the query expansion system.

## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Pytest fixtures and configuration
├── test_query_analyzer.py   # Unit tests for QueryAnalyzer
├── test_query_generator.py  # Unit tests for QueryGenerator
├── test_answer_generator.py # Unit tests for AnswerGenerator
├── test_integration.py      # Integration tests
└── README.md               # This file
```

## Running Tests

### Quick Start

Run all tests:
```bash
./run_tests.sh
```

Or using pytest directly:
```bash
pytest tests/
```

### Test Options

**Unit tests only:**
```bash
./run_tests.sh unit
pytest tests/ -m unit
```

**Integration tests only:**
```bash
./run_tests.sh integration
pytest tests/ -m integration
```

**With coverage report:**
```bash
./run_tests.sh coverage
```

**Quick tests (excludes slow tests):**
```bash
./run_tests.sh quick
```

**Verbose output:**
```bash
./run_tests.sh verbose
```

### Individual Test Files

Run tests from a specific file:
```bash
pytest tests/test_query_analyzer.py -v
pytest tests/test_query_generator.py -v
pytest tests/test_answer_generator.py -v
pytest tests/test_integration.py -v
```

### Specific Test Functions

Run a specific test function:
```bash
pytest tests/test_query_analyzer.py::TestQueryAnalyzer::test_extract_entities -v
```

## Test Coverage

Generate HTML coverage report:
```bash
pytest tests/ --cov --cov-report=html
```

View the report by opening `htmlcov/index.html` in a browser.

## Test Markers

Tests are organized with markers:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.requires_api` - Tests requiring API access

Run tests by marker:
```bash
pytest tests/ -m unit
pytest tests/ -m integration
pytest tests/ -m "not slow"
```

## Test Components

### QueryAnalyzer Tests (`test_query_analyzer.py`)

Tests for query element extraction:
- Entity extraction
- Noun phrase extraction
- Verb extraction
- Concept extraction
- Edge cases (empty queries, complex queries)

### QueryGenerator Tests (`test_query_generator.py`)

Tests for question generation:
- Basic question generation
- Prompt construction
- Response parsing
- Error handling

### AnswerGenerator Tests (`test_answer_generator.py`)

Tests for answer generation:
- LLM-based answers
- Source routing (LLM, datastore, Google Search)
- Q&A pair structure
- Error recovery

### Integration Tests (`test_integration.py`)

End-to-end pipeline tests:
- Full query processing pipeline
- Multiple query handling
- Data flow integrity
- Error propagation

## Fixtures

Common fixtures available in `conftest.py`:

- `sample_query` - Sample query string
- `sample_elements` - Sample extracted elements
- `sample_questions` - Sample questions list
- `sample_qa_pairs` - Sample Q&A pairs

## Configuration

Test configuration is in:
- `pytest.ini` - Pytest settings
- `conftest.py` - Shared fixtures and setup

## Continuous Integration

These tests are designed to run in CI/CD pipelines. They:
- Use mocks for external dependencies
- Have predictable, deterministic behavior
- Include proper error handling tests
- Generate coverage reports

## Writing New Tests

When adding new tests:

1. Follow the existing naming convention (`test_*.py`)
2. Use descriptive test names (`test_what_is_being_tested`)
3. Add appropriate markers
4. Mock external dependencies (API calls, file I/O)
5. Test both success and failure cases
6. Update this README if adding new test categories

## Troubleshooting

**Import errors:**
- Ensure you're running from the project root
- Check that all dependencies are installed: `pip install -r requirements.txt`

**Test failures:**
- Check environment variables are set (see `conftest.py`)
- Verify mock objects are configured correctly
- Review test logs for detailed error messages

**Coverage issues:**
- Ensure test coverage includes both success and error paths
- Check that mocks don't skip important code paths
