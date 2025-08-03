import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import altair as alt
from datetime import datetime, timedelta

def render_analytics():
    """Render the analytics dashboard UI component."""
    st.header("Study Analytics")
    st.write("Track your study progress and performance.")
    
    # Initialize session state variables if they don't exist
    if "study_sessions" not in st.session_state:
        # Create some sample data for demonstration
        st.session_state.study_sessions = generate_sample_study_data()
    
    if "quiz_history" not in st.session_state:
        # Create some sample quiz data for demonstration
        st.session_state.quiz_history = generate_sample_quiz_data()
    
    # Dashboard tabs
    tab1, tab2, tab3 = st.tabs(["Study Time", "Quiz Performance", "Topic Analysis"])
    
    with tab1:
        render_study_time_analytics()
    
    with tab2:
        render_quiz_performance_analytics()
    
    with tab3:
        render_topic_analysis()

def render_study_time_analytics():
    """Render study time analytics visualizations."""
    st.subheader("Study Time Analytics")
    
    # Get study session data
    study_data = pd.DataFrame(st.session_state.study_sessions)
    
    # Time period filter
    time_period = st.selectbox(
        "Time Period",
        ["Last 7 Days", "Last 30 Days", "All Time"],
        key="time_period_study"
    )
    
    # Filter data based on selected time period
    today = datetime.now().date()
    if time_period == "Last 7 Days":
        start_date = today - timedelta(days=7)
        filtered_data = study_data[study_data['date'] >= start_date.strftime('%Y-%m-%d')]
    elif time_period == "Last 30 Days":
        start_date = today - timedelta(days=30)
        filtered_data = study_data[study_data['date'] >= start_date.strftime('%Y-%m-%d')]
    else:  # All Time
        filtered_data = study_data
    
    # Study time by date chart
    st.subheader("Daily Study Time")
    
    # Group by date and sum duration
    daily_study = filtered_data.groupby('date')['duration_minutes'].sum().reset_index()
    daily_study['date'] = pd.to_datetime(daily_study['date'])
    
    # Create Altair chart
    chart = alt.Chart(daily_study).mark_bar().encode(
        x=alt.X('date:T', title='Date'),
        y=alt.Y('duration_minutes:Q', title='Minutes'),
        tooltip=['date:T', 'duration_minutes:Q']
    ).properties(
        width=600,
        height=300
    )
    
    st.altair_chart(chart, use_container_width=True)
    
    # Study time by subject
    st.subheader("Study Time by Subject")
    
    # Group by subject and sum duration
    subject_study = filtered_data.groupby('subject')['duration_minutes'].sum().reset_index()
    
    # Create pie chart
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(subject_study['duration_minutes'], labels=subject_study['subject'], autopct='%1.1f%%')
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    
    st.pyplot(fig)
    
    # Study statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_time = filtered_data['duration_minutes'].sum()
        st.metric("Total Study Time", f"{total_time} min")
    
    with col2:
        avg_daily = daily_study['duration_minutes'].mean()
        st.metric("Avg. Daily Study Time", f"{avg_daily:.1f} min")
    
    with col3:
        most_studied = subject_study.loc[subject_study['duration_minutes'].idxmax(), 'subject']
        st.metric("Most Studied Subject", most_studied)

def render_quiz_performance_analytics():
    """Render quiz performance analytics visualizations."""
    st.subheader("Quiz Performance Analytics")
    
    # Get quiz history data
    quiz_data = pd.DataFrame(st.session_state.quiz_history)
    
    # Time period filter
    time_period = st.selectbox(
        "Time Period",
        ["Last 7 Days", "Last 30 Days", "All Time"],
        key="time_period_quiz"
    )
    
    # Filter data based on selected time period
    today = datetime.now().date()
    if time_period == "Last 7 Days":
        start_date = today - timedelta(days=7)
        filtered_data = quiz_data[quiz_data['date'] >= start_date.strftime('%Y-%m-%d')]
    elif time_period == "Last 30 Days":
        start_date = today - timedelta(days=30)
        filtered_data = quiz_data[quiz_data['date'] >= start_date.strftime('%Y-%m-%d')]
    else:  # All Time
        filtered_data = quiz_data
    
    # Quiz performance over time chart
    st.subheader("Quiz Performance Over Time")
    
    # Convert date to datetime
    filtered_data['date'] = pd.to_datetime(filtered_data['date'])
    
    # Create Altair chart
    chart = alt.Chart(filtered_data).mark_line(point=True).encode(
        x=alt.X('date:T', title='Date'),
        y=alt.Y('score_percentage:Q', title='Score (%)', scale=alt.Scale(domain=[0, 100])),
        color=alt.Color('subject:N', title='Subject'),
        tooltip=['date:T', 'subject:N', 'score_percentage:Q', 'difficulty:N']
    ).properties(
        width=600,
        height=300
    )
    
    st.altair_chart(chart, use_container_width=True)
    
    # Performance by subject
    st.subheader("Average Performance by Subject")
    
    # Group by subject and calculate average score
    subject_performance = filtered_data.groupby('subject')['score_percentage'].mean().reset_index()
    
    # Create bar chart
    chart = alt.Chart(subject_performance).mark_bar().encode(
        x=alt.X('subject:N', title='Subject'),
        y=alt.Y('score_percentage:Q', title='Average Score (%)', scale=alt.Scale(domain=[0, 100])),
        color=alt.Color('subject:N', legend=None),
        tooltip=['subject:N', 'score_percentage:Q']
    ).properties(
        width=600,
        height=300
    )
    
    st.altair_chart(chart, use_container_width=True)
    
    # Performance by difficulty
    st.subheader("Performance by Difficulty Level")
    
    # Group by difficulty and calculate average score
    difficulty_performance = filtered_data.groupby('difficulty')['score_percentage'].mean().reset_index()
    
    # Create bar chart
    chart = alt.Chart(difficulty_performance).mark_bar().encode(
        x=alt.X('difficulty:N', title='Difficulty', sort=['easy', 'medium', 'hard']),
        y=alt.Y('score_percentage:Q', title='Average Score (%)', scale=alt.Scale(domain=[0, 100])),
        color=alt.Color('difficulty:N', legend=None),
        tooltip=['difficulty:N', 'score_percentage:Q']
    ).properties(
        width=600,
        height=300
    )
    
    st.altair_chart(chart, use_container_width=True)

def render_topic_analysis():
    """Render topic analysis visualizations."""
    st.subheader("Topic Analysis")
    
    # Get quiz history data for topic analysis
    quiz_data = pd.DataFrame(st.session_state.quiz_history)
    
    # Create sample topic performance data
    topic_data = generate_sample_topic_data()
    topic_df = pd.DataFrame(topic_data)
    
    # Topic strength chart
    st.subheader("Topic Strength Analysis")
    
    # Create radar chart for topic strengths
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    
    # Number of topics
    N = len(topic_df)
    
    # Angles for each topic (in radians)
    angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
    
    # Close the polygon
    strengths = topic_df['strength'].tolist()
    strengths.append(strengths[0])
    angles.append(angles[0])
    
    # Plot data
    ax.plot(angles, strengths, 'o-', linewidth=2)
    ax.fill(angles, strengths, alpha=0.25)
    
    # Set labels
    ax.set_thetagrids(np.degrees(angles[:-1]), topic_df['topic'].tolist())
    
    # Set y-axis limits
    ax.set_ylim(0, 100)
    
    st.pyplot(fig)
    
    # Topic improvement recommendations
    st.subheader("Recommended Focus Areas")
    
    # Sort topics by strength (ascending)
    weak_topics = topic_df.sort_values('strength').head(3)
    
    for _, topic in weak_topics.iterrows():
        st.markdown(f"**{topic['topic']}** - Current strength: {topic['strength']}%")
        st.write(f"Recommendation: {topic['recommendation']}")
        st.progress(topic['strength'] / 100)
        st.write("---")

def generate_sample_study_data():
    """Generate sample study session data for demonstration."""
    # Current date
    today = datetime.now().date()
    
    # Sample subjects
    subjects = ["Mathematics", "Physics", "Computer Science", "Biology", "Chemistry"]
    
    # Generate data for the last 30 days
    study_sessions = []
    
    for i in range(30):
        date = today - timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        
        # Random number of sessions per day (0-3)
        num_sessions = np.random.randint(0, 4)
        
        for _ in range(num_sessions):
            subject = np.random.choice(subjects)
            duration = np.random.randint(15, 121)  # 15-120 minutes
            
            study_sessions.append({
                "date": date_str,
                "subject": subject,
                "duration_minutes": duration,
                "notes": f"Study session on {subject}"
            })
    
    return study_sessions

def generate_sample_quiz_data():
    """Generate sample quiz history data for demonstration."""
    # Current date
    today = datetime.now().date()
    
    # Sample subjects and difficulties
    subjects = ["Mathematics", "Physics", "Computer Science", "Biology", "Chemistry"]
    difficulties = ["easy", "medium", "hard"]
    
    # Generate data for the last 30 days
    quiz_history = []
    
    for i in range(30):
        date = today - timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        
        # Random number of quizzes per day (0-2)
        num_quizzes = np.random.randint(0, 3)
        
        for _ in range(num_quizzes):
            subject = np.random.choice(subjects)
            difficulty = np.random.choice(difficulties)
            
            # Score depends on difficulty
            if difficulty == "easy":
                score = np.random.randint(70, 101)  # 70-100%
            elif difficulty == "medium":
                score = np.random.randint(60, 96)  # 60-95%
            else:  # hard
                score = np.random.randint(50, 91)  # 50-90%
            
            quiz_history.append({
                "date": date_str,
                "subject": subject,
                "difficulty": difficulty,
                "num_questions": 10,
                "num_correct": int(score / 10),
                "score_percentage": score
            })
    
    return quiz_history

def generate_sample_topic_data():
    """Generate sample topic performance data for demonstration."""
    topics = [
        {
            "topic": "Algebra",
            "strength": 85,
            "recommendation": "Continue practicing to maintain proficiency."
        },
        {
            "topic": "Calculus",
            "strength": 62,
            "recommendation": "Focus on integration techniques and applications."
        },
        {
            "topic": "Mechanics",
            "strength": 78,
            "recommendation": "Review force diagrams and circular motion."
        },
        {
            "topic": "Thermodynamics",
            "strength": 45,
            "recommendation": "Spend more time on entropy and heat transfer concepts."
        },
        {
            "topic": "Algorithms",
            "strength": 90,
            "recommendation": "Continue with advanced algorithm topics."
        },
        {
            "topic": "Data Structures",
            "strength": 82,
            "recommendation": "Practice implementing more complex data structures."
        },
        {
            "topic": "Genetics",
            "strength": 58,
            "recommendation": "Review Mendelian inheritance and gene expression."
        },
        {
            "topic": "Organic Chemistry",
            "strength": 40,
            "recommendation": "Focus on reaction mechanisms and functional groups."
        }
    ]
    
    return topics