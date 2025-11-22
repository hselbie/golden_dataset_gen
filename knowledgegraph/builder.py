from typing import List, Dict, Tuple
import networkx as nx


class KnowledgeGraphBuilder:
    def __init__(self):
        self.graph = nx.Graph()
        # Define weight multipliers for different relationships
        self.weight_multipliers = {
            ("entities", "entities"): 2.0,  # Strong connection between named entities
            ("entities", "concepts"): 1.5,  # Entity-concept connections are important
            ("noun_phrases", "verbs"): 1.2,  # Action relationships
            ("concepts", "concepts"): 1.3,  # Concept relationships
            ("verbs", "verbs"): 0.8,  # Weaker verb-verb connections
        }
        # Track frequency of co-occurrences
        self.cooccurrence_counts = {}

    def _calculate_edge_weight(
        self, node1: str, node2: str, type1: str, type2: str
    ) -> float:
        """
        Calculate edge weight based on node types and relationship patterns
        """
        # Base weight
        weight = 1.0

        # Get edge type combination (order alphabetically for consistency)
        edge_types = tuple(sorted([type1, type2]))

        # Apply type-based multiplier if exists
        if edge_types in self.weight_multipliers:
            weight *= self.weight_multipliers[edge_types]

        # Consider semantic similarity if they're the same type
        if type1 == type2:
            # Nodes of same type get a small boost
            weight *= 1.1

        # Track co-occurrence
        edge_key = tuple(sorted([node1, node2]))
        self.cooccurrence_counts[edge_key] = (
            self.cooccurrence_counts.get(edge_key, 0) + 1
        )

        # Adjust weight based on co-occurrence frequency
        frequency_multiplier = min(
            1 + (self.cooccurrence_counts[edge_key] - 1) * 0.2, 2.0
        )
        weight *= frequency_multiplier

        return weight

    def add_query_elements(self, query_id: str, elements: Dict[str, List[str]]):
        """
        Add query elements to the knowledge graph
        Creates nodes for elements and edges based on co-occurrence
        """
        # Add nodes for each element type
        for element_type, items in elements.items():
            for item in items:
                if isinstance(item, dict):
                    node_id = f"{element_type}:{item['text']}"
                    self.graph.add_node(
                        node_id,
                        type=element_type,
                        label=item["label"],
                        query_id=query_id,
                    )
                else:
                    node_id = f"{element_type}:{item}"
                    self.graph.add_node(node_id, type=element_type, query_id=query_id)

        # Create edges between elements from same query
        nodes = list(self.graph.nodes())
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                if (
                    self.graph.nodes[nodes[i]]["query_id"]
                    == self.graph.nodes[nodes[j]]["query_id"]
                ):
                    # Get node types for weight calculation
                    type1 = self.graph.nodes[nodes[i]]["type"]
                    type2 = self.graph.nodes[nodes[j]]["type"]

                    # Calculate edge weight
                    weight = self._calculate_edge_weight(
                        nodes[i], nodes[j], type1, type2
                    )

                    # Add edge with calculated weight
                    self.graph.add_edge(
                        nodes[i],
                        nodes[j],
                        weight=weight,
                        query_id=self.graph.nodes[nodes[i]]["query_id"],
                    )

    def get_related_elements(
        self, element_type: str, min_weight: int = 1
    ) -> List[Tuple[str, str]]:
        """
        Get pairs of related elements of specified type based on edge weights
        """
        related_pairs = []
        for edge in self.graph.edges(data=True):
            if (
                edge[0].startswith(f"{element_type}:")
                and edge[1].startswith(f"{element_type}:")
                and edge[2]["weight"] >= min_weight
            ):
                related_pairs.append(
                    (edge[0].split(":", 1)[1], edge[1].split(":", 1)[1])
                )
        return related_pairs


class GraphVisualizer:
    def __init__(self, graph: nx.Graph, domain_name: str = None):
        self.graph = graph
        self.domain_name = domain_name

    def visualize(self, figsize=(15, 10)):
        """
        Visualize the knowledge graph with different colors for different node types
        and edge thickness based on weights
        """
        import matplotlib.pyplot as plt

        # Create color map for different node types
        color_map = {
            "entities": "#ff7f0e",  # Orange
            "noun_phrases": "#1f77b4",  # Blue
            "verbs": "#2ca02c",  # Green
            "concepts": "#d62728",  # Red
        }

        # Get node colors based on type
        node_colors = []
        node_sizes = []
        for node in self.graph.nodes():
            node_type = node.split(":")[0]
            node_colors.append(color_map.get(node_type, "#808080"))
            # Make named entities larger
            node_sizes.append(2000 if node_type == "entities" else 1000)

        # Get edge weights and normalize them for visualization
        edge_weights = [self.graph[u][v]["weight"] for u, v in self.graph.edges()]

        # Handle edge weight normalization
        if edge_weights:  # If there are edges
            max_weight = max(edge_weights)
            min_weight = min(edge_weights)

            # If all weights are the same, use a default width
            if max_weight == min_weight:
                normalized_weights = [2.5] * len(
                    edge_weights
                )  # Use constant middle value
            else:
                try:
                    normalized_weights = [
                        (w - min_weight) / (max_weight - min_weight) * 4 + 1
                        for w in edge_weights
                    ]
                except ZeroDivisionError:
                    normalized_weights = [2.5] * len(
                        edge_weights
                    )  # Fallback to constant width
        else:
            # No edges case
            normalized_weights = []
            max_weight = 0
            min_weight = 0

        # Set up the plot
        plt.figure(figsize=figsize)

        # Create layout
        pos = nx.spring_layout(self.graph, k=1, iterations=50)

        # Draw the graph
        nx.draw(
            self.graph,
            pos,
            node_color=node_colors,
            node_size=node_sizes,
            with_labels=True,
            font_size=8,
            font_weight="bold",
            edge_color="#CCCCCC",
            width=normalized_weights,  # Edge thickness based on weight
            alpha=0.7,
        )

        # Create legend for nodes
        legend_elements = [
            plt.Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                markerfacecolor=color,
                label=node_type,
                markersize=10,
            )
            for node_type, color in color_map.items()
        ]

        # Add legend elements for edge weights only if there are edges
        if edge_weights:
            if max_weight != min_weight:
                legend_elements.extend(
                    [
                        plt.Line2D(
                            [0],
                            [0],
                            color="#CCCCCC",
                            linewidth=1,
                            label="Weak Connection",
                        ),
                        plt.Line2D(
                            [0],
                            [0],
                            color="#CCCCCC",
                            linewidth=3,
                            label="Medium Connection",
                        ),
                        plt.Line2D(
                            [0],
                            [0],
                            color="#CCCCCC",
                            linewidth=5,
                            label="Strong Connection",
                        ),
                    ]
                )
            else:
                legend_elements.append(
                    plt.Line2D(
                        [0],
                        [0],
                        color="#CCCCCC",
                        linewidth=2.5,
                        label="Uniform Connection",
                    )
                )

        plt.legend(handles=legend_elements, loc="upper left", bbox_to_anchor=(1, 1))

        # Add title with weight range information
        if edge_weights:
            if max_weight != min_weight:
                plt.title(
                    f"Knowledge Graph Visualization\nEdge Weights: {min_weight:.2f} to {max_weight:.2f}"
                )
            else:
                plt.title(
                    f"Knowledge Graph Visualization\nUniform Edge Weight: {max_weight:.2f}"
                )
        else:
            plt.title("Knowledge Graph Visualization\nNo edges present")

        # Add weight labels on edges if there are any
        if edge_weights:
            edge_labels = nx.get_edge_attributes(self.graph, "weight")
            nx.draw_networkx_edge_labels(self.graph, pos, edge_labels, font_size=6)

        # Save and show the plot
        if self.domain_name:
            plt.savefig(
                f"generated_datasets/{self.domain_name}_.png", bbox_inches="tight"
            )
        plt.show()
