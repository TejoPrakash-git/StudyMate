from typing import List, Dict, Any
from api_layer.llm_interface import GeminiInterface

class MCQGenerator:
    """Generates multiple-choice questions based on study materials."""
    
    def __init__(self):
        """Initialize the MCQ Generator with Gemini interface."""
        self.llm = GeminiInterface()
    
    def generate_mcqs(self, content: str, num_questions: int = 5, 
                     difficulty: str = "medium") -> List[Dict[str, Any]]:
        """Generate multiple-choice questions based on the provided content.
        
        Args:
            content: The study material content to generate questions from
            num_questions: Number of questions to generate
            difficulty: Difficulty level (easy, medium, hard)
            
        Returns:
            List of MCQ dictionaries with question, options, and correct answer
        """
        prompt = f"""Generate {num_questions} multiple-choice questions with {difficulty} difficulty based on the following content. 
        For each question, provide 4 options (A, B, C, D) with exactly one correct answer.
        Format the output as a list of JSON objects with the following structure for each question:
        {{"question": "Question text", "options": ["A. Option A", "B. Option B", "C. Option C", "D. Option D"], "correct_answer": "A", "explanation": "Explanation why this is correct"}}
        
        Content:
        {content}
        """
        
        response = self.llm.generate_text(prompt, temperature=0.3)
        
        # Process the response to extract the MCQs
        # This is a simplified implementation - in a real app, you'd want more robust parsing
        try:
            import json
            # Find the JSON part in the response
            start_idx = response.find('[{')
            end_idx = response.rfind('}]') + 2
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                mcqs = json.loads(json_str)
                return mcqs
            else:
                # Fallback parsing if the model didn't return proper JSON
                mcqs = []
                questions = response.split("\n\n")
                for q in questions[:num_questions]:
                    if "?" in q and "A." in q and "B." in q:
                        question_parts = q.split("?")
                        question = question_parts[0] + "?"
                        options_text = question_parts[1]
                        options = []
                        for opt in ["A.", "B.", "C.", "D."]:
                            if opt in options_text:
                                opt_start = options_text.find(opt)
                                next_opt = next((o for o in ["A.", "B.", "C.", "D."] if o > opt and o in options_text), None)
                                opt_end = options_text.find(next_opt) if next_opt else len(options_text)
                                options.append(options_text[opt_start:opt_end].strip())
                        
                        # Determine correct answer (simplified)
                        correct = "A"  # Default
                        if "correct" in q.lower():
                            for opt in ["A", "B", "C", "D"]:
                                if f"correct answer is {opt}" in q.lower() or f"correct: {opt}" in q.lower():
                                    correct = opt
                                    break
                        
                        mcqs.append({
                            "question": question.strip(),
                            "options": options,
                            "correct_answer": correct,
                            "explanation": "Explanation not available in parsed format"
                        })
                return mcqs
        except Exception as e:
            print(f"Error parsing MCQs: {e}")
            # Return a simplified structure if parsing fails
            return [{
                "question": "Failed to parse questions properly. Please try again.",
                "options": ["A. Try again", "B. Use different content", "C. Adjust parameters", "D. Contact support"],
                "correct_answer": "A",
                "explanation": "There was an error processing the AI response."
            }]
    
    def generate_quiz_from_pdf(self, pdf_text: str, num_questions: int = 5, 
                             topics: List[str] = None, 
                             difficulty: str = "medium") -> List[Dict[str, Any]]:
        """Generate a quiz based on PDF content with optional topic filtering.
        
        Args:
            pdf_text: The extracted text from a PDF document
            num_questions: Number of questions to generate
            topics: Optional list of topics to focus on
            difficulty: Difficulty level (easy, medium, hard)
            
        Returns:
            List of MCQ dictionaries
        """
        if topics and len(topics) > 0:
            topic_str = ", ".join(topics)
            prompt = f"From the following PDF content, generate {num_questions} multiple-choice questions with {difficulty} difficulty focusing on these topics: {topic_str}.\n\nPDF Content:\n{pdf_text[:10000]}"  # Limit content length
        else:
            prompt = f"From the following PDF content, generate {num_questions} multiple-choice questions with {difficulty} difficulty covering the main concepts.\n\nPDF Content:\n{pdf_text[:10000]}"  # Limit content length
        
        return self.generate_mcqs(prompt, num_questions, difficulty)