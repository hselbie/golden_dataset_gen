"""
Pytest configuration and fixtures for tests.
"""

import pytest
import logging
import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment before running tests."""
    # Set environment variables for testing
    os.environ["PROJECT"] = "test-project"
    os.environ["LOCATION"] = "us-central1"
    os.environ["LLM"] = "gemini-2.0-flash"
    os.environ["EMBEDDING_MODEL"] = "textembedding-gecko@003"
    os.environ["DATASTORE_ID"] = "test-datastore"
    os.environ["GROUNDING"] = "0"
    os.environ["GAPIKEY"] = "test-api-key"

    # Configure logging for tests
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    yield

    # Cleanup after tests
    pass


@pytest.fixture
def sample_query():
    """Provide a sample query for testing."""
    return "What are popular attractions in Seattle?"


@pytest.fixture
def sample_elements():
    """Provide sample extracted elements for testing."""
    return {
        "entities": [{"text": "Seattle", "label": "GPE"}],
        "noun_phrases": ["popular attractions", "Seattle"],
        "verbs": ["be"],
        "concepts": ["attractions"],
    }


@pytest.fixture
def sample_questions():
    """Provide sample questions for testing."""
    return [
        "What attractions can I visit in Seattle?",
        "What is Seattle known for?",
        "Where should tourists go in Seattle?",
    ]


@pytest.fixture
def sample_qa_pairs():
    """Provide sample Q&A pairs for testing."""
    return [
        ("What is machine learning?", "Machine learning is a subset of AI."),
        ("How does AI work?", "AI works through algorithms and data."),
        ("What are neural networks?", "Neural networks are computing systems."),
    ]


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line(
        "markers", "requires_api: mark test as requiring API access"
    )
