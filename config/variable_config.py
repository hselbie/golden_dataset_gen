import os
import logging
from dotenv import load_dotenv
from google import genai

logger = logging.getLogger(__name__)


class VarConfig:
    """Configuration class for environment variables and API clients."""

    def __init__(self):
        load_dotenv()
        logger.info("Loading configuration from environment variables")

        self.project = os.getenv("PROJECT")
        self.embedding_model = os.getenv("EMBEDDING_MODEL")
        self.location = os.getenv("LOCATION")
        self.llm = os.getenv("LLM")
        self.datastore_id = os.getenv("DATASTORE_ID")
        self.grounding_enabled = int(os.getenv("GROUNDING", 0))
        self.google_api_key_ = os.getenv("GAPIKEY")

        if not self.project or not self.location:
            logger.warning("PROJECT or LOCATION not set in environment variables")

        try:
            self.client = genai.Client(
                vertexai=True, project=self.project, location=self.location
            )
            logger.info(f"Initialized genai client for project: {self.project}")
        except Exception as e:
            logger.error(f"Failed to initialize genai client: {e}")
            raise


class GroundingConfig(VarConfig):
    """Configuration for grounding with Vertex AI Search."""

    def __init__(self):
        super().__init__()
        logger.info("Initializing GroundingConfig")

    def initialize_grounding(self):
        """
        Initialize grounding tools for Vertex AI.

        Returns:
            Tuple of (model, tool) for grounded content generation
        """
        if not self.grounding_enabled:
            logger.warning("Grounding is not enabled")
            return None, None

        try:
            from vertexai.preview.generative_models import (
                GenerativeModel,
                Tool,
                grounding,
            )

            logger.info(f"Initializing grounding with datastore: {self.datastore_id}")

            model = GenerativeModel(self.llm)

            tool = Tool.from_retrieval(
                grounding.Retrieval(
                    grounding.VertexAISearch(
                        datastore=self.datastore_id,
                        project=self.project,
                        location="global",
                    )
                )
            )

            logger.info("Grounding initialized successfully")
            return model, tool
        except Exception as e:
            logger.error(f"Failed to initialize grounding: {e}")
            raise
