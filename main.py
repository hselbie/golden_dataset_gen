import pandas as pd
from typing import List, Dict, Tuple
from goldendataset.ds_generator import GoldenDatasetGenerator
from knowledgegraph.builder import GraphVisualizer


# Example usage:
LOCATION = "us-central1"
PROJECT = "zinc-forge-302418"
LLM = "gemini-1.5-flash-002"
MODEL = "textembedding-gecko@003"

generator = GoldenDatasetGenerator(
    project=PROJECT,
    location=LOCATION,
    llm_model=LLM,
    embedding_model=MODEL
)

# Add seed queries
seed_queries = [
    ("My laptop charger stopped working. Can I expense a new charger?", "q1"),
    ("Hello, are we able to expense our cell phone?", "q2"),
    ("I lost/misplaced my receipt, how can I submit the expense?", "q3"),
    ("I'm having an issue with hotel itemizations as a deposit was taken at time of booking. can someone help?", "q4"),
    ("How do I submit corporate credit card transactions?", "q5"),
    ("I can't find the mileage expense type", "q6")
]

for query, query_id in seed_queries:
    generator.add_seed_query(query, query_id)

visualizer = GraphVisualizer(generator.graph_builder.graph)
visualizer.visualize()

# Generate new dataset
dataset = generator.generate_dataset(num_queries=5)
print(dataset)