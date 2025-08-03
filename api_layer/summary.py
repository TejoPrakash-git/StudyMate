from typing import Dict, Any, Optional
from api_layer.llm_interface import GeminiInterface

class DocumentSummarizer:
    """Creates summaries of documents using Gemini AI."""
    
    def __init__(self):
        """Initialize the Document Summarizer with Gemini interface."""
        self.llm = GeminiInterface()
    
    def summarize_text(self, text: str, length: str = "medium", 
                      focus: Optional[str] = None) -> Dict[str, Any]:
        """Generate a summary of the provided text.
        
        Args:
            text: The text content to summarize
            length: Summary length (short, medium, long)
            focus: Optional focus area for the summary
            
        Returns:
            Dictionary with summary and key points
        """
        # Determine target word count based on length parameter
        word_counts = {
            "short": 150,
            "medium": 300,
            "long": 500
        }
        target_words = word_counts.get(length.lower(), 300)
        
        # Create the prompt based on parameters
        if focus:
            prompt = f"""Summarize the following text in approximately {target_words} words, focusing on aspects related to {focus}.
            Also extract 3-5 key points from the text.
            
            Text to summarize:
            {text[:10000]}  # Limit text length to avoid token limits
            
            Format the output as follows:
            Summary: [Your summary here]
            
            Key Points:
            - [Key point 1]
            - [Key point 2]
            - [Key point 3]
            - [Key point 4 (if applicable)]
            - [Key point 5 (if applicable)]
            """
        else:
            prompt = f"""Summarize the following text in approximately {target_words} words.
            Also extract 3-5 key points from the text.
            
            Text to summarize:
            {text[:10000]}  # Limit text length to avoid token limits
            
            Format the output as follows:
            Summary: [Your summary here]
            
            Key Points:
            - [Key point 1]
            - [Key point 2]
            - [Key point 3]
            - [Key point 4 (if applicable)]
            - [Key point 5 (if applicable)]
            """
        
        response = self.llm.generate_text(prompt, temperature=0.3)
        
        # Parse the response
        try:
            summary_part = ""
            key_points = []
            
            if "Summary:" in response and "Key Points:" in response:
                summary_part = response.split("Summary:")[1].split("Key Points:")[0].strip()
                key_points_text = response.split("Key Points:")[1].strip()
                key_points = [point.strip().lstrip('-').strip() for point in key_points_text.split('\n') if point.strip()]
            else:
                # Fallback if the format isn't as expected
                lines = response.split('\n')
                summary_lines = []
                for i, line in enumerate(lines):
                    if i < len(lines) // 2:  # First half is summary
                        summary_lines.append(line)
                    elif line.strip().startswith('-'):  # Lines with dashes are key points
                        key_points.append(line.strip().lstrip('-').strip())
                
                summary_part = '\n'.join(summary_lines).strip()
                if not key_points:  # If no key points were found
                    # Generate some key points from the summary
                    key_points_prompt = f"Extract 3-5 key points from this summary:\n{summary_part}"
                    key_points_response = self.llm.generate_text(key_points_prompt, temperature=0.3)
                    key_points = [point.strip().lstrip('-').strip() for point in key_points_response.split('\n') if point.strip() and point.strip().startswith('-')]
            
            return {
                "summary": summary_part,
                "key_points": key_points[:5]  # Limit to 5 key points
            }
        
        except Exception as e:
            print(f"Error parsing summary: {e}")
            # Return a simplified response if parsing fails
            return {
                "summary": response[:500],  # Just return the first part of the response
                "key_points": ["Error parsing key points"]
            }
    
    def summarize_pdf(self, pdf_text: str, length: str = "medium", 
                     focus: Optional[str] = None) -> Dict[str, Any]:
        """Generate a summary of PDF content.
        
        Args:
            pdf_text: The extracted text from a PDF document
            length: Summary length (short, medium, long)
            focus: Optional focus area for the summary
            
        Returns:
            Dictionary with summary and key points
        """
        return self.summarize_text(pdf_text, length, focus)
    
    def generate_chapter_summaries(self, chapters: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
        """Generate summaries for multiple chapters or sections.
        
        Args:
            chapters: Dictionary mapping chapter titles to their content
            
        Returns:
            Dictionary mapping chapter titles to their summary dictionaries
        """
        summaries = {}
        for title, content in chapters.items():
            summaries[title] = self.summarize_text(content, "short")
        
        return summaries