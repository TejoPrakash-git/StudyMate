import json
import os
from datetime import datetime
import streamlit as st
from api_layer.llm_interface import GeminiInterface

class FeedbackSystem:
    """Class to handle peer review and feedback functionality."""
    
    def __init__(self, data_dir="./data/feedback"):
        """Initialize the FeedbackSystem.
        
        Args:
            data_dir (str): Directory to store feedback data
        """
        self.data_dir = data_dir
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # File path for feedback data
        self.feedback_file = os.path.join(self.data_dir, "feedback_data.json")
        
        # Initialize or load data
        self.feedback_data = self._load_data(self.feedback_file, [])
        
        # Initialize LLM interface if needed
        try:
            self.llm = GeminiInterface()
        except Exception as e:
            st.error(f"Error initializing Gemini AI: {str(e)}")
            self.llm = None
    
    def _load_data(self, file_path, default_data):
        """Load data from a JSON file or return default if file doesn't exist.
        
        Args:
            file_path (str): Path to the JSON file
            default_data: Default data to return if file doesn't exist
            
        Returns:
            Data loaded from the file or default data
        """
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
            return default_data
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return default_data
    
    def _save_data(self, file_path, data):
        """Save data to a JSON file.
        
        Args:
            file_path (str): Path to the JSON file
            data: Data to save
        """
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            st.error(f"Error saving data: {str(e)}")
    
    def submit_content_for_review(self, content, content_type, subject, author_name, notes=None):
        """Submit content for peer review.
        
        Args:
            content (str): The content to be reviewed
            content_type (str): Type of content (e.g., 'essay', 'summary', 'notes')
            subject (str): Subject of the content
            author_name (str): Name of the author
            notes (str, optional): Additional notes for reviewers
            
        Returns:
            str: ID of the submitted content
        """
        # Generate a unique ID for the submission
        submission_id = f"{content_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        submission_data = {
            "id": submission_id,
            "timestamp": datetime.now().isoformat(),
            "content": content,
            "content_type": content_type,
            "subject": subject,
            "author_name": author_name,
            "notes": notes,
            "reviews": [],
            "ai_feedback": None,
            "status": "pending"
        }
        
        # Add AI feedback if LLM is available
        if self.llm is not None:
            try:
                ai_feedback = self.generate_ai_feedback(content, content_type, subject)
                submission_data["ai_feedback"] = ai_feedback
            except Exception as e:
                st.error(f"Error generating AI feedback: {str(e)}")
        
        # Add to feedback data and save
        self.feedback_data.append(submission_data)
        self._save_data(self.feedback_file, self.feedback_data)
        
        return submission_id
    
    def add_peer_review(self, submission_id, reviewer_name, rating, comments, strengths=None, areas_for_improvement=None):
        """Add a peer review to a submitted content.
        
        Args:
            submission_id (str): ID of the submission
            reviewer_name (str): Name of the reviewer
            rating (int): Rating (1-5)
            comments (str): Review comments
            strengths (list, optional): List of strengths
            areas_for_improvement (list, optional): List of areas for improvement
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Find the submission
        for submission in self.feedback_data:
            if submission["id"] == submission_id:
                # Create review data
                review_data = {
                    "timestamp": datetime.now().isoformat(),
                    "reviewer_name": reviewer_name,
                    "rating": rating,
                    "comments": comments,
                    "strengths": strengths or [],
                    "areas_for_improvement": areas_for_improvement or []
                }
                
                # Add to reviews and save
                submission["reviews"].append(review_data)
                submission["status"] = "reviewed"
                self._save_data(self.feedback_file, self.feedback_data)
                
                return True
        
        return False
    
    def get_submission(self, submission_id):
        """Get a submission by ID.
        
        Args:
            submission_id (str): ID of the submission
            
        Returns:
            dict: Submission data or None if not found
        """
        for submission in self.feedback_data:
            if submission["id"] == submission_id:
                return submission
        
        return None
    
    def get_submissions_by_author(self, author_name):
        """Get all submissions by an author.
        
        Args:
            author_name (str): Name of the author
            
        Returns:
            list: List of submissions
        """
        return [s for s in self.feedback_data if s["author_name"] == author_name]
    
    def get_pending_submissions(self):
        """Get all pending submissions.
        
        Returns:
            list: List of pending submissions
        """
        return [s for s in self.feedback_data if s["status"] == "pending"]
    
    def generate_ai_feedback(self, content, content_type, subject):
        """Generate AI feedback for content.
        
        Args:
            content (str): The content to provide feedback on
            content_type (str): Type of content
            subject (str): Subject of the content
            
        Returns:
            dict: AI feedback with strengths, areas for improvement, and suggestions
        """
        if self.llm is None:
            return None
        
        try:
            # Create prompt for AI feedback
            prompt = f"""Please provide constructive feedback on the following {content_type} about {subject}. 
            
            CONTENT:
            {content}
            
            Please structure your feedback with the following sections:
            1. Overall assessment
            2. Strengths (list 3-5 specific strengths)
            3. Areas for improvement (list 3-5 specific areas)
            4. Specific suggestions for improvement
            
            Be specific, constructive, and educational in your feedback.
            """
            
            # Generate feedback
            feedback_text = self.llm.generate_text(prompt, temperature=0.3)
            
            # Parse the feedback (in a real implementation, this would be more sophisticated)
            sections = feedback_text.split("\n\n")
            
            # Create structured feedback
            feedback = {
                "overall": sections[0] if len(sections) > 0 else "",
                "strengths": [],
                "areas_for_improvement": [],
                "suggestions": sections[-1] if len(sections) > 3 else ""
            }
            
            # Extract strengths and areas for improvement
            for section in sections:
                if "strength" in section.lower():
                    # Extract bullet points
                    points = [p.strip().lstrip('-*•').strip() for p in section.split("\n")[1:] if p.strip()]
                    feedback["strengths"] = points
                elif "improvement" in section.lower() or "improve" in section.lower():
                    # Extract bullet points
                    points = [p.strip().lstrip('-*•').strip() for p in section.split("\n")[1:] if p.strip()]
                    feedback["areas_for_improvement"] = points
            
            return feedback
        
        except Exception as e:
            st.error(f"Error generating AI feedback: {str(e)}")
            return None
    
    def summarize_feedback(self, submission_id):
        """Summarize all feedback for a submission.
        
        Args:
            submission_id (str): ID of the submission
            
        Returns:
            dict: Summary of feedback
        """
        submission = self.get_submission(submission_id)
        
        if submission is None or not submission["reviews"]:
            return None
        
        # Calculate average rating
        ratings = [r["rating"] for r in submission["reviews"]]
        avg_rating = sum(ratings) / len(ratings)
        
        # Collect all strengths and areas for improvement
        all_strengths = []
        all_areas = []
        
        for review in submission["reviews"]:
            all_strengths.extend(review.get("strengths", []))
            all_areas.extend(review.get("areas_for_improvement", []))
        
        # Count occurrences of each point
        strength_counts = {}
        for s in all_strengths:
            if s in strength_counts:
                strength_counts[s] += 1
            else:
                strength_counts[s] = 1
        
        area_counts = {}
        for a in all_areas:
            if a in area_counts:
                area_counts[a] += 1
            else:
                area_counts[a] = 1
        
        # Sort by frequency
        top_strengths = sorted(strength_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        top_areas = sorted(area_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "avg_rating": round(avg_rating, 1),
            "num_reviews": len(submission["reviews"]),
            "top_strengths": [s[0] for s in top_strengths],
            "top_areas_for_improvement": [a[0] for a in top_areas],
            "ai_feedback": submission.get("ai_feedback")
        }