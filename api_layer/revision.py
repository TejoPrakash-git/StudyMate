from typing import List, Dict, Any
from api_layer.llm_interface import GeminiInterface

class RevisionHelper:
    """Handles revision content generation and management."""
    
    def __init__(self):
        """Initialize the Revision Helper with Gemini interface."""
        self.llm = GeminiInterface()
    
    def generate_flashcards(self, content: str, num_cards: int = 10) -> List[Dict[str, str]]:
        """Generate flashcards based on the provided content.
        
        Args:
            content: The study material content to generate flashcards from
            num_cards: Number of flashcards to generate
            
        Returns:
            List of flashcard dictionaries with front and back content
        """
        prompt = f"""Generate {num_cards} flashcards based on the following content. 
        Each flashcard should have a question on the front and the answer on the back.
        Focus on key concepts, definitions, and important facts.
        
        Format the output as a list of JSON objects with the following structure for each flashcard:
        {{"front": "Question or concept", "back": "Answer or explanation"}}
        
        Content:
        {content[:8000]}  # Limit content length
        """
        
        response = self.llm.generate_text(prompt, temperature=0.3)
        
        # Process the response to extract the flashcards
        try:
            import json
            # Find the JSON part in the response
            start_idx = response.find('[{')
            end_idx = response.rfind('}]') + 2
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                flashcards = json.loads(json_str)
                return flashcards
            else:
                # Fallback parsing if the model didn't return proper JSON
                flashcards = []
                cards = response.split("\n\n")
                for card in cards[:num_cards]:
                    if "front" in card.lower() and "back" in card.lower():
                        front = ""
                        back = ""
                        lines = card.split("\n")
                        for line in lines:
                            if "front:" in line.lower():
                                front = line.split(":", 1)[1].strip()
                            elif "back:" in line.lower():
                                back = line.split(":", 1)[1].strip()
                        
                        if front and back:
                            flashcards.append({"front": front, "back": back})
                
                return flashcards
        except Exception as e:
            print(f"Error parsing flashcards: {e}")
            # Return a simplified structure if parsing fails
            return [{
                "front": "Failed to parse flashcards properly. Please try again.",
                "back": "There was an error processing the AI response."
            }]
    
    def generate_study_guide(self, content: str, topics: List[str] = None) -> Dict[str, Any]:
        """Generate a comprehensive study guide based on the provided content.
        
        Args:
            content: The study material content to generate a guide from
            topics: Optional list of topics to focus on
            
        Returns:
            Dictionary with study guide sections
        """
        if topics and len(topics) > 0:
            topic_str = ", ".join(topics)
            prompt = f"""Create a comprehensive study guide based on the following content, focusing on these topics: {topic_str}.
            
            Include the following sections:
            1. Key Concepts - List and briefly explain the most important concepts
            2. Definitions - Provide clear definitions for important terms
            3. Summary - Summarize the main points in a concise way
            4. Practice Questions - Include 3-5 practice questions with answers
            
            Content:
            {content[:8000]}  # Limit content length
            """
        else:
            prompt = f"""Create a comprehensive study guide based on the following content.
            
            Include the following sections:
            1. Key Concepts - List and briefly explain the most important concepts
            2. Definitions - Provide clear definitions for important terms
            3. Summary - Summarize the main points in a concise way
            4. Practice Questions - Include 3-5 practice questions with answers
            
            Content:
            {content[:8000]}  # Limit content length
            """
        
        response = self.llm.generate_text(prompt, temperature=0.3, max_output_tokens=2048)
        
        # Process the response to extract the study guide sections
        try:
            sections = {}
            
            # Extract Key Concepts
            if "Key Concepts" in response:
                key_concepts_text = response.split("Key Concepts")[1]
                if any(section in key_concepts_text for section in ["Definitions", "Summary", "Practice Questions"]):
                    for section in ["Definitions", "Summary", "Practice Questions"]:
                        if section in key_concepts_text:
                            key_concepts_text = key_concepts_text.split(section)[0]
                            break
                sections["key_concepts"] = key_concepts_text.strip()
            
            # Extract Definitions
            if "Definitions" in response:
                definitions_text = response.split("Definitions")[1]
                if any(section in definitions_text for section in ["Summary", "Practice Questions"]):
                    for section in ["Summary", "Practice Questions"]:
                        if section in definitions_text:
                            definitions_text = definitions_text.split(section)[0]
                            break
                sections["definitions"] = definitions_text.strip()
            
            # Extract Summary
            if "Summary" in response:
                summary_text = response.split("Summary")[1]
                if "Practice Questions" in summary_text:
                    summary_text = summary_text.split("Practice Questions")[0]
                sections["summary"] = summary_text.strip()
            
            # Extract Practice Questions
            if "Practice Questions" in response:
                practice_questions = response.split("Practice Questions")[1].strip()
                sections["practice_questions"] = practice_questions
            
            return sections
        
        except Exception as e:
            print(f"Error parsing study guide: {e}")
            # Return the raw response if parsing fails
            return {"raw_content": response}
    
    def generate_concept_connections(self, content: str, main_concept: str) -> Dict[str, List[Dict[str, Any]]]:
        """Generate connections between concepts for concept mapping.
        
        Args:
            content: The study material content to analyze
            main_concept: The central concept to map relationships from
            
        Returns:
            Dictionary with nodes and edges for concept mapping
        """
        prompt = f"""Analyze the following content and identify concepts related to '{main_concept}'.
        For each related concept, explain how it connects to '{main_concept}' and to other concepts.
        
        Format the output as a JSON object with the following structure:
        {{
          "nodes": [
            {{"id": "1", "label": "{main_concept}", "type": "main"}},
            {{"id": "2", "label": "Related Concept 1", "type": "related"}},
            ...
          ],
          "edges": [
            {{"from": "1", "to": "2", "label": "relationship description"}},
            ...
          ]
        }}
        
        Content:
        {content[:8000]}  # Limit content length
        """
        
        response = self.llm.generate_text(prompt, temperature=0.3)
        
        # Process the response to extract the concept map
        try:
            import json
            # Find the JSON part in the response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                concept_map = json.loads(json_str)
                return concept_map
            else:
                # Fallback if JSON parsing fails
                return {
                    "nodes": [
                        {"id": "1", "label": main_concept, "type": "main"}
                    ],
                    "edges": []
                }
        except Exception as e:
            print(f"Error parsing concept connections: {e}")
            # Return a basic structure if parsing fails
            return {
                "nodes": [
                    {"id": "1", "label": main_concept, "type": "main"}
                ],
                "edges": []
            }