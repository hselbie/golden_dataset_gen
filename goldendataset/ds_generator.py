from langchain_google_vertexai import ChatVertexAI
from langchain_google_vertexai import VertexAIEmbeddings
from querygenerator.generator import QueryAnalyzer, QueryGenerator
from knowledgegraph.builder import KnowledgeGraphBuilder
from knowledgegraph.builder import GraphVisualizer
import random
import vertexai
import pandas as pd

class GoldenDatasetGenerator:
    def __init__(self, project: str, location: str, llm_model: str, embedding_model: str):
        # Initialize Vertex AI
        vertexai.init(project=project, location=location)
        
        # Initialize components
        self.analyzer = QueryAnalyzer()
        self.graph_builder = KnowledgeGraphBuilder()
        
        # Setup LLM and embeddings
        llm = ChatVertexAI(
            model_name=llm_model,
            location=location,
            temperature=0,
            max_output_tokens=1024
        )
        
        embeddings = VertexAIEmbeddings(
            model_name=embedding_model,
            location=location
        )
        
        self.generator = QueryGenerator(llm, embeddings)
        
    def add_seed_query(self, query: str, query_id: str):
        """
        Process a seed query and add its elements to the knowledge graph
        """
        elements = self.analyzer.extract_elements(query)
        self.graph_builder.add_query_elements(query_id, elements)
        
    def generate_dataset(self, num_queries: int) -> pd.DataFrame:
        """
        Generate new queries using the knowledge graph
        Returns DataFrame with questions and answers
        """
        dataset = []
        
        for _ in range(num_queries):
            # Get random combinations of related elements
            elements = {}
            
            # Safely sample elements, taking as many as available up to the desired number
            for element_type, count in [
                ('entities', 2),
                ('noun_phrases', 2),
                ('verbs', 1),
                ('concepts', 2)
            ]:
                available_elements = self.graph_builder.get_related_elements(element_type)
                sample_size = min(len(available_elements), count)
                elements[element_type] = random.sample(available_elements, sample_size) if available_elements else []
            
            # Generate new query
            question, answer = self.generator.generate_query(elements)
            
            dataset.append({
                'question': question,
                'answer': answer
            })

            df = pd.DataFrame(dataset)
            
        return df

def generate_domain_dataset(generator, domain_queries, domain_name, num_queries=5):
    """
    Generate domain-specific datasets using specialized seed queries
    """
    # Initialize domain-specific generator
    domain_generator = generator    
    
    print(f"\nProcessing {domain_name} domain:")
    
    # Add domain-specific seed queries
    for query, query_id in domain_queries:
        print(f"Adding seed query: {query_id}")
        domain_generator.add_seed_query(query, query_id)
    
    # Generate domain-specific dataset
    dataset = domain_generator.generate_dataset(num_queries=num_queries)
    
    # Save domain-specific results
    output_file = f'generated_datasets/{domain_name}_dataset.csv'
    print(f"Saving dataset to {output_file}")
    dataset.to_csv(output_file, index=False)
    
    # Visualize domain knowledge graph
    print(f"\nGenerating knowledge graph for {domain_name} domain")
    visualizer = GraphVisualizer(domain_generator.graph_builder.graph)
    visualizer.visualize()
    
    return dataset, domain_generator