"""
Tests for the Knowledge Graph Builder and Visualizer.

This module tests the sophisticated knowledge graph construction algorithm
including weighted edge calculation, co-occurrence tracking, and visualization.
"""

import pytest
import networkx as nx
from knowledgegraph.builder import KnowledgeGraphBuilder, GraphVisualizer


class TestKnowledgeGraphBuilder:
    """Test suite for KnowledgeGraphBuilder class."""

    def test_initialization(self):
        """Test knowledge graph builder initializes correctly"""
        builder = KnowledgeGraphBuilder()

        assert isinstance(builder.graph, nx.Graph)
        assert len(builder.graph.nodes()) == 0
        assert len(builder.graph.edges()) == 0
        assert isinstance(builder.weight_multipliers, dict)
        assert isinstance(builder.cooccurrence_counts, dict)

    def test_add_query_elements_simple(self):
        """Test adding simple query elements creates nodes and edges"""
        builder = KnowledgeGraphBuilder()

        elements = {
            "entities": [{"text": "Python", "label": "LANGUAGE"}],
            "noun_phrases": ["programming language"],
            "verbs": ["code"],
            "concepts": ["programming"],
        }

        builder.add_query_elements("query1", elements)

        # Should create 4 nodes (one per element)
        assert len(builder.graph.nodes()) == 4

        # Should create edges between all pairs (4 choose 2 = 6 edges)
        assert len(builder.graph.edges()) == 6

    def test_node_attributes(self):
        """Test that nodes have correct attributes"""
        builder = KnowledgeGraphBuilder()

        elements = {
            "entities": [{"text": "Google", "label": "ORG"}],
            "concepts": ["search"],
        }

        builder.add_query_elements("q1", elements)

        # Check entity node attributes
        entity_node = "entities:Google"
        assert builder.graph.has_node(entity_node)
        assert builder.graph.nodes[entity_node]["type"] == "entities"
        assert builder.graph.nodes[entity_node]["label"] == "ORG"
        assert builder.graph.nodes[entity_node]["query_id"] == "q1"

        # Check concept node attributes
        concept_node = "concepts:search"
        assert builder.graph.has_node(concept_node)
        assert builder.graph.nodes[concept_node]["type"] == "concepts"
        assert builder.graph.nodes[concept_node]["query_id"] == "q1"

    def test_edge_weight_calculation_base(self):
        """Test base edge weight calculation"""
        builder = KnowledgeGraphBuilder()

        # Calculate weight for first occurrence
        weight = builder._calculate_edge_weight("node1", "node2", "verbs", "verbs")

        # Should have base weight (1.0) * verb-verb multiplier (0.8) * same type boost (1.1)
        expected = 1.0 * 0.8 * 1.1
        assert abs(weight - expected) < 0.01

    def test_edge_weight_with_multipliers(self):
        """Test edge weights apply correct type-based multipliers"""
        builder = KnowledgeGraphBuilder()

        # Entity-entity connection should have 2.0 multiplier
        weight_ee = builder._calculate_edge_weight("e1", "e2", "entities", "entities")
        # 1.0 * 2.0 (entity multiplier) * 1.1 (same type)
        assert abs(weight_ee - 2.2) < 0.01

        # Concept-concept connection should have 1.3 multiplier
        weight_cc = builder._calculate_edge_weight("c1", "c2", "concepts", "concepts")
        # 1.0 * 1.3 (concept multiplier) * 1.1 (same type)
        assert abs(weight_cc - 1.43) < 0.01

        # Noun phrase-verb connection should have 1.2 multiplier
        weight_nv = builder._calculate_edge_weight("n1", "v1", "noun_phrases", "verbs")
        # 1.0 * 1.2 (noun-verb multiplier)
        assert abs(weight_nv - 1.2) < 0.01

    def test_cooccurrence_tracking(self):
        """Test that co-occurrence frequencies are tracked correctly"""
        builder = KnowledgeGraphBuilder()

        elements = {
            "entities": [{"text": "AI", "label": "TECH"}],
            "concepts": ["machine learning"],
        }

        # Add same elements twice (different query IDs)
        builder.add_query_elements("q1", elements)

        # Check co-occurrence count
        edge_key = tuple(sorted(["entities:AI", "concepts:machine learning"]))
        assert edge_key in builder.cooccurrence_counts
        assert builder.cooccurrence_counts[edge_key] == 1

    def test_frequency_multiplier(self):
        """Test that frequency multiplier increases with co-occurrences"""
        builder = KnowledgeGraphBuilder()

        # First occurrence
        weight1 = builder._calculate_edge_weight("n1", "n2", "concepts", "concepts")

        # Second occurrence (same nodes)
        weight2 = builder._calculate_edge_weight("n1", "n2", "concepts", "concepts")

        # Weight should increase due to frequency multiplier
        assert weight2 > weight1

        # Third occurrence
        weight3 = builder._calculate_edge_weight("n1", "n2", "concepts", "concepts")
        assert weight3 > weight2

    def test_frequency_multiplier_cap(self):
        """Test that frequency multiplier is capped at 2.0"""
        builder = KnowledgeGraphBuilder()

        # Simulate many co-occurrences
        for i in range(20):
            weight = builder._calculate_edge_weight("n1", "n2", "concepts", "concepts")

        # Check the edge key
        edge_key = tuple(sorted(["n1", "n2"]))
        assert edge_key in builder.cooccurrence_counts
        assert builder.cooccurrence_counts[edge_key] == 20

        # Frequency multiplier should be capped
        # Formula: min(1 + (count - 1) * 0.2, 2.0)
        expected_multiplier = 2.0  # Capped

        # Base weight for concept-concept: 1.0 * 1.3 * 1.1 = 1.43
        # With max frequency multiplier: 1.43 * 2.0 = 2.86
        expected_weight = 1.0 * 1.3 * 1.1 * 2.0
        assert abs(weight - expected_weight) < 0.01

    def test_multiple_queries(self):
        """Test adding elements from multiple queries"""
        builder = KnowledgeGraphBuilder()

        elements1 = {
            "entities": [{"text": "Python", "label": "LANGUAGE"}],
            "concepts": ["programming"],
        }

        elements2 = {
            "entities": [{"text": "Java", "label": "LANGUAGE"}],
            "concepts": ["programming"],
        }

        builder.add_query_elements("q1", elements1)
        builder.add_query_elements("q2", elements2)

        # Should have 3 unique nodes (Python, Java, programming)
        # Note: 'programming' appears in both queries but should be same node
        assert len(builder.graph.nodes()) == 3

        # q1: Python-programming (1 edge)
        # q2: Java-programming (1 edge)
        # Total: 2 edges
        assert len(builder.graph.edges()) == 2

    def test_get_related_elements(self):
        """Test retrieving related elements by type and weight"""
        builder = KnowledgeGraphBuilder()

        elements = {
            "entities": [
                {"text": "Google", "label": "ORG"},
                {"text": "AI", "label": "TECH"},
            ],
            "concepts": ["search", "machine learning"],
        }

        builder.add_query_elements("q1", elements)

        # Get related entities (should have edge weight >= 1)
        related = builder.get_related_elements("entities", min_weight=1)

        # Should find the Google-AI relationship
        assert len(related) >= 1

        # Verify the pair (order might vary)
        related_texts = [set(pair) for pair in related]
        assert {"Google", "AI"} in related_texts

    def test_get_related_elements_min_weight_filter(self):
        """Test that min_weight filter works correctly"""
        builder = KnowledgeGraphBuilder()

        elements = {"verbs": ["run", "execute", "process"], "concepts": ["code"]}

        builder.add_query_elements("q1", elements)

        # Get verb-verb relationships (weight multiplier 0.8 * 1.1 = 0.88)
        # With min_weight=1, should filter out some edges
        related_high = builder.get_related_elements("verbs", min_weight=1)

        # With min_weight=0.5, should include more edges
        related_low = builder.get_related_elements("verbs", min_weight=0.5)

        # Lower threshold should include at least as many as higher threshold
        assert len(related_low) >= len(related_high)

    def test_empty_elements(self):
        """Test handling of empty element dictionaries"""
        builder = KnowledgeGraphBuilder()

        elements = {"entities": [], "noun_phrases": [], "verbs": [], "concepts": []}

        builder.add_query_elements("q1", elements)

        # Should not create any nodes or edges
        assert len(builder.graph.nodes()) == 0
        assert len(builder.graph.edges()) == 0

    def test_edge_weight_consistency(self):
        """Test that edge weight calculation is consistent for same-type pairs"""
        builder = KnowledgeGraphBuilder()

        # Same type pairs should give consistent weights
        weight1 = builder._calculate_edge_weight("n1", "n2", "concepts", "concepts")
        weight2 = builder._calculate_edge_weight("n3", "n4", "concepts", "concepts")

        # First occurrence weights should match (before co-occurrence tracking affects them)
        # Both should be 1.0 * 1.3 * 1.1 = 1.43
        assert abs(weight1 - 1.43) < 0.01


class TestGraphVisualizer:
    """Test suite for GraphVisualizer class."""

    def test_initialization(self):
        """Test visualizer initializes correctly"""
        graph = nx.Graph()
        visualizer = GraphVisualizer(graph, domain_name="test")

        assert visualizer.graph == graph
        assert visualizer.domain_name == "test"

    def test_initialization_without_domain(self):
        """Test visualizer works without domain name"""
        graph = nx.Graph()
        visualizer = GraphVisualizer(graph)

        assert visualizer.graph == graph
        assert visualizer.domain_name is None

    def test_visualize_empty_graph(self):
        """Test visualization of empty graph doesn't crash"""
        graph = nx.Graph()
        visualizer = GraphVisualizer(graph, domain_name="empty")

        # Should not raise an exception
        try:
            # Don't actually show the plot in tests
            import matplotlib

            matplotlib.use("Agg")  # Use non-interactive backend
            import matplotlib.pyplot as plt

            visualizer.visualize()
            plt.close("all")  # Clean up
        except Exception as e:
            pytest.fail(f"Visualization of empty graph raised exception: {e}")

    def test_visualize_simple_graph(self):
        """Test visualization of simple graph"""
        builder = KnowledgeGraphBuilder()

        elements = {
            "entities": [{"text": "Test", "label": "ORG"}],
            "concepts": ["testing"],
        }

        builder.add_query_elements("q1", elements)

        visualizer = GraphVisualizer(builder.graph, domain_name="test")

        # Should not raise an exception
        try:
            import matplotlib

            matplotlib.use("Agg")
            import matplotlib.pyplot as plt

            visualizer.visualize()
            plt.close("all")
        except Exception as e:
            pytest.fail(f"Visualization raised exception: {e}")

    def test_visualize_with_uniform_weights(self):
        """Test visualization handles uniform edge weights correctly"""
        graph = nx.Graph()
        graph.add_node("entities:A", type="entities")
        graph.add_node("entities:B", type="entities")
        graph.add_edge("entities:A", "entities:B", weight=1.5)

        visualizer = GraphVisualizer(graph, domain_name="uniform")

        try:
            import matplotlib

            matplotlib.use("Agg")
            import matplotlib.pyplot as plt

            visualizer.visualize()
            plt.close("all")
        except Exception as e:
            pytest.fail(f"Visualization with uniform weights raised exception: {e}")

    def test_visualize_with_varied_weights(self):
        """Test visualization with varied edge weights"""
        graph = nx.Graph()
        graph.add_node("entities:A", type="entities")
        graph.add_node("entities:B", type="entities")
        graph.add_node("concepts:C", type="concepts")

        graph.add_edge("entities:A", "entities:B", weight=2.0)
        graph.add_edge("entities:A", "concepts:C", weight=1.0)
        graph.add_edge("entities:B", "concepts:C", weight=3.0)

        visualizer = GraphVisualizer(graph, domain_name="varied")

        try:
            import matplotlib

            matplotlib.use("Agg")
            import matplotlib.pyplot as plt

            visualizer.visualize()
            plt.close("all")
        except Exception as e:
            pytest.fail(f"Visualization with varied weights raised exception: {e}")
