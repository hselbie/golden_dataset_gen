from langchain_google_vertexai import ChatVertexAI
from langchain_google_vertexai import VertexAIEmbeddings
from typing import List, Dict, Tuple
import spacy

class QueryAnalyzer:
    def __init__(self):
        # Load English language model
        self.nlp = spacy.load("en_core_web_sm")
        
    def extract_elements(self, query: str) -> Dict[str, List[str]]:
        """
        Extract key elements from a query using spaCy
        Returns dictionary with entities, key phrases, and syntax elements
        """
        doc = self.nlp(query)
        
        elements = {
            'entities': [],
            'noun_phrases': [],
            'verbs': [],
            'concepts': []
        }
        
        # Extract named entities
        for ent in doc.ents:
            elements['entities'].append({
                'text': ent.text,
                'label': ent.label_
            })
            
        # Extract noun phrases
        for chunk in doc.noun_chunks:
            elements['noun_phrases'].append(chunk.text)
            
        # Extract main verbs
        for token in doc:
            if token.pos_ == "VERB":
                elements['verbs'].append(token.lemma_)
                
        # Extract key concepts using dependency parsing
        for token in doc:
            if token.dep_ in ['nsubj', 'dobj', 'pobj']:
                elements['concepts'].append(token.text)
                
        return elements

class QueryGenerator:
    def __init__(self, llm: ChatVertexAI, embeddings: VertexAIEmbeddings):
        self.llm = llm
        self.embeddings = embeddings
        
    def generate_query(self, elements: Dict[str, List[str]]) -> Tuple[str, str]:
        """
        Generate a new query and answer using the provided elements
        Returns tuple of (question, answer)
        """
        # Construct prompt using elements
        prompt = self._construct_prompt(elements)
        
        # Generate completion using Vertex AI
        response = self.llm.invoke(prompt)
        
        # Parse response to extract question and answer
        question, answer = self._parse_response(response.content)
        
        return question, answer
        
    def _construct_prompt(self, elements: Dict[str, List[str]]) -> str:
        """
        Construct prompt for query generation using provided elements
        """
        prompt = "Generate a question and detailed answer using some or all of these elements:\n\n"
        
        for element_type, items in elements.items():
            prompt += f"{element_type}:\n"
            for item in items:
                if isinstance(item, dict):
                    prompt += f"- {item['text']} ({item['label']})\n"
                else:
                    prompt += f"- {item}\n"
            prompt += "\n"
            
        prompt += """
Format the response as:
Question: [generated question]
Answer: [detailed answer]

Make sure the question is natural and the answer is comprehensive."""
        
        return prompt
    
    def _parse_response(self, response: str) -> Tuple[str, str]:
        """
        Parse generated response to extract question and answer
        Returns tuple of (question, answer)
        If answer is missing, returns a default message
        """
        parts = response.split('\n')
        question = ""
        answer = ""
        
        # Look for question and answer in response
        for part in parts:
            if part.strip().startswith("Question: "):
                question = part.replace("Question: ", "").strip()
            elif part.strip().startswith("Answer: "):
                answer = part.replace("Answer: ", "").strip()
        
        # Check if we have both parts
        if not question:
            question = "ERROR: No question generated"
        if not answer:
            answer = "Please try regenerating this response as no answer was provided."
        
        # Optional: Log missing parts for debugging
        if not answer or not question:
            print(f"Warning: Incomplete response received:")
            print(f"Original response: {response}")
            print(f"Parsed question: {question}")
            print(f"Parsed answer: {answer}")
        
        return question, answer