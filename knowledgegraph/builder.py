from typing import List, Dict, Tuple
import networkx as nx

class KnowledgeGraphBuilder:
    def __init__(self):
        self.graph = nx.Graph()
        
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
                    self.graph.add_node(node_id, 
                                      type=element_type,
                                      label=item['label'],
                                      query_id=query_id)
                else:
                    node_id = f"{element_type}:{item}"
                    self.graph.add_node(node_id, 
                                      type=element_type,
                                      query_id=query_id)
                
        # Create edges between elements from same query
        nodes = list(self.graph.nodes())
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                if self.graph.nodes[nodes[i]]['query_id'] == self.graph.nodes[nodes[j]]['query_id']:
                    self.graph.add_edge(nodes[i], nodes[j], 
                                      weight=1,
                                      query_id=self.graph.nodes[nodes[i]]['query_id'])
                    
    def get_related_elements(self, element_type: str, min_weight: int = 1) -> List[Tuple[str, str]]:
        """
        Get pairs of related elements of specified type based on edge weights
        """
        related_pairs = []
        for edge in self.graph.edges(data=True):
            if (edge[0].startswith(f"{element_type}:") and 
                edge[1].startswith(f"{element_type}:") and 
                edge[2]['weight'] >= min_weight):
                related_pairs.append((
                    edge[0].split(':', 1)[1],
                    edge[1].split(':', 1)[1]
                ))
        return related_pairs

class GraphVisualizer:
    def __init__(self, graph: nx.Graph, domain_name: str = None):
        self.graph = graph
        self.domain_name = domain_name
        
    def visualize(self, figsize=(15, 10)):
        """
        Visualize the knowledge graph with different colors for different node types
        """
        import matplotlib.pyplot as plt
        
        # Create color map for different node types
        color_map = {
            'entities': '#ff7f0e',    # Orange
            'noun_phrases': '#1f77b4', # Blue
            'verbs': '#2ca02c',       # Green
            'concepts': '#d62728'      # Red
        }
        
        # Get node colors based on type
        node_colors = []
        node_sizes = []
        for node in self.graph.nodes():
            node_type = node.split(':')[0]
            node_colors.append(color_map.get(node_type, '#808080'))
            # Make named entities larger
            node_sizes.append(2000 if node_type == 'entities' else 1000)
            
        # Set up the plot
        plt.figure(figsize=figsize)
        
        # Create layout
        pos = nx.spring_layout(self.graph, k=1, iterations=50)
        
        # Draw the graph
        nx.draw(self.graph, pos,
                node_color=node_colors,
                node_size=node_sizes,
                with_labels=True,
                font_size=8,
                font_weight='bold',
                edge_color='#CCCCCC',
                width=0.5,
                alpha=0.7)
        
        # Create legend
        legend_elements = [plt.Line2D([0], [0], marker='o', color='w', 
                                    markerfacecolor=color, label=node_type, markersize=10)
                          for node_type, color in color_map.items()]
        plt.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1))
        
        plt.title('Knowledge Graph Visualization')
        plt.tight_layout()
        plt.savefig(f'generated_datasets/{self.domain_name}_.png')
        plt.show()