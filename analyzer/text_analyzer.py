from typing import Dict, List

class TextAnalyzer:
    def __init__(self, embeddings):
        self.embeddings = embeddings

    def extract_elements(self, text: str) -> Dict[str, List[str]]:
        """Extract key elements from text for question generation"""
        # Basic implementation - can be enhanced with NLP processing
        return {
            "text": [text],
            "keywords": self._extract_keywords(text)
        }

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        # Simple implementation - can be enhanced with keyword extraction
        STOP_WORDS = {'what', 'where', 'when', 'how', 'why', 'who', 'the', 'and', 'are'}        
        return [word.strip('?.,!') for word in text.split() 
                if len(word) > 3 and word.lower() not in STOP_WORDS]

