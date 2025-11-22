"""
Component factory for creating common components with consistent configuration.

This module centralizes the initialization of LLMs, embeddings, and other
frequently used components to eliminate code duplication and ensure consistency.
"""

import logging
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from config.variable_config import VarConfig

logger = logging.getLogger(__name__)


def create_llm(
    config: VarConfig = None,
    model_name: str = None,
    temperature: float = 0,
    max_output_tokens: int = 1024,
    location: str = None,
    google_api_key: str = None,
) -> ChatGoogleGenerativeAI:
    """
    Create a ChatGoogleGenerativeAI instance with consistent configuration.

    Args:
        config: VarConfig instance to get default values from (optional)
        model_name: Override model name (uses config.llm if not provided)
        temperature: Temperature for generation (default: 0)
        max_output_tokens: Maximum tokens to generate (default: 1024)
        location: Location for the model (uses config.location if not provided)
        google_api_key: API key (uses config.google_api_key_ if not provided)

    Returns:
        Configured ChatGoogleGenerativeAI instance
    """
    # Use config if provided, otherwise create a new one
    if config is None:
        config = VarConfig()

    # Use provided values or fall back to config
    final_model_name = model_name or config.llm
    final_location = location or config.location
    final_api_key = google_api_key or config.google_api_key_

    logger.info(f"Creating LLM with model: {final_model_name}")

    # Build kwargs conditionally
    kwargs = {
        "model_name": final_model_name,
        "temperature": temperature,
        "max_output_tokens": max_output_tokens,
    }

    if final_location:
        kwargs["location"] = final_location

    if final_api_key:
        kwargs["google_api_key"] = final_api_key

    return ChatGoogleGenerativeAI(**kwargs)


def create_embeddings(
    config: VarConfig = None, model_name: str = None, location: str = None
) -> GoogleGenerativeAIEmbeddings:
    """
    Create a GoogleGenerativeAIEmbeddings instance with consistent configuration.

    Args:
        config: VarConfig instance to get default values from (optional)
        model_name: Override model name (uses config.embedding_model if not provided)
        location: Location for the model (uses config.location if not provided)

    Returns:
        Configured GoogleGenerativeAIEmbeddings instance
    """
    # Use config if provided, otherwise create a new one
    if config is None:
        config = VarConfig()

    # Use provided values or fall back to config
    final_model_name = model_name or config.embedding_model
    final_location = location or config.location

    logger.info(f"Creating embeddings with model: {final_model_name}")

    # Build kwargs conditionally
    kwargs = {"model_name": final_model_name}

    if final_location:
        kwargs["location"] = final_location

    return GoogleGenerativeAIEmbeddings(**kwargs)


def create_query_analyzer():
    """
    Create a QueryAnalyzer instance.

    Returns:
        Configured QueryAnalyzer instance
    """
    from querygenerator.generator import QueryAnalyzer

    logger.info("Creating QueryAnalyzer")
    return QueryAnalyzer()


def create_query_generator(
    config: VarConfig = None,
    llm: ChatGoogleGenerativeAI = None,
    embeddings: GoogleGenerativeAIEmbeddings = None,
):
    """
    Create a QueryGenerator instance with LLM and embeddings.

    Args:
        config: VarConfig instance for creating components (optional)
        llm: Pre-configured LLM (will create one if not provided)
        embeddings: Pre-configured embeddings (will create one if not provided)

    Returns:
        Configured QueryGenerator instance
    """
    from querygenerator.generator import QueryGenerator

    logger.info("Creating QueryGenerator")

    # Create components if not provided
    if llm is None:
        llm = create_llm(config)

    if embeddings is None:
        embeddings = create_embeddings(config)

    return QueryGenerator(llm=llm, embeddings=embeddings)


def create_answer_generator(
    config: VarConfig = None, llm: ChatGoogleGenerativeAI = None
):
    """
    Create an AnswerGenerator instance with LLM.

    Args:
        config: VarConfig instance for creating components (optional)
        llm: Pre-configured LLM (will create one if not provided)

    Returns:
        Configured AnswerGenerator instance
    """
    from querygenerator.generator import AnswerGenerator

    logger.info("Creating AnswerGenerator")

    # Create LLM if not provided
    if llm is None:
        llm = create_llm(config)

    return AnswerGenerator(llm=llm)


def create_query_components(config: VarConfig = None):
    """
    Create a complete set of query processing components with shared LLM and embeddings.

    This is a convenience function that creates all necessary components for
    query expansion with shared instances to avoid redundant initialization.

    Args:
        config: VarConfig instance to use (will create one if not provided)

    Returns:
        Tuple of (llm, embeddings, analyzer, query_generator, answer_generator)
    """
    logger.info("Creating complete query component set")

    # Use config if provided, otherwise create a new one
    if config is None:
        config = VarConfig()

    # Create shared components
    llm = create_llm(config)
    embeddings = create_embeddings(config)
    analyzer = create_query_analyzer()

    # Create generators with shared components
    query_generator = QueryGenerator(llm=llm, embeddings=embeddings)
    answer_generator = AnswerGenerator(llm=llm)

    logger.info("Successfully created all query components")

    return llm, embeddings, analyzer, query_generator, answer_generator
