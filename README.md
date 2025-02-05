# Golden Dataset Generator

This tool helps generate golden datasets for question-answering tasks by leveraging Large Language Models (LLMs) and knowledge graph construction.  It starts with a set of seed questions, expands them using an LLM, and builds a knowledge graph to visualize the relationships between concepts.

## Installation

```bash
pip install spacy networkx pandas langchain-google-vertexai matplotlib
python -m spacy download en_core_web_sm
