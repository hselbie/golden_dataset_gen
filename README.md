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

To get started, install the necessary dependencies:

```bash
pip install spacy networkx pandas langchain-google-vertexai matplotlib
python -m spacy download en_core_web_sm
```

## Usage

### Basic Execution

1.  **Define Seed Queries:** Create a list of seed queries, each represented as a tuple containing the question and a unique identifier.

    ```python
    # Example Seed Queries
    seed_queries = [
        ("What are the key components of a SWOT analysis?", "bus1"),
        ("How does supply chain optimization work?", "bus2"),
        ("Explain the concept of market segmentation.", "bus3"),
        ("What are the principles of agile project management?", "bus4")
    ]
    ```

    *   The first element of the tuple is the query string.
    *   The second element is a unique identifier for the query.

2.  **Add Seed Queries and Generate Dataset:** Iterate through the seed queries, add them to the generator, and then generate a new dataset.  The `generate_dataset` method takes the desired number of new queries as input.

    ```python
    from your_module import Generator, GraphVisualizer # Replace your_module

    generator = Generator() # Initialize your generator class

    for query, query_id in seed_queries:
        generator.add_seed_query(query, query_id)

    visualizer = GraphVisualizer(generator.graph_builder.graph)
    visualizer.visualize()

    # Generate new dataset
    dataset = generator.generate_dataset(num_queries=5)
    print(dataset)
    ```

    The `dataset` object is returned as a pandas DataFrame.  You can export it to a CSV file using the pandas [`to_csv`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html) method.

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

