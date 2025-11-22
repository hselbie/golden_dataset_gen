# Setup Guide

This guide will help you set up and run the query expansion project.

## Prerequisites

- Python 3.11 or higher
- UV (recommended) or pip

## Installation

### Option 1: Using UV (Recommended - Fast!)

1. **Install UV** (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. **Sync dependencies**:
```bash
uv sync
```

3. **Install test dependencies**:
```bash
uv sync --extra test
```

4. **Download spaCy language model**:
```bash
uv run python -m spacy download en_core_web_sm
```

### Option 2: Using pip

1. **Create virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Download spaCy language model**:
```bash
python -m spacy download en_core_web_sm
```

## Configuration

1. **Create `.env` file** from the template:
```bash
cp .env.example .env
```

2. **Edit `.env`** and add your credentials:
```env
PROJECT=your-gcp-project-id
LOCATION=us-central1
LLM=gemini-2.0-flash
EMBEDDING_MODEL=textembedding-gecko@003
DATASTORE_ID=your-datastore-id
GROUNDING=1
GAPIKEY=your-google-api-key-here
```

## Running Tests

### With UV (Recommended)

```bash
# Run all tests
./run_tests_uv.sh

# Run with coverage
./run_tests_uv.sh coverage

# Run only unit tests
./run_tests_uv.sh unit

# Run only integration tests
./run_tests_uv.sh integration

# Quick tests (no slow tests)
./run_tests_uv.sh quick

# Verbose output
./run_tests_uv.sh verbose
```

### With pytest directly

```bash
# Using UV
uv run pytest tests/ -v

# Using activated venv
pytest tests/ -v

# With coverage
pytest tests/ --cov --cov-report=html
```

## Running the Application

### With UV
```bash
uv run python main.py
```

### With activated venv
```bash
python main.py
```

## Project Structure

```
query_expansion/
├── analyzer/              # Text analysis components
├── config/                # Configuration and logging
├── goldendataset/         # Golden dataset generation
├── knowledgegraph/        # Knowledge graph builder
├── querygenerator/        # Query and answer generation
├── rag_evaluator/         # RAG evaluation tools
├── tests/                 # Test suite
├── .env.example           # Environment template
├── pyproject.toml         # Project metadata and dependencies
├── requirements.txt       # Pip requirements
└── README.md             # Project documentation
```

## Logging

Logs are automatically saved to the `logs/` directory with rotation:
- Console output: INFO level
- File output: DEBUG level with detailed context
- Log files are rotated at 10MB with 5 backups

To configure logging in your code:
```python
from config.logging_config import setup_logging

# Setup logging (call once at start)
setup_logging(log_level=logging.INFO)

# Use logger in your modules
import logging
logger = logging.getLogger(__name__)
logger.info("Your message here")
```

## Development

### Installing development dependencies

With UV:
```bash
uv sync --extra dev
```

With pip:
```bash
pip install ipython jupyter
```

### Running interactive Python
```bash
uv run ipython  # With UV
# or
ipython         # With activated venv
```

## Troubleshooting

**Tests fail with import errors:**
- Ensure dependencies are installed: `uv sync --extra test`
- Check you're in the project root directory

**spaCy model not found:**
- Download the model: `uv run python -m spacy download en_core_web_sm`

**API errors:**
- Verify your `.env` file has correct credentials
- Check GCP project permissions

**UV not found:**
- Install UV: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Restart your terminal after installation

## Next Steps

1. Review the [Test Documentation](tests/README.md)
2. Check the main [README.md](README.md) for usage examples
3. Explore the example queries in `ExampleQueries.py`
