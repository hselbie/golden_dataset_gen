"""
Unit tests for QueryGenerator class.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from querygenerator.generator import QueryGenerator


class TestQueryGenerator:
    """Test suite for QueryGenerator."""

    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM for testing."""
        llm = Mock()
        response = Mock()
        response.content = """Question: What is Seattle known for?
Question: Where can I find good coffee in Seattle?
Question: What are the best restaurants in Seattle?"""
        llm.invoke.return_value = response
        return llm

    @pytest.fixture
    def mock_embeddings(self):
        """Create a mock embeddings model for testing."""
        return Mock()

    @pytest.fixture
    def generator(self, mock_llm, mock_embeddings):
        """Create a QueryGenerator instance for testing."""
        with patch("querygenerator.generator.VarConfig.__init__", return_value=None):
            gen = QueryGenerator(mock_llm, mock_embeddings)
            # Mock the parent class attributes
            gen.project = "test-project"
            gen.location = "us-central1"
            gen.llm = mock_llm
            gen.embeddings = mock_embeddings
            return gen

    def test_generator_initialization(self, generator):
        """Test that QueryGenerator initializes correctly."""
        assert generator is not None
        assert generator.llm is not None
        assert generator.embeddings is not None

    def test_generate_questions_basic(self, generator, mock_llm):
        """Test basic question generation."""
        elements = {
            "entities": [{"text": "Seattle", "label": "GPE"}],
            "noun_phrases": ["popular attractions"],
            "verbs": ["visit"],
            "concepts": ["attractions"],
        }

        questions = generator.generate_questions(elements, num_questions=3)

        assert len(questions) == 3
        assert all(isinstance(q, str) for q in questions)
        mock_llm.invoke.assert_called_once()

    def test_generate_questions_count(self, generator, mock_llm):
        """Test that correct number of questions is requested."""
        elements = {
            "entities": [],
            "noun_phrases": ["restaurants"],
            "verbs": ["serve"],
            "concepts": [],
        }

        generator.generate_questions(elements, num_questions=5)

        # Check that the prompt requests 5 questions
        call_args = mock_llm.invoke.call_args[0][0]
        assert "5" in call_args

    def test_construct_question_prompt(self, generator):
        """Test prompt construction."""
        elements = {
            "entities": [{"text": "Austin", "label": "GPE"}],
            "noun_phrases": ["vegan food"],
            "verbs": ["serve"],
            "concepts": ["restaurants"],
        }

        prompt = generator._construct_question_prompt(elements, num_questions=3)

        assert "Generate 3" in prompt
        assert "Austin" in prompt
        assert "vegan food" in prompt
        assert isinstance(prompt, str)

    def test_parse_questions(self, generator):
        """Test parsing of LLM response."""
        response = """Question: What is machine learning?
Question: How does AI work?
Question: What are neural networks?
Some other text that should be ignored."""

        questions = generator._parse_questions(response)

        assert len(questions) == 3
        assert questions[0] == "What is machine learning?"
        assert questions[1] == "How does AI work?"
        assert questions[2] == "What are neural networks?"

    def test_parse_questions_no_questions(self, generator):
        """Test parsing response with no questions."""
        response = "This is just some text without questions."

        questions = generator._parse_questions(response)

        assert len(questions) == 0

    def test_parse_questions_with_extra_whitespace(self, generator):
        """Test parsing handles extra whitespace."""
        response = """
        Question:   What is quantum physics?

        Question: How does it relate to chemistry?
        """

        questions = generator._parse_questions(response)

        assert len(questions) == 2
        assert questions[0] == "What is quantum physics?"
        assert questions[1] == "How does it relate to chemistry?"

    def test_generate_questions_with_empty_elements(self, generator, mock_llm):
        """Test question generation with empty elements."""
        elements = {"entities": [], "noun_phrases": [], "verbs": [], "concepts": []}

        questions = generator.generate_questions(elements, num_questions=2)

        # Should still call LLM even with empty elements
        assert mock_llm.invoke.called

    def test_generate_questions_with_complex_elements(self, generator, mock_llm):
        """Test question generation with complex elements."""
        elements = {
            "entities": [
                {"text": "Seattle", "label": "GPE"},
                {"text": "Manhattan", "label": "GPE"},
            ],
            "noun_phrases": [
                "outdoor activities",
                "team building",
                "popular attractions",
            ],
            "verbs": ["visit", "explore", "enjoy"],
            "concepts": ["activities", "locations", "teamwork"],
        }

        questions = generator.generate_questions(elements, num_questions=5)

        # Verify all element types are included in prompt
        call_args = mock_llm.invoke.call_args[0][0]
        assert "Seattle" in call_args
        assert "outdoor activities" in call_args
        assert len(questions) > 0
