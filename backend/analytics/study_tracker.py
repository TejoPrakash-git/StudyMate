import pandas as pd
import json
import os
from datetime import datetime, timedelta
import streamlit as st

class StudyTracker:
    """Class to track and analyze study activities and performance."""
    
    def __init__(self, data_dir="./data/analytics"):
        """Initialize the StudyTracker.
        
        Args:
            data_dir (str): Directory to store analytics data
        """
        self.data_dir = data_dir
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # File paths for different analytics data
        self.study_time_file = os.path.join(self.data_dir, "study_time.json")
        self.quiz_results_file = os.path.join(self.data_dir, "quiz_results.json")
        self.topic_data_file = os.path.join(self.data_dir, "topic_data.json")
        
        # Initialize or load data
        self.study_time_data = self._load_data(self.study_time_file, [])
        self.quiz_results_data = self._load_data(self.quiz_results_file, [])
        self.topic_data = self._load_data(self.topic_data_file, {})
    
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
    
    def record_study_session(self, subject, duration_minutes, document_name=None, notes=None):
        """Record a study session.
        
        Args:
            subject (str): Subject studied
            duration_minutes (int): Duration of the session in minutes
            document_name (str, optional): Name of the document studied
            notes (str, optional): Additional notes about the session
        """
        session_data = {
            "timestamp": datetime.now().isoformat(),
            "subject": subject,
            "duration_minutes": duration_minutes,
            "document_name": document_name,
            "notes": notes
        }
        
        self.study_time_data.append(session_data)
        self._save_data(self.study_time_file, self.study_time_data)
        
        # Update topic data
        if subject in self.topic_data:
            self.topic_data[subject]["total_time"] = self.topic_data[subject].get("total_time", 0) + duration_minutes
            self.topic_data[subject]["sessions"] = self.topic_data[subject].get("sessions", 0) + 1
        else:
            self.topic_data[subject] = {
                "total_time": duration_minutes,
                "sessions": 1,
                "quizzes": 0,
                "avg_score": 0
            }
        
        self._save_data(self.topic_data_file, self.topic_data)
    
    def record_quiz_result(self, subject, score_percentage, num_questions, difficulty, time_taken_seconds=None):
        """Record a quiz result.
        
        Args:
            subject (str): Subject of the quiz
            score_percentage (float): Score as a percentage (0-100)
            num_questions (int): Number of questions in the quiz
            difficulty (str): Difficulty level of the quiz
            time_taken_seconds (int, optional): Time taken to complete the quiz in seconds
        """
        quiz_data = {
            "timestamp": datetime.now().isoformat(),
            "subject": subject,
            "score_percentage": score_percentage,
            "num_questions": num_questions,
            "difficulty": difficulty,
            "time_taken_seconds": time_taken_seconds
        }
        
        self.quiz_results_data.append(quiz_data)
        self._save_data(self.quiz_results_file, self.quiz_results_data)
        
        # Update topic data
        if subject in self.topic_data:
            current_quizzes = self.topic_data[subject].get("quizzes", 0)
            current_avg = self.topic_data[subject].get("avg_score", 0)
            
            # Calculate new average score
            new_avg = (current_avg * current_quizzes + score_percentage) / (current_quizzes + 1)
            
            self.topic_data[subject]["quizzes"] = current_quizzes + 1
            self.topic_data[subject]["avg_score"] = new_avg
        else:
            self.topic_data[subject] = {
                "total_time": 0,
                "sessions": 0,
                "quizzes": 1,
                "avg_score": score_percentage
            }
        
        self._save_data(self.topic_data_file, self.topic_data)
    
    def get_study_time_df(self, days=30):
        """Get study time data as a pandas DataFrame.
        
        Args:
            days (int): Number of days to include in the data
            
        Returns:
            pandas.DataFrame: Study time data
        """
        try:
            # Convert to DataFrame
            df = pd.DataFrame(self.study_time_data)
            
            if df.empty:
                return pd.DataFrame(columns=["date", "subject", "duration_minutes"])
            
            # Convert timestamp to datetime
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            
            # Filter for the specified number of days
            cutoff_date = datetime.now() - timedelta(days=days)
            df = df[df["timestamp"] >= cutoff_date]
            
            # Extract date from timestamp
            df["date"] = df["timestamp"].dt.date
            
            return df
        except Exception as e:
            st.error(f"Error processing study time data: {str(e)}")
            return pd.DataFrame(columns=["date", "subject", "duration_minutes"])
    
    def get_quiz_results_df(self, days=30):
        """Get quiz results data as a pandas DataFrame.
        
        Args:
            days (int): Number of days to include in the data
            
        Returns:
            pandas.DataFrame: Quiz results data
        """
        try:
            # Convert to DataFrame
            df = pd.DataFrame(self.quiz_results_data)
            
            if df.empty:
                return pd.DataFrame(columns=["date", "subject", "score_percentage", "difficulty"])
            
            # Convert timestamp to datetime
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            
            # Filter for the specified number of days
            cutoff_date = datetime.now() - timedelta(days=days)
            df = df[df["timestamp"] >= cutoff_date]
            
            # Extract date from timestamp
            df["date"] = df["timestamp"].dt.date
            
            return df
        except Exception as e:
            st.error(f"Error processing quiz results data: {str(e)}")
            return pd.DataFrame(columns=["date", "subject", "score_percentage", "difficulty"])
    
    def get_topic_data_df(self):
        """Get topic data as a pandas DataFrame.
        
        Returns:
            pandas.DataFrame: Topic data
        """
        try:
            # Convert dictionary to DataFrame
            data = []
            for subject, stats in self.topic_data.items():
                row = {"subject": subject}
                row.update(stats)
                data.append(row)
            
            df = pd.DataFrame(data)
            
            if df.empty:
                return pd.DataFrame(columns=["subject", "total_time", "sessions", "quizzes", "avg_score"])
            
            return df
        except Exception as e:
            st.error(f"Error processing topic data: {str(e)}")
            return pd.DataFrame(columns=["subject", "total_time", "sessions", "quizzes", "avg_score"])
    
    def get_study_time_summary(self, days=30):
        """Get a summary of study time.
        
        Args:
            days (int): Number of days to include in the summary
            
        Returns:
            dict: Summary statistics
        """
        df = self.get_study_time_df(days)
        
        if df.empty:
            return {
                "total_hours": 0,
                "days_studied": 0,
                "avg_daily_minutes": 0,
                "top_subject": None
            }
        
        total_minutes = df["duration_minutes"].sum()
        unique_days = df["date"].nunique()
        
        # Get top subject
        subject_time = df.groupby("subject")["duration_minutes"].sum()
        top_subject = subject_time.idxmax() if not subject_time.empty else None
        
        return {
            "total_hours": round(total_minutes / 60, 1),
            "days_studied": unique_days,
            "avg_daily_minutes": round(total_minutes / unique_days, 1) if unique_days > 0 else 0,
            "top_subject": top_subject
        }
    
    def get_quiz_performance_summary(self, days=30):
        """Get a summary of quiz performance.
        
        Args:
            days (int): Number of days to include in the summary
            
        Returns:
            dict: Summary statistics
        """
        df = self.get_quiz_results_df(days)
        
        if df.empty:
            return {
                "total_quizzes": 0,
                "avg_score": 0,
                "best_subject": None,
                "needs_improvement": None
            }
        
        total_quizzes = len(df)
        avg_score = df["score_percentage"].mean()
        
        # Get best and worst subjects
        subject_scores = df.groupby("subject")["score_percentage"].mean()
        best_subject = subject_scores.idxmax() if not subject_scores.empty else None
        needs_improvement = subject_scores.idxmin() if not subject_scores.empty and len(subject_scores) > 1 else None
        
        return {
            "total_quizzes": total_quizzes,
            "avg_score": round(avg_score, 1),
            "best_subject": best_subject,
            "needs_improvement": needs_improvement
        }
    
    def generate_recommendations(self):
        """Generate study recommendations based on analytics data.
        
        Returns:
            list: List of recommendation strings
        """
        recommendations = []
        
        # Get recent data
        study_df = self.get_study_time_df(30)
        quiz_df = self.get_quiz_results_df(30)
        topic_df = self.get_topic_data_df()
        
        # Check if we have enough data
        if study_df.empty and quiz_df.empty:
            return ["Not enough data to generate recommendations. Continue using StudyMateZ to get personalized insights."]
        
        # Study time recommendations
        if not study_df.empty:
            # Check for consistency
            unique_days = study_df["date"].nunique()
            total_days = (datetime.now().date() - study_df["date"].min()).days + 1
            
            if unique_days / total_days < 0.5:
                recommendations.append("Try to study more consistently. Regular study sessions are more effective than cramming.")
            
            # Check for subject balance
            subject_time = study_df.groupby("subject")["duration_minutes"].sum()
            if len(subject_time) > 1 and subject_time.max() / subject_time.sum() > 0.7:
                recommendations.append(f"Your study time is heavily focused on {subject_time.idxmax()}. Consider balancing your time across different subjects.")
        
        # Quiz performance recommendations
        if not quiz_df.empty:
            # Check for low scores
            subject_scores = quiz_df.groupby("subject")["score_percentage"].mean()
            low_score_subjects = subject_scores[subject_scores < 70].index.tolist()
            
            if low_score_subjects:
                subjects_str = ", ".join(low_score_subjects)
                recommendations.append(f"Consider spending more time on {subjects_str} to improve your quiz scores.")
            
            # Check for difficulty progression
            if "difficulty" in quiz_df.columns:
                easy_count = quiz_df[quiz_df["difficulty"] == "Easy"].shape[0]
                medium_count = quiz_df[quiz_df["difficulty"] == "Medium"].shape[0]
                hard_count = quiz_df[quiz_df["difficulty"] == "Hard"].shape[0]
                
                if easy_count > 0 and medium_count == 0 and hard_count == 0:
                    recommendations.append("Try increasing the difficulty of your quizzes to challenge yourself.")
        
        # Topic-based recommendations
        if not topic_df.empty:
            # Find neglected subjects
            neglected = topic_df[topic_df["sessions"] <= 1].sort_values("total_time")
            
            if not neglected.empty:
                neglected_subjects = neglected["subject"].iloc[0] if len(neglected) == 1 else ", ".join(neglected["subject"].iloc[:2])
                recommendations.append(f"You haven't spent much time on {neglected_subjects}. Consider revisiting these topics.")
        
        # Add general recommendations if we don't have many specific ones
        if len(recommendations) < 2:
            general_recommendations = [
                "Try using the Concept Map feature to visualize connections between topics.",
                "Regular quizzing helps with long-term retention. Try taking quizzes on topics you studied a week ago.",
                "Summarizing content in your own words is an effective study technique.",
                "Consider using the Tutor Mode for subjects you find challenging."
            ]
            
            import random
            recommendations.extend(random.sample(general_recommendations, min(2, len(general_recommendations))))
        
        return recommendations[:3]  # Limit to top 3 recommendations