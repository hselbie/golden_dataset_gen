# Pre-Commit Checklist

Complete this checklist before committing to the repository.

## ✅ Code Quality

- [x] All Python files follow PEP 8 style guidelines
- [x] All functions have docstrings
- [x] Type hints are used where appropriate
- [x] No hardcoded credentials or API keys in code
- [x] No TODO comments without tracking issues
- [x] Imports are properly organized (stdlib, third-party, local)

## ✅ Testing

- [x] All tests pass (`./run_tests_uv.sh`)
- [x] Test coverage is adequate (>40% overall, >80% for core modules)
- [x] New features have corresponding unit tests
- [x] Integration tests cover main workflows
- [x] No test files or artifacts in commit

## ✅ Documentation

- [x] README.md is up to date
- [x] SETUP.md has installation instructions
- [x] PROJECT_STRUCTURE.md reflects current structure
- [x] Docstrings explain complex logic
- [x] API usage examples are provided

## ✅ Configuration

- [x] .env.example exists with all required variables
- [x] No .env file is committed
- [x] .gitignore is comprehensive
- [x] pyproject.toml is properly configured
- [x] requirements.txt is up to date

## ✅ File Cleanup

- [x] No __pycache__ directories
- [x] No .pyc files
- [x] No IDE-specific files (.vscode, .idea, .claude)
- [x] No test artifacts (.coverage, htmlcov/, .pytest_cache/)
- [x] No virtual environment directories
- [x] No generated output files (*.csv, *.log)
- [x] No lock files (uv.lock)

## ✅ Dependencies

- [x] All dependencies are in pyproject.toml
- [x] All dependencies are in requirements.txt (for compatibility)
- [x] No unused dependencies
- [x] Version constraints are appropriate

## ✅ Security

- [x] No API keys, tokens, or secrets in code
- [x] No credentials in commit history
- [x] .env.example uses placeholder values
- [x] Sensitive files are in .gitignore

## ✅ Git Hygiene

- [x] Commit message is descriptive
- [x] Commits are atomic (one logical change per commit)
- [x] No large binary files (except necessary assets)
- [x] No merge conflicts
- [x] Branch is up to date with main/master

## Quick Verification Commands

```bash
# 1. Run tests
./run_tests_uv.sh

# 2. Check for ignored files in staging
git status --ignored

# 3. Review what will be committed
git status --short

# 4. Check for secrets (optional, requires tool)
# git secrets --scan

# 5. Check Python syntax
python -m py_compile **/*.py 2>/dev/null

# 6. View diff before commit
git diff --cached
```

## Files That Should Be Committed

✅ **Source Code**
- `analyzer/*.py`
- `config/*.py`
- `goldendataset/*.py`
- `knowledgegraph/*.py`
- `querygenerator/*.py`
- `rag_evaluator/*.py`
- `tests/*.py`
- `main.py`
- `ExampleQueries.py`

✅ **Configuration**
- `.env.example` (template only)
- `.gitignore`
- `pyproject.toml`
- `pytest.ini`
- `requirements.txt`

✅ **Documentation**
- `README.md`
- `SETUP.md`
- `PROJECT_STRUCTURE.md`
- `TEST_RESULTS.md`
- `tests/README.md`

✅ **Scripts**
- `run_tests.sh`
- `run_tests_uv.sh`

✅ **Assets**
- `example_knowledge_graph.png` (example only)

## Files That Should NOT Be Committed

❌ **Generated Files**
- `.coverage`, `coverage.xml`
- `htmlcov/`
- `.pytest_cache/`
- `generated_datasets/*.csv`
- `generated_datasets/*.png`
- `logs/*.log`

❌ **Environment**
- `.env` (actual credentials)
- `.venv/`, `venv*/`
- `uv.lock`
- `.python-version`

❌ **IDE**
- `.vscode/`
- `.idea/`
- `.claude/`
- `*.swp`, `*.swo`

❌ **Cache**
- `__pycache__/`
- `*.pyc`
- `.mypy_cache/`

❌ **Deprecated**
- `old_files/`

## Commit Message Template

```
<type>: <short summary>

<detailed description>

- Key change 1
- Key change 2
- Key change 3

Tests: <test status>
Coverage: <coverage percentage>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test additions/changes
- `refactor`: Code refactoring
- `style`: Code style changes
- `chore`: Maintenance tasks

### Example
```
feat: Add comprehensive logging and test suite

Added comprehensive logging throughout the codebase with rotating
file handlers and configurable log levels. Created 41 unit and
integration tests covering all major components.

- Added logging_config.py with rotating file handlers
- Enhanced all modules with debug/info/error logging
- Created 12 QueryAnalyzer tests
- Created 10 QueryGenerator tests
- Created 10 AnswerGenerator tests
- Created 9 integration tests
- Added pytest configuration and test runners

Tests: 41/41 passing
Coverage: 40.59% overall, 81.68% querygenerator
```

## Post-Commit Verification

After committing, verify:

```bash
# 1. Clone to a temp directory
git clone <repo-url> /tmp/test-clone
cd /tmp/test-clone

# 2. Verify setup works
cp .env.example .env
# Edit .env with test credentials

# 3. Install and test
uv sync --extra test
./run_tests_uv.sh

# 4. Cleanup
cd -
rm -rf /tmp/test-clone
```

## Notes

- This project uses UV for fast dependency management
- Tests are mocked and don't require real API keys
- Coverage reports are generated locally, not committed
- All modules are properly packaged with `__init__.py`
- Logging is configured centrally in `config/logging_config.py`
