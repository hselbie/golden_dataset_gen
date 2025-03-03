import os
import ExampleQueries 
from typing import List, Dict, Tuple
import pandas as pd
from config.variable_config import VarConfig 
from langchain_google_vertexai import ChatVertexAI, VertexAIEmbeddings
from querygenerator.generator import QueryGenerator, QueryAnalyzer

# Create output directory if it doesn't exist
os.makedirs('generated_datasets', exist_ok=True)

global_variables = VarConfig()

def generate_domain_dataset(queries: List[Tuple[str, str]], domain_name: str, num_questions: int = 15):
    """Generate dataset for a specific domain"""
    dataset = []
    analyzer = QueryAnalyzer()  # Create an instance of QueryAnalyzer
    generator = initialize_generator()
    
    for query, query_id in queries:
        # Extract elements and generate questions
        elements = analyzer.extract_elements(query)  # Use instance method
        questions = generator.generate_questions(elements, num_questions=num_questions)
        
        # Generate answers using different sources
        # qa_pairs_datastore = analyzer.generate_answers(questions, source="datastore")
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

def initialize_generator():
    """Initialize the query generator with required components"""
    llm = ChatVertexAI(model_name=global_variables.llm)
    embeddings = VertexAIEmbeddings(model_name=global_variables.embedding_model)
    return QueryGenerator(llm=llm, embeddings=embeddings)

if __name__ == "__main__":
    # Generate general dataset
    print("Generating general dataset...")
    general_dataset = generate_domain_dataset(
        queries=ExampleQueries.seed_queries,
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