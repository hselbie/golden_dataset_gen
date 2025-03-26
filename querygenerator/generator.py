from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
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
    def __init__(self, llm: ChatGoogleGenerativeAI, embeddings: GoogleGenerativeAIEmbeddings):
        super().__init__()
        self.llm = llm
        self.embeddings = embeddings
        self.analyzer = TextAnalyzer(embeddings)

    def generate_questions(self, elements: Dict[str, List[str]], num_questions: int = 5) -> List[str]:
        """Generate specified number of questions from the elements"""
        prompt = self._construct_question_prompt(elements, num_questions)
        response = self.llm.invoke(prompt)
        return self._parse_questions(response.content)

    def _construct_question_prompt(self, elements: Dict[str, List[str]], num_questions: int) -> str:
        """Construct prompt for question generation"""
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

    def _parse_questions(self, response: str) -> List[str]:
        """Parse response to extract questions"""
        questions = []
        for line in response.split('\n'):
            if line.strip().startswith("Question: "):
                questions.append(line.replace("Question: ", "").strip())
        return questions

class AnswerGenerator(VarConfig):
    def __init__(self, llm: ChatGoogleGenerativeAI):
        super().__init__()
        self.llm = llm
        self.vertex_client = VertexAIClient()

    def generate_answers(self, questions: List[str], source: str = "llm") -> List[Tuple[str, str]]:
        """Generate answers for questions using specified source"""
        qa_pairs = []
        for question in questions:
            answer = self._get_answer(question, source)
            qa_pairs.append((question, answer))
        return qa_pairs

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

        datastore_path = f"projects/{config.project}/locations/global/collections/default_collection/dataStores/{config.datastore_id}"

        # Create the Vertex AI Search tool
        vais_tool = Tool(
            retrieval=Retrieval(
                vertex_ai_search=VertexAISearch(
                    datastore=datastore_path
                )
            )
        )

        # Generate content with the tool in the proper config format
        response = client.models.generate_content(
            model=config.llm,
            contents=question,
            config=GenerateContentConfig(
                tools=[vais_tool]  # Tools are passed directly in the config
            )
        )

        return response.text

    def _get_google_search_answer(self, question: str) -> str:
        """Get answer using Google Search grounding"""
        vertexai.init(project=self.project, location=self.location)

        google_search_tool = Tool(google_search=GoogleSearch())
        response = client.models.generate_content(
            model=config.llm,
            contents=question,
            config=GenerateContentConfig(tools=[google_search_tool]))
        return response.text


    def _get_llm_answer(self, question: str) -> str:
        """Get answer directly from LLM"""
        prompt = f"Please provide a detailed and accurate answer to this question:\n{question}"
        response = self.llm.invoke(prompt)
        return response.content