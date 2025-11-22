"""
Unit tests for AnswerGenerator class.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from querygenerator.generator import AnswerGenerator


class TestAnswerGenerator:
    """Test suite for AnswerGenerator."""

    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM for testing."""
        llm = Mock()
        response = Mock()
        response.content = "This is a test answer from the LLM."
        llm.invoke.return_value = response
        return llm

    @pytest.fixture
    def generator(self, mock_llm):
        """Create an AnswerGenerator instance for testing."""
        with (
            patch("querygenerator.generator.VarConfig.__init__", return_value=None),
            patch("querygenerator.generator.VertexAIClient"),
        ):
            gen = AnswerGenerator(mock_llm)
            # Mock the parent class attributes
            gen.project = "test-project"
            gen.location = "us-central1"
            gen.llm = mock_llm
            return gen

    def test_generator_initialization(self, generator):
        """Test that AnswerGenerator initializes correctly."""
        assert generator is not None
        assert generator.llm is not None

    def test_generate_answers_llm_source(self, generator, mock_llm):
        """Test answer generation using LLM source."""
        questions = ["What is machine learning?", "How does AI work?"]

        qa_pairs = generator.generate_answers(questions, source="llm")

        assert len(qa_pairs) == 2
        assert all(isinstance(pair, tuple) for pair in qa_pairs)
        assert all(len(pair) == 2 for pair in qa_pairs)
        assert mock_llm.invoke.call_count == 2

    def test_generate_answers_single_question(self, generator, mock_llm):
        """Test answer generation for a single question."""
        questions = ["What is the capital of France?"]

        qa_pairs = generator.generate_answers(questions, source="llm")

        assert len(qa_pairs) == 1
        assert qa_pairs[0][0] == "What is the capital of France?"
        assert isinstance(qa_pairs[0][1], str)

    def test_generate_answers_empty_list(self, generator, mock_llm):
        """Test answer generation with empty question list."""
        questions = []

        qa_pairs = generator.generate_answers(questions, source="llm")

        assert len(qa_pairs) == 0
        assert not mock_llm.invoke.called

    def test_get_llm_answer(self, generator, mock_llm):
        """Test direct LLM answer generation."""
        question = "What is quantum physics?"

        answer = generator._get_llm_answer(question)

        assert isinstance(answer, str)
        assert len(answer) > 0
        mock_llm.invoke.assert_called_once()

        # Check that question is in the prompt
        call_args = mock_llm.invoke.call_args[0][0]
        assert question in call_args

    def test_get_answer_llm_source(self, generator):
        """Test _get_answer with llm source."""
        question = "Test question?"

        answer = generator._get_answer(question, "llm")

        assert isinstance(answer, str)

    def test_get_answer_source_routing(self, generator):
        """Test that _get_answer routes to correct method based on source."""
        question = "Test question?"

        # Mock the individual answer methods
        with (
            patch.object(
                generator, "_get_llm_answer", return_value="llm answer"
            ) as mock_llm_ans,
            patch.object(
                generator, "_get_datastore_answer", return_value="ds answer"
            ) as mock_ds_ans,
            patch.object(
                generator, "_get_google_search_answer", return_value="google answer"
            ) as mock_google_ans,
        ):
            # Test LLM routing
            answer = generator._get_answer(question, "llm")
            assert answer == "llm answer"
            mock_llm_ans.assert_called_once_with(question)

            # Test datastore routing
            answer = generator._get_answer(question, "datastore")
            assert answer == "ds answer"
            mock_ds_ans.assert_called_once_with(question)

            # Test google routing
            answer = generator._get_answer(question, "google")
            assert answer == "google answer"
            mock_google_ans.assert_called_once_with(question)

    def test_generate_answers_error_handling(self, generator, mock_llm):
        """Test that errors are handled gracefully during answer generation."""
        questions = ["Valid question?", "Question that will fail?"]

        # Make the second call raise an exception
        mock_llm.invoke.side_effect = [Mock(content="Answer 1"), Exception("API Error")]

        qa_pairs = generator.generate_answers(questions, source="llm")

        # Should still return results, with error for failed question
        assert len(qa_pairs) == 2
        assert qa_pairs[0][1] == "Answer 1"
        assert "Error" in qa_pairs[1][1]

    def test_qa_pair_structure(self, generator, mock_llm):
        """Test that QA pairs have correct structure."""
        questions = ["What is Python?"]
        mock_llm.invoke.return_value.content = "Python is a programming language."

        qa_pairs = generator.generate_answers(questions, source="llm")

        assert len(qa_pairs) == 1
        question, answer = qa_pairs[0]
        assert question == "What is Python?"
        assert answer == "Python is a programming language."

    def test_multiple_questions_distinct_answers(self, generator, mock_llm):
        """Test that multiple questions get distinct answers."""
        questions = ["What is 1 + 1?", "What is 2 + 2?", "What is 3 + 3?"]

        # Set up different responses for each call
        mock_llm.invoke.side_effect = [
            Mock(content="Answer to 1+1"),
            Mock(content="Answer to 2+2"),
            Mock(content="Answer to 3+3"),
        ]

        qa_pairs = generator.generate_answers(questions, source="llm")

        assert len(qa_pairs) == 3
        assert qa_pairs[0][1] == "Answer to 1+1"
        assert qa_pairs[1][1] == "Answer to 2+2"
        assert qa_pairs[2][1] == "Answer to 3+3"
