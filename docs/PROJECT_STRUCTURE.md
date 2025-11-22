# Project Structure

This document outlines the complete structure of the Query Expansion project.

## Directory Layout

```
query_expansion/
├── analyzer/                    # Text analysis components
│   ├── __init__.py
│   └── text_analyzer.py         # Simple text keyword extraction
│
├── config/                      # Configuration management
│   ├── __init__.py
│   ├── logging_config.py        # Logging setup with rotation
│   └── variable_config.py       # Environment variable config & GroundingConfig
│
├── goldendataset/               # Golden dataset generation for RAG evaluation
│   ├── __init__.py
│   └── ds_generator.py          # Generate Q&A datasets from seed queries
│
├── knowledgegraph/              # Knowledge graph building
│   ├── __init__.py
│   └── builder.py               # Build and visualize knowledge graphs
│
├── querygenerator/              # Core query expansion logic
│   ├── __init__.py
│   └── generator.py             # QueryAnalyzer, QueryGenerator, AnswerGenerator
│
├── rag_evaluator/               # RAG evaluation utilities
│   ├── __init__.py
│   └── enhanced_generator.py    # Generate datasets from GCS documents
│
├── tests/                       # Comprehensive test suite
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures and configuration
│   ├── README.md                # Test documentation
│   ├── test_answer_generator.py # AnswerGenerator unit tests (10 tests)
│   ├── test_integration.py      # Integration tests (9 tests)
│   ├── test_query_analyzer.py   # QueryAnalyzer unit tests (12 tests)
│   └── test_query_generator.py  # QueryGenerator unit tests (10 tests)
│
├── .env.example                 # Environment variable template
├── .gitignore                   # Comprehensive gitignore
├── example_knowledge_graph.png  # Example visualization
├── ExampleQueries.py            # Sample queries for testing
├── main.py                      # Main entry point
├── PROJECT_STRUCTURE.md         # This file
├── pyproject.toml               # UV/pip package configuration
├── pytest.ini                   # Pytest configuration
├── README.md                    # Project documentation
├── requirements.txt             # Pip requirements
├── run_tests.sh                 # Test runner (traditional)
├── run_tests_uv.sh              # Test runner (UV)
├── SETUP.md                     # Setup and installation guide
└── TEST_RESULTS.md              # Latest test results
```

## Core Components

### 1. Query Processing Pipeline

**QueryAnalyzer** (`querygenerator/generator.py`)
- Extracts semantic elements from queries using spaCy
- Identifies entities, noun phrases, verbs, and concepts
- Provides structured data for downstream processing

**QueryGenerator** (`querygenerator/generator.py`)
- Generates new questions from extracted elements
- Uses LLM to create diverse, natural questions
- Configurable number of questions per query

**AnswerGenerator** (`querygenerator/generator.py`)
- Generates answers from multiple sources:
  - LLM (Gemini)
  - Datastore (Vertex AI Search)
  - Google Search (with grounding)
- Returns Q&A pairs for evaluation

### 2. Knowledge Graph System

**KnowledgeGraphBuilder** (`knowledgegraph/builder.py`)
- Builds weighted graphs from query elements
- Tracks co-occurrence patterns
- Enables related element discovery

**GraphVisualizer** (`knowledgegraph/builder.py`)
- Visualizes knowledge graphs with matplotlib
- Color-coded by node type
- Edge thickness represents relationship strength

### 3. Dataset Generation

**GoldenDatasetGenerator** (`goldendataset/ds_generator.py`)
- Creates evaluation datasets from seed queries
- Integrates with knowledge graphs
- Supports domain-specific generation

**QueryDatasetGenerator** (`rag_evaluator/enhanced_generator.py`)
- Generates Q&A pairs from GCS documents
- Chunks documents for processing
- Exports to CSV for evaluation

### 4. Configuration & Logging

**VarConfig** (`config/variable_config.py`)
- Loads environment variables
- Initializes API clients (Gemini, Vertex AI)
- Provides centralized configuration

**GroundingConfig** (`config/variable_config.py`)
- Extends VarConfig for grounding features
- Supports Vertex AI Search integration
- Configurable grounding sources

**Logging** (`config/logging_config.py`)
- Rotating file handlers (10MB, 5 backups)
- Console and file output
- Configurable log levels per module

## Module Dependencies

```
main.py
  ├── config.variable_config (VarConfig)
  ├── querygenerator.generator
  │   ├── QueryAnalyzer (uses spacy)
  │   ├── QueryGenerator (uses LLM)
  │   └── AnswerGenerator (uses LLM, VertexAI)
  └── analyzer.text_analyzer (TextAnalyzer)

goldendataset/ds_generator.py
  ├── querygenerator.generator (QueryAnalyzer, QueryGenerator)
  ├── knowledgegraph.builder (KnowledgeGraphBuilder, GraphVisualizer)
  └── config.variable_config (GroundingConfig)

rag_evaluator/enhanced_generator.py
  ├── config.variable_config (VarConfig)
  └── google.cloud.storage
```

## Data Flow

### Query Expansion Flow
```
User Query
    ↓
QueryAnalyzer.extract_elements()
    ↓
[entities, noun_phrases, verbs, concepts]
    ↓
QueryGenerator.generate_questions()
    ↓
[List of generated questions]
    ↓
AnswerGenerator.generate_answers(source="llm"|"datastore"|"google")
    ↓
[(question, answer), ...]
```

### Knowledge Graph Flow
```
Seed Queries
    ↓
QueryAnalyzer.extract_elements()
    ↓
KnowledgeGraphBuilder.add_query_elements()
    ↓
Weighted Graph (nodes + edges)
    ↓
GraphVisualizer.visualize()
    ↓
PNG visualization
```

## File Sizes (Production Code Only)

| Component | Lines of Code |
|-----------|---------------|
| querygenerator/generator.py | ~275 lines |
| knowledgegraph/builder.py | ~210 lines |
| goldendataset/ds_generator.py | ~123 lines |
| rag_evaluator/enhanced_generator.py | ~278 lines |
| config/variable_config.py | ~83 lines |
| config/logging_config.py | ~95 lines |
| main.py | ~300 lines |
| **Total Production Code** | **~1,364 lines** |
| **Total Test Code** | **~450 lines** |

## Entry Points

### Main Application
```bash
# With UV
uv run python main.py

# With activated venv
python main.py
```

### Running Tests
```bash
# All tests
./run_tests_uv.sh

# With coverage
./run_tests_uv.sh coverage

# Specific test file
uv run pytest tests/test_query_analyzer.py -v
```

### Generating Datasets
See `goldendataset/ds_generator.py` for examples of:
- Domain-specific dataset generation
- Knowledge graph visualization
- Custom seed query processing

## Dependencies

### Core Dependencies
- `spacy` - NLP for query analysis
- `langchain` - LLM integration framework
- `langchain-google-genai` - Gemini integration
- `google-cloud-aiplatform` - Vertex AI
- `pandas` - Data manipulation
- `networkx` - Graph structures
- `matplotlib` - Visualization

### Testing Dependencies
- `pytest` - Test framework
- `pytest-cov` - Coverage reporting
- `pytest-mock` - Mocking utilities

## Ignored Files

The following are excluded from version control (see `.gitignore`):
- Virtual environments (`.venv/`, `venv*/`)
- Python caches (`__pycache__/`, `*.pyc`)
- Test artifacts (`.pytest_cache/`, `htmlcov/`, `.coverage`)
- Environment files (`.env`, `.env.*`)
- Generated outputs (`generated_datasets/*.csv`, `*.png`)
- IDE files (`.vscode/`, `.idea/`, `.claude/`)
- UV lock file (`uv.lock`)
- Logs (`logs/`, `*.log`)

## Adding New Components

When adding new functionality:

1. **Create appropriate package structure**
   ```bash
   mkdir new_component
   touch new_component/__init__.py
   touch new_component/module.py
   ```

2. **Add logging**
   ```python
   import logging
   logger = logging.getLogger(__name__)
   ```

3. **Write tests**
   ```bash
   touch tests/test_new_component.py
   ```

4. **Update documentation**
   - Add to this file
   - Update README.md if user-facing
   - Document in module docstrings

## Notes

- All Python packages have `__init__.py` files
- Logging is configured centrally in `config/logging_config.py`
- Environment variables are managed via `.env` (use `.env.example` as template)
- Tests use mocked dependencies (no real API calls)
- Coverage target: >80% for core modules
