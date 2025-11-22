import os
import logging
from typing import List, Dict, Tuple, Optional

import spacy
import vertexai
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from vertexai.preview.generative_models import (
    GenerationConfig,
    GenerativeModel,
    Tool,
    grounding,
    HarmCategory,
    HarmBlockThreshold,
)
from google.genai.types import (
    GenerateContentConfig,
    GoogleSearch,
    Retrieval,
    VertexAISearch,
)

from config.variable_config import VarConfig
from analyzer.text_analyzer import TextAnalyzer

logger = logging.getLogger(__name__)


# Singleton for Vertex AI initialization
class VertexAIClient(VarConfig):
    """Singleton client for Vertex AI initialization."""

    def __init__(self):
        super().__init__()
        self._initialized = False

        if not self._initialized:
            try:
                vertexai.init(project=self.project, location=self.location)
                self._initialized = True
                logger.info(f"Vertex AI initialized for project: {self.project}")
            except Exception as e:
                logger.error(f"Failed to initialize Vertex AI: {e}")
                raise


class QueryAnalyzer:
    """Analyzer for extracting semantic elements from queries using spaCy."""

    def __init__(self):
        try:
            # Load English language model
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("Loaded spaCy en_core_web_sm model")
        except Exception as e:
            logger.error(f"Failed to load spaCy model: {e}")
            raise

    def extract_elements(self, query: str) -> Dict[str, List[str]]:
        """
        Extract key elements from a query using spaCy.

        Args:
            query: The input query string

        Returns:
            Dictionary with entities, key phrases, and syntax elements
        """
        logger.debug(f"Extracting elements from query: {query}")

        try:
            doc = self.nlp(query)

            elements = {"entities": [], "noun_phrases": [], "verbs": [], "concepts": []}

            # Extract named entities
            for ent in doc.ents:
                elements["entities"].append({"text": ent.text, "label": ent.label_})

            # Extract noun phrases
            for chunk in doc.noun_chunks:
                elements["noun_phrases"].append(chunk.text)

            # Extract main verbs
            for token in doc:
                if token.pos_ == "VERB":
                    elements["verbs"].append(token.lemma_)

            # Extract key concepts using dependency parsing
            for token in doc:
                if token.dep_ in ["nsubj", "dobj", "pobj"]:
                    elements["concepts"].append(token.text)

            logger.debug(
                f"Extracted {len(elements['entities'])} entities, "
                f"{len(elements['noun_phrases'])} noun phrases, "
                f"{len(elements['verbs'])} verbs, "
                f"{len(elements['concepts'])} concepts"
            )

            return elements
        except Exception as e:
            logger.error(f"Error extracting elements from query: {e}")
            raise


class QueryGenerator(VarConfig):
    """Generator for creating questions from extracted query elements."""

    def __init__(
        self, llm: ChatGoogleGenerativeAI, embeddings: GoogleGenerativeAIEmbeddings
    ):
        super().__init__()
        self.llm = llm
        self.embeddings = embeddings
        self.analyzer = TextAnalyzer(embeddings)
        logger.info("QueryGenerator initialized")

    def generate_questions(
        self, elements: Dict[str, List[str]], num_questions: int = 5
    ) -> List[str]:
        """
        Generate specified number of questions from the elements.

        Args:
            elements: Dictionary of extracted query elements
            num_questions: Number of questions to generate

        Returns:
            List of generated questions
        """
        logger.info(f"Generating {num_questions} questions from elements")
        logger.debug(f"Elements: {elements}")

        try:
            prompt = self._construct_question_prompt(elements, num_questions)
            response = self.llm.invoke(prompt)
            questions = self._parse_questions(response.content)
            logger.info(f"Successfully generated {len(questions)} questions")
            return questions
        except Exception as e:
            logger.error(f"Error generating questions: {e}")
            raise

    def _construct_question_prompt(
        self, elements: Dict[str, List[str]], num_questions: int
    ) -> str:
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
        for line in response.split("\n"):
            if line.strip().startswith("Question: "):
                questions.append(line.replace("Question: ", "").strip())
        return questions


class AnswerGenerator(VarConfig):
    """Generator for creating answers from various sources (LLM, datastore, Google Search)."""

    def __init__(self, llm: ChatGoogleGenerativeAI):
        super().__init__()
        self.llm = llm
        self.vertex_client = VertexAIClient()
        logger.info("AnswerGenerator initialized")

    def generate_answers(
        self, questions: List[str], source: str = "llm"
    ) -> List[Tuple[str, str]]:
        """
        Generate answers for questions using specified source.

        Args:
            questions: List of questions to answer
            source: Source to use ('llm', 'datastore', or 'google')

        Returns:
            List of (question, answer) tuples
        """
        logger.info(
            f"Generating answers for {len(questions)} questions using source: {source}"
        )

        qa_pairs = []
        for idx, question in enumerate(questions):
            try:
                logger.debug(
                    f"Processing question {idx + 1}/{len(questions)}: {question}"
                )
                answer = self._get_answer(question, source)
                qa_pairs.append((question, answer))
            except Exception as e:
                logger.error(f"Error answering question '{question}': {e}")
                qa_pairs.append((question, f"Error: {str(e)}"))

        logger.info(f"Successfully generated {len(qa_pairs)} Q&A pairs")
        return qa_pairs

    def _get_answer(self, question: str, source: str) -> str:
        """
        Get answer from specified source.

        Args:
            question: The question to answer
            source: The source to use

        Returns:
            Answer string
        """
        if source == "datastore":
            return self._get_datastore_answer(question)
        elif source == "google":
            return self._get_google_search_answer(question)
        else:
            return self._get_llm_answer(question)

    def _get_datastore_answer(self, question: str) -> str:
        """Get answer from datastore using grounding"""
        logger.debug(f"Getting datastore answer for: {question}")

        try:
            datastore_path = f"projects/{self.project}/locations/global/collections/default_collection/dataStores/{self.datastore_id}"

            # Create the Vertex AI Search tool
            vais_tool = Retrieval(
                vertex_ai_search=VertexAISearch(datastore=datastore_path)
            )

            # Generate content with the tool in the proper config format
            response = self.client.models.generate_content(
                model=self.llm,
                contents=question,
                config=GenerateContentConfig(tools=[vais_tool]),
            )

            logger.debug(f"Datastore answer received (length: {len(response.text)})")
            return response.text
        except Exception as e:
            logger.error(f"Error getting datastore answer: {e}")
            raise

    def _get_google_search_answer(self, question: str) -> str:
        """Get answer using Google Search grounding"""
        logger.debug(f"Getting Google Search answer for: {question}")

        try:
            google_search_tool = GoogleSearch()
            response = self.client.models.generate_content(
                model=self.llm,
                contents=question,
                config=GenerateContentConfig(tools=[google_search_tool]),
            )

            logger.debug(
                f"Google Search answer received (length: {len(response.text)})"
            )
            return response.text
        except Exception as e:
            logger.error(f"Error getting Google Search answer: {e}")
            raise

    def _get_llm_answer(self, question: str) -> str:
        """
        Get answer directly from LLM.

        Args:
            question: The question to answer

        Returns:
            Answer from LLM
        """
        logger.debug(f"Getting LLM answer for: {question}")
        try:
            prompt = f"Please provide a detailed and accurate answer to this question:\n{question}"
            response = self.llm.invoke(prompt)
            logger.debug(f"LLM answer received (length: {len(response.content)})")
            return response.content
        except Exception as e:
            logger.error(f"Error getting LLM answer: {e}")
            raise
