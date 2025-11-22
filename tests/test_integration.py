"""
Integration tests for the query expansion system.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from querygenerator.generator import QueryAnalyzer, QueryGenerator, AnswerGenerator
import pandas as pd


class TestIntegration:
    """Integration tests for the full query processing pipeline."""

    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM for testing."""
        llm = Mock()
        # Mock responses for different calls
        responses = [
            Mock(
                content="""Question: What attractions are in Seattle?
Question: Where can I visit in Seattle?
Question: What is Seattle famous for?"""
            ),
            Mock(
                content="Seattle is known for the Space Needle and Pike Place Market."
            ),
            Mock(
                content="You can visit Pike Place Market, the Space Needle, and many parks."
            ),
            Mock(
                content="Seattle is famous for its coffee culture, tech industry, and natural beauty."
            ),
        ]
        llm.invoke.side_effect = responses
        return llm

    @pytest.fixture
    def mock_embeddings(self):
        """Create a mock embeddings model."""
        return Mock()

    @pytest.fixture
    def analyzer(self):
        """Create a real QueryAnalyzer instance."""
        return QueryAnalyzer()

    @pytest.fixture
    def query_generator(self, mock_llm, mock_embeddings):
        """Create a QueryGenerator with mocked dependencies."""
        with patch("querygenerator.generator.VarConfig.__init__", return_value=None):
            gen = QueryGenerator(mock_llm, mock_embeddings)
            gen.project = "test-project"
            gen.location = "us-central1"
            gen.llm = mock_llm
            gen.embeddings = mock_embeddings
            return gen

    @pytest.fixture
    def answer_generator(self, mock_llm):
        """Create an AnswerGenerator with mocked dependencies."""
        with (
            patch("querygenerator.generator.VarConfig.__init__", return_value=None),
            patch("querygenerator.generator.VertexAIClient"),
        ):
            gen = AnswerGenerator(mock_llm)
            gen.project = "test-project"
            gen.location = "us-central1"
            gen.llm = mock_llm
            return gen

    def test_full_pipeline_single_query(
        self, analyzer, query_generator, answer_generator
    ):
        """Test the complete pipeline from query to Q&A pairs."""
        # Step 1: Extract elements from query
        original_query = "What are popular attractions in Seattle?"
        elements = analyzer.extract_elements(original_query)

        # Verify elements were extracted
        assert len(elements) > 0
        assert "entities" in elements

        # Step 2: Generate questions from elements
        questions = query_generator.generate_questions(elements, num_questions=3)

        # Verify questions were generated
        assert len(questions) == 3
        assert all(isinstance(q, str) for q in questions)

        # Step 3: Generate answers for the questions
        qa_pairs = answer_generator.generate_answers(questions, source="llm")

        # Verify Q&A pairs were generated
        assert len(qa_pairs) == 3
        for question, answer in qa_pairs:
            assert isinstance(question, str)
            assert isinstance(answer, str)
            assert len(answer) > 0

    def test_pipeline_with_multiple_queries(self, analyzer, query_generator):
        """Test processing multiple queries through the pipeline."""
        queries = [
            "What restaurants serve vegan food in Austin?",
            "What are outdoor activities in Manhattan?",
        ]

        all_questions = []
        for query in queries:
            # Extract elements
            elements = analyzer.extract_elements(query)

            # Generate questions
            questions = query_generator.generate_questions(elements, num_questions=2)
            all_questions.extend(questions)

        # Should have questions from both queries (at least some)
        assert len(all_questions) >= 1  # At least some questions generated

    def test_element_extraction_to_question_generation(self, analyzer, query_generator):
        """Test that elements are properly used in question generation."""
        query = "How does quantum entanglement work in physics?"
        elements = analyzer.extract_elements(query)

        # Generate questions using the elements
        questions = query_generator.generate_questions(elements, num_questions=3)

        # The LLM should have been called with a prompt containing the elements
        assert len(questions) > 0

    def test_error_recovery_in_pipeline(self, analyzer, query_generator, mock_llm):
        """Test that the pipeline handles errors gracefully."""
        query = "What is machine learning?"
        elements = analyzer.extract_elements(query)

        # Make the LLM fail
        mock_llm.invoke.side_effect = Exception("API Error")

        # Should raise exception during question generation
        with pytest.raises(Exception):
            query_generator.generate_questions(elements, num_questions=3)

    def test_answer_generation_with_real_questions(self, answer_generator):
        """Test answer generation with realistic questions."""
        questions = [
            "What is the capital of France?",
            "How does photosynthesis work?",
            "What are the benefits of exercise?",
        ]

        qa_pairs = answer_generator.generate_answers(questions, source="llm")

        assert len(qa_pairs) == len(questions)
        for (q_orig, q_result), answer in zip(enumerate(questions), qa_pairs):
            assert answer[0] == q_result
            assert len(answer[1]) > 0

    def test_data_flow_integrity(self, analyzer, query_generator, answer_generator):
        """Test that data maintains integrity through the pipeline."""
        original_query = "What is the role of mitochondria?"

        # Step 1: Extract elements
        elements = analyzer.extract_elements(original_query)
        original_element_count = sum(
            len(v) if isinstance(v, list) else 1 for v in elements.values()
        )

        # Verify elements extracted
        assert original_element_count > 0

        # Step 2: Generate questions
        questions = query_generator.generate_questions(elements, num_questions=2)

        # Step 3: Generate answers
        qa_pairs = answer_generator.generate_answers(questions, source="llm")

        # Verify data integrity
        assert len(qa_pairs) == len(questions)
        for i, (question, answer) in enumerate(qa_pairs):
            assert question == questions[i]  # Questions match
            assert answer  # Answer exists

    def test_empty_query_handling(self, analyzer, query_generator):
        """Test how the pipeline handles empty queries."""
        query = ""
        elements = analyzer.extract_elements(query)

        # Elements should be empty but valid
        assert all(len(v) == 0 for v in elements.values())

        # Question generation should still work (though may produce generic questions)
        questions = query_generator.generate_questions(elements, num_questions=1)
        assert isinstance(questions, list)

    @pytest.mark.parametrize(
        "query,expected_entity_types",
        [
            ("What attractions are in Seattle?", ["GPE"]),
            ("How does quantum physics work?", []),
            ("What restaurants are in Austin, Texas?", ["GPE"]),
        ],
    )
    def test_entity_recognition_across_queries(
        self, analyzer, query, expected_entity_types
    ):
        """Test entity recognition for various query types."""
        elements = analyzer.extract_elements(query)

        if expected_entity_types:
            # Should have extracted entities
            assert len(elements["entities"]) > 0
            entity_labels = [e["label"] for e in elements["entities"]]
            # At least one expected type should be present
            assert any(label in entity_labels for label in expected_entity_types)
        # Note: Empty expected_entity_types means we're just checking it doesn't crash
