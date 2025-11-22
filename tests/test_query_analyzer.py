"""
Unit tests for QueryAnalyzer class.
"""

import pytest
from querygenerator.generator import QueryAnalyzer


class TestQueryAnalyzer:
    """Test suite for QueryAnalyzer."""

    @pytest.fixture
    def analyzer(self):
        """Create a QueryAnalyzer instance for testing."""
        return QueryAnalyzer()

    def test_analyzer_initialization(self, analyzer):
        """Test that QueryAnalyzer initializes correctly."""
        assert analyzer is not None
        assert analyzer.nlp is not None

    def test_extract_elements_basic_query(self, analyzer):
        """Test element extraction from a basic query."""
        query = "What are popular attractions in Seattle?"
        elements = analyzer.extract_elements(query)

        assert "entities" in elements
        assert "noun_phrases" in elements
        assert "verbs" in elements
        assert "concepts" in elements

    def test_extract_entities(self, analyzer):
        """Test that named entities are correctly extracted."""
        query = "What restaurants serve vegan food in Austin?"
        elements = analyzer.extract_elements(query)

        # Check that Austin is recognized as a location entity
        entity_texts = [e["text"] for e in elements["entities"]]
        assert "Austin" in entity_texts

    def test_extract_noun_phrases(self, analyzer):
        """Test that noun phrases are extracted."""
        query = "What are some popular attractions to visit in Seattle?"
        elements = analyzer.extract_elements(query)

        assert len(elements["noun_phrases"]) > 0
        assert isinstance(elements["noun_phrases"][0], str)

    def test_extract_verbs(self, analyzer):
        """Test that verbs are extracted and lemmatized."""
        query = "What restaurants are serving vegan food?"
        elements = analyzer.extract_elements(query)

        assert "serve" in elements["verbs"] or "be" in elements["verbs"]

    def test_extract_concepts(self, analyzer):
        """Test that key concepts are extracted via dependency parsing."""
        query = "What is the role of mitochondria in cellular respiration?"
        elements = analyzer.extract_elements(query)

        assert len(elements["concepts"]) > 0

    def test_empty_query(self, analyzer):
        """Test handling of empty query."""
        query = ""
        elements = analyzer.extract_elements(query)

        assert elements["entities"] == []
        assert elements["noun_phrases"] == []
        assert elements["verbs"] == []
        assert elements["concepts"] == []

    def test_complex_query(self, analyzer):
        """Test element extraction from a complex query."""
        query = "How does quantum entanglement work in physics and why is it important?"
        elements = analyzer.extract_elements(query)

        # Should extract multiple elements
        total_elements = (
            len(elements["entities"])
            + len(elements["noun_phrases"])
            + len(elements["verbs"])
            + len(elements["concepts"])
        )
        assert total_elements > 0

    def test_entity_labels(self, analyzer):
        """Test that entities include proper labels."""
        query = "What are the laws of thermodynamics in New York?"
        elements = analyzer.extract_elements(query)

        if elements["entities"]:
            # Check that entities have both text and label
            assert "text" in elements["entities"][0]
            assert "label" in elements["entities"][0]

    def test_multiple_entities(self, analyzer):
        """Test extraction of multiple entities."""
        query = "Compare the weather in Seattle, Austin, and Manhattan."
        elements = analyzer.extract_elements(query)

        entity_texts = [e["text"] for e in elements["entities"]]
        # Should detect multiple location entities
        assert len(entity_texts) >= 2

    def test_technical_query(self, analyzer):
        """Test element extraction from a technical query."""
        query = "How do microprocessors handle parallel processing?"
        elements = analyzer.extract_elements(query)

        # Should extract technical noun phrases
        noun_phrases_lower = [np.lower() for np in elements["noun_phrases"]]
        assert any("microprocessor" in np for np in noun_phrases_lower) or any(
            "parallel processing" in np for np in noun_phrases_lower
        )

    def test_question_words_filtered_as_concepts(self, analyzer):
        """Test that question words are properly handled."""
        query = "What is machine learning?"
        elements = analyzer.extract_elements(query)

        # Concepts should not include just 'what'
        assert "what" not in [c.lower() for c in elements["concepts"]]
