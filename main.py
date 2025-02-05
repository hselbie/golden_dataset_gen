import pandas as pd
import os
from typing import List, Dict, Tuple
from goldendataset.ds_generator import GoldenDatasetGenerator, generate_domain_dataset
from knowledgegraph.builder import GraphVisualizer
import os
from dotenv import load_dotenv

load_dotenv()
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
DATASTORE_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")

# Project Config
LOCATION = os.getenv("LOCATION")
PROJECT = os.getenv("PROJECT")
LLM = os.getenv("LLM")
MODEL = os.getenv("MODEL")

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

# Generate datasets for each domain
scientific_dataset, scientific_generator = generate_domain_dataset(
    generator=generator,
    domain_queries=scientific_queries, 
    domain_name="scientific", 
    num_queries=5,
)

tech_dataset, tech_generator = generate_domain_dataset(
    generator=generator,
    domain_queries=tech_queries, 
    domain_name="technology", 
    num_queries=5
)

business_dataset, business_generator = generate_domain_dataset(
    generator=generator,
    domain_queries=business_queries,
    domain_name="business", 
    num_queries=5
)

# for query, query_id in seed_queries:
#     generator.add_seed_query(query, query_id)

# visualizer = GraphVisualizer(generator.graph_builder.graph)
# visualizer.visualize()

# # Generate new dataset
# dataset = generator.generate_dataset(num_queries=5)
# print(dataset)