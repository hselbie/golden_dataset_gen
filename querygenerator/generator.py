from langchain_google_vertexai import ChatVertexAI
from langchain_google_vertexai import VertexAIEmbeddings
from typing import List, Dict, Tuple, Optional
import spacy
from vertexai.preview.generative_models import (
    GenerationConfig,
    GenerativeModel,
    Tool,
    grounding,
    HarmCategory,
    HarmBlockThreshold
)
from config.variable_config import VarConfig
import os
from analyzer.text_analyzer import TextAnalyzer
import vertexai

# Singleton for Vertex AI initialization
class VertexAIClient(VarConfig):
    def __init__(self):
        super().__init__()
        self._initialized = False

        if not self._initialized:
            vertexai.init(project=self.project, location=self.location)
            self._initialized = True
    
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

class QueryGenerator(VarConfig):
    def __init__(self, llm: ChatVertexAI, embeddings: VertexAIEmbeddings):
        super().__init__()
        self.llm = llm
        self.embeddings = embeddings
        self.analyzer = TextAnalyzer(embeddings)
        self.vertex_client = VertexAIClient()
        

    def generate_questions(self, elements: Dict[str, List[str]], num_questions: int = 5) -> List[str]:
        """
        Generate specified number of questions from the elements
        
        Args:
            elements: Dictionary of elements to use for question generation
            num_questions: Number of questions to generate (default: 5)
        
        Returns:
            List of generated questions
        """
        prompt = self._construct_question_prompt(elements, num_questions)
        response = self.llm.invoke(prompt)
        return self._parse_questions(response.content)

    def generate_answers(self, questions: List[str], source: str = "llm") -> List[Tuple[str, str]]:
        """Generate answers for questions using specified source"""
        qa_pairs = []
        for question in questions:
            answer = self._get_answer(question, source)
            qa_pairs.append((question, answer))
        return qa_pairs

    def _construct_question_prompt(self, elements: Dict[str, List[str]], num_questions: int) -> str:
        """
        Construct prompt for question generation
        
        Args:
            elements: Dictionary of elements to use for question generation
            num_questions: Number of questions to generate
        """
        prompt = f"Generate {num_questions} natural questions using some or all of these elements:\n\n"
        
        for element_type, items in elements.items():
            prompt += f"{element_type}:\n"
            for item in items:
                if isinstance(item, dict):
                    prompt += f"- {item['text']} ({item['label']})\n"
                else:
                    prompt += f"- {item}\n"
            prompt += "\n"
            
        prompt += """
Format each question on a new line starting with 'Question: '
Make sure the questions are natural and diverse."""
        
        return prompt

    def _get_answer(self, question: str, source: str) -> str:
        """Get answer from specified source"""
        if source == "datastore":
            return self._get_datastore_answer(question)
        elif source == "google":
            return self._get_google_search_answer(question)
        else:
            return self._get_llm_answer(question)

    def _get_datastore_answer(self, question: str) -> str:
        """Get answer from datastore using grounding"""
        vertexai.init(project=self.project, location=self.location)

        model = GenerativeModel("gemini-1.5-flash-001")

        tool = Tool.from_retrieval(
            grounding.Retrieval(
                grounding.VertexAISearch(
                    datastore=self.datastore_id,
                    project=self.project,
                    location="global",
                )
            )
        )
        response = model.generate_content(
            question,
            tools=[tool],
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                    },
            generation_config=GenerationConfig(
                temperature=0.0,
            ),
        )


        return response.text

    def _get_google_search_answer(self, question: str) -> str:
        """Get answer using Google Search grounding"""
        # Get model from singleton to ensure proper initialization
        vertexai.init(project=self.project, location=self.location)
        model = self.vertex_client.get_generative_model()
        
        tool = Tool.from_google_search_retrieval(
            grounding.GoogleSearchRetrieval(
                dynamic_retrieval_config=grounding.DynamicRetrievalConfig(
                    dynamic_threshold=0.7,
                )
            )
        )
        response = model.generate_content(
            question,
            tools=[tool],
            generation_config=GenerationConfig(temperature=0.0)
        )
        return response.text

    def _get_llm_answer(self, question: str) -> str:
        """Get answer directly from LLM"""
        prompt = f"Please provide a detailed and accurate answer to this question:\n{question}"
        response = self.llm.invoke(prompt)
        return response.content

    def _parse_questions(self, response: str) -> List[str]:
        """Parse response to extract questions"""
        questions = []
        for line in response.split('\n'):
            if line.strip().startswith("Question: "):
                questions.append(line.replace("Question: ", "").strip())
        return questions