# Golden Dataset Generator

High-quality golden datasets are essential for objectively evaluating and improving Retrieval-Augmented Generation (RAG) and search systems.  However, creating these datasets is traditionally expensive and time-consuming. This tool tackles that challenge, empowering developers to build more accurate, robust, and trustworthy RAG/search applications by streamlining the generation process.

**Why are Golden Datasets Important?** They provide:

*   **Objective Truth:** A reliable benchmark for measuring accuracy and relevance.
*   **Targeted Analysis:** Allows separate evaluation of retrieval and generation components.
*   **Iterative Improvement:** Enables data-driven optimization and error correction.
*   **Regression Prevention:** Detects performance degradation after changes.
*   **Real-World Representation:** Mirrors real-world scenarios for relevant evaluation.

**How This Tool Works:**

This tool facilitates the creation of golden datasets for question-answering tasks by combining the power of Large Language Models (LLMs) and knowledge graph construction. Starting with seed questions, the tool uses an LLM to expand the dataset.  A knowledge graph is built to visualize the relationships between concepts, aiding in data quality and coverage analysis.

Example knowledge graph can be seen [here](https://github.com/hselbie/golden_dataset_gen/blob/main/generated_datasets/general_.png).

## Installation

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Linux/Mac
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

3. Configure environment variables:
   Create a `.env` file in the root directory with the following variables:
```plaintext
GOOGLE_CLOUD_PROJECT=your-project-id
VERTEX_LOCATION=your-location  # e.g., us-central1
VERTEX_MODEL=text-bison@001
EMBEDDING_MODEL=textembedding-gecko@001
DATASTORE_ID=your-datastore-id  # Optional, for datastore integration
```

## Usage

### Setting Up Example Queries

1. Create or modify `ExampleQueries.py` in the root directory:
```python
# filepath: ExampleQueries.py
seed_queries = [
    ("What are the key components of a SWOT analysis?", "bus1"),
    ("How does supply chain optimization work?", "bus2"),
    # Add more queries as (question, unique_id) tuples
]
```

### Basic Usage

Generate a dataset using the default settings:
```bash
python main.py
```

### Advanced Usage

Generate dataset with custom parameters:
```bash
python main.py \
  --questions "What is Python?" "How does Git work?" \
  --domain technology \
  --num-questions 10 \
  --output custom_datasets
```

Available command-line arguments:
- `--questions`: List of input questions to process
- `--domain`: Domain name for the dataset (default: "general")
- `--num-questions`: Number of questions to generate per input (default: 15)
- `--output`: Output directory for generated datasets (default: "generated_datasets")
- `--datastore-id`: Override the datastore ID from .env file

### Output

The tool generates:
1. A CSV file containing the generated dataset
2. A knowledge graph visualization (saved as PNG)

Generated files are stored in the `generated_datasets` directory (or custom output directory if specified).

## Advanced Usage: Domain-Specific Dataset Generation

The `ds_generator` module provides a function for generating domain-specific datasets. To use this feature, prepare seed datasets for each domain you want to target.

1.  **Create Domain-Specific Seed Queries:**  Define seed query lists for each domain.

    ```python
    # Scientific Domain Queries
    scientific_queries = [
        ("What is the role of mitochondria in cellular respiration?", "sci1"),
        ("How does quantum entanglement work in physics?", "sci2"),
        ("Explain the process of DNA replication.", "sci3"),
        ("What are the laws of thermodynamics?", "sci4")
    ]

    # Technology Domain Queries
    tech_queries = [
        ("How do microprocessors handle parallel processing?", "tech1"),
        ("What are the principles of cloud computing architecture?", "tech2"),
        ("Explain how blockchain maintains data integrity.", "tech3"),
        ("What is the difference between HTTP and HTTPS?", "tech4")
    ]

    # Business Domain Queries
    business_queries = [
        ("What are the key components of a SWOT analysis?", "bus1"),
        ("How does supply chain optimization work?", "bus2"),
        ("Explain the concept of market segmentation.", "bus3"),
        ("What are the principles of agile project management?", "bus4")
    ]
    ```

2.  **Generate Domain Datasets:** Call the `generate_domain_dataset` function for each domain.

    ```python
    from your_module import generate_domain_dataset, Generator # Replace your_module

    generator = Generator() # Initialize your generator class


    scientific_dataset = generate_domain_dataset(
        generator=generator,
        domain_queries=scientific_queries,
        domain_name="scientific",
        num_queries=5,
    )
    ```

    This will generate a dataset specific to the "scientific" domain, named "scientific_dataset".

