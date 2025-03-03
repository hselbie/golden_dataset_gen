# Define seed queries with their IDs
seed_queries = [
    ("What are some popular attractions to visit in Seattle?", "q1"),
    ("What restaurants serve vegan food in Austin?", "q2"),
    ("What would be a good teambuilding outdoor activity in Manhattan?", "q3"),
    ("Where is the nearest local coffee shop to my hotel?", "q4")
]

# Domain-specific queries
domains = {
    "scientific": [
        ("What is the role of mitochondria in cellular respiration?", "sci1"),
        ("How does quantum entanglement work in physics?", "sci2"),
        ("Explain the process of DNA replication.", "sci3"),
        ("What are the laws of thermodynamics?", "sci4")
    ],
    "technology": [
        ("How do microprocessors handle parallel processing?", "tech1"),
        ("What are the principles of cloud computing architecture?", "tech2"),
        ("Explain how blockchain maintains data integrity?", "tech3"),
        ("What is the difference between HTTP and HTTPS?", "tech4")
    ],
    "business": [
        ("What are the key components of a SWOT analysis?", "bus1"),
        ("How does supply chain optimization work?", "bus2"),
        ("Explain the concept of market segmentation?", "bus3"),
        ("What are the principles of agile project management?", "bus4")
    ]
}

