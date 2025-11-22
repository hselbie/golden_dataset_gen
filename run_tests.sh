#!/bin/bash

# UV-based test runner script for query expansion project

set -e  # Exit on error

echo "========================================="
echo "Query Expansion - UV Test Runner"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "${RED}UV not found. Please install UV first:${NC}"
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Ensure test dependencies are installed
echo "${YELLOW}Ensuring test dependencies are installed...${NC}"
uv sync --extra test

# Download spaCy model if needed
echo "${YELLOW}Checking spaCy model...${NC}"
uv run python -m spacy download en_core_web_sm 2>/dev/null || true

echo ""

# Run tests with different options based on arguments
if [ "$1" == "unit" ]; then
    echo "${GREEN}Running unit tests only...${NC}"
    uv run pytest tests/ -m unit -v

elif [ "$1" == "integration" ]; then
    echo "${GREEN}Running integration tests only...${NC}"
    uv run pytest tests/ -m integration -v

elif [ "$1" == "coverage" ]; then
    echo "${GREEN}Running tests with coverage report...${NC}"
    uv run pytest tests/ --cov --cov-report=html --cov-report=term

elif [ "$1" == "quick" ]; then
    echo "${GREEN}Running quick tests (no slow tests)...${NC}"
    uv run pytest tests/ -m "not slow" -v

elif [ "$1" == "verbose" ]; then
    echo "${GREEN}Running all tests with verbose output...${NC}"
    uv run pytest tests/ -vv --tb=long

elif [ "$1" == "watch" ]; then
    echo "${GREEN}Running tests in watch mode...${NC}"
    uv run pytest-watch tests/ -v

else
    echo "${GREEN}Running all tests...${NC}"
    uv run pytest tests/ -v
fi

echo ""
echo "${GREEN}=========================================${NC}"
echo "${GREEN}Test run complete!${NC}"
echo "${GREEN}=========================================${NC}"
