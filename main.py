import os
from typing import List, Dict, Tuple
import pandas as pd
from config.variable_config import VarConfig 
from langchain_google_vertexai import ChatVertexAI, VertexAIEmbeddings
from querygenerator.generator import QueryGenerator

# Create output directory if it doesn't exist
os.makedirs('generated_datasets', exist_ok=True)

global_variables = VarConfig()

def initialize_generator():
    """Initialize the query generator with required components"""
    llm = ChatVertexAI(model_name=global_variables.llm)
    embeddings = VertexAIEmbeddings(model_name=global_variables.embedding_model)
    return QueryGenerator(llm=llm, embeddings=embeddings)

# Initialize query generator
generator = initialize_generator()

# Define seed queries with their IDs
seed_queries = [
    ("What are some popular attractions to visit in Seattle?", "q1"),
    ("What restaurants serve vegan food in Austin?", "q2"),
    ("What would be a good teambuilding outdoor activity in Manhattan?", "q3"),
    ("Where is the nearest local coffee shop to my hotel?", "q4")
]

# Domain-specific queries
domains = {
    "scientific": [
        ("What is the role of mitochondria in cellular respiration?", "sci1"),
        ("How does quantum entanglement work in physics?", "sci2"),
        ("Explain the process of DNA replication.", "sci3"),
        ("What are the laws of thermodynamics?", "sci4")
    ],
    "technology": [
        ("How do microprocessors handle parallel processing?", "tech1"),
        ("What are the principles of cloud computing architecture?", "tech2"),
        ("Explain how blockchain maintains data integrity?", "tech3"),
        ("What is the difference between HTTP and HTTPS?", "tech4")
    ],
    "business": [
        ("What are the key components of a SWOT analysis?", "bus1"),
        ("How does supply chain optimization work?", "bus2"),
        ("Explain the concept of market segmentation?", "bus3"),
        ("What are the principles of agile project management?", "bus4")
    ]
}


def generate_domain_dataset(queries: List[Tuple[str, str]], domain_name: str, num_questions: int = 15):
    """Generate dataset for a specific domain"""
    dataset = []
    
    for query, query_id in queries:
        # Extract elements and generate questions
        elements = generator.analyzer.extract_elements(query)
        questions = generator.generate_questions(elements, num_questions=num_questions)
        
        # Generate answers using different sources
        # qa_pairs_datastore = generator.generate_answers(questions, source="datastore")
        qa_pairs_google = generator.generate_answers(questions, source="google")
        qa_pairs_llm = generator.generate_answers(questions, source="llm")
        
        # Combine results
        for (q, a_gs), (_, a_llm) in zip(qa_pairs_google, qa_pairs_llm):
            dataset.append({
                'query_id': query_id,
                'original_query': query,
                'generated_question': q,
                'google_search_answer': a_gs,
                'llm_answer': a_llm,
                'domain': domain_name
            })
    
    return pd.DataFrame(dataset)

# # Generate datasets for each domain
# datasets = {}
# for domain_name, domain_queries in domains.items():
#     print(f"Generating dataset for {domain_name} domain...")
#     datasets[domain_name] = generate_domain_dataset(
#         queries=domain_queries,
#         domain_name=domain_name,
#         num_questions=3
#     )
#     # Save domain-specific dataset
#     datasets[domain_name].to_csv(f'generated_datasets/{domain_name}_dataset.csv', index=False)

# Generate general dataset
print("Generating general dataset...")
general_dataset = generate_domain_dataset(
    queries=seed_queries,
    domain_name="general",
    num_questions=15
)
general_dataset.to_csv('generated_datasets/general_dataset.csv', index=False)
print('complete')

# Visualize the results
# for domain_name, dataset in datasets.items():
#     print(f"\n{domain_name.capitalize()} Dataset Summary:")
#     print(f"Total questions generated: {len(dataset)}")
#     print(dataset[['query_id', 'generated_question']].head())