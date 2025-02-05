# Golden Dataset Generator

This tool helps generate golden datasets for question-answering tasks by leveraging Large Language Models (LLMs) and knowledge graph construction.  It starts with a set of seed questions, expands them using an LLM, and builds a knowledge graph to visualize the relationships between concepts.

## Installation

```bash
pip install spacy networkx pandas langchain-google-vertexai matplotlib
python -m spacy download en_core_web_sm
```

## Execute
### Steps
1. Come up with N number of seed queries and store them like this.

```
# Business Domain Queries
business_queries = [
    ("What are the key components of a SWOT analysis?", "bus1"),
    ("How does supply chain optimization work?", "bus2"),
    ("Explain the concept of market segmentation.", "bus3"),
    ("What are the principles of agile project management?", "bus4")
]
```
The first element in the tuple is the query, the second element is the id.

2. If using an single theme of seed queries loop through them and add them to the generator. Then use the generate to generate new queries passing the number of new queries into the `generate_dataset` method. 

```
for query, query_id in seed_queries:
    generator.add_seed_query(query, query_id)

visualizer = GraphVisualizer(generator.graph_builder.graph)
visualizer.visualize()

# Generate new dataset
dataset = generator.generate_dataset(num_queries=5)
print(dataset)

```

The dataset object is retrieved as a pandas df and can be exported using the pandas [to_csv](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html) method. 

## Advanced Execution
In the `ds_generator` there is a function to generate domain datasets, if you choose to use this, create seed datasets as before, example 

```
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

2. Execute the domain-specific dataset generation like this scientific_dataset, 

```
scientific_generator = generate_domain_dataset(

    generator=generator,
    domain_queries=scientific_queries, 
    domain_name="scientific", 
    num_queries=5,
)
```
This will generate a specific named dataset.