import streamlit as st
import os
from dotenv import load_dotenv

# Import components
from frontend.chatbot_ui import render_chatbot
from frontend.pdf_viewer import render_pdf_viewer
from frontend.quiz_ui import render_quiz
from frontend.analytics_dashboard import render_analytics
from frontend.concept_map import render_concept_map
from frontend.tutor_mode import render_tutor
from frontend.handwriting_recognition import render_handwriting
from frontend.flashcard_ui import render_flashcards

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(page_title="StudyMateZ", page_icon="📚", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
    }
    .stApp {
        background-color: #000000;
    }
    h1, h2, h3 {
        color: #ffffff;
    }
    .stRadio label, .stRadio div, p, span {
        color: #ffffff;
    }
    .stSidebar .stRadio label {
        color: #ffffff;
    }
    .stMarkdown {
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# App title
st.title("StudyMateZ - AI Study Assistant")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select a feature:",
    ["PDF Study Assistant", "General Chatbot", "Quiz Generator", 
     "Summarizer", "Concept Map", "Flashcards", "Tutor Mode", "Handwriting Recognition", "Analytics"]
)

# Display selected page
if page == "PDF Study Assistant":
    render_pdf_viewer()

elif page == "General Chatbot":
    render_chatbot()

elif page == "Quiz Generator":
    render_quiz()

elif page == "Summarizer":
    st.header("Document Summarizer")
    # Implement summarizer UI here
    uploaded_file = st.file_uploader("Upload a document to summarize", type=["pdf", "txt", "docx"])
    if uploaded_file is not None:
        if st.button("Generate Summary"):
            st.info("Generating summary... Please wait.")
            # Call summary function here
            st.success("Summary generated!")
            st.markdown("### Summary")
            st.write("This is a placeholder for the generated summary.")

elif page == "Concept Map":
    render_concept_map()

elif page == "Flashcards":
    render_flashcards()

elif page == "Tutor Mode":
    render_tutor()

elif page == "Handwriting Recognition":
    render_handwriting()

elif page == "Analytics":
    render_analytics()

# Footer
st.markdown("---")
st.markdown("© 2023 StudyMateZ - Powered by Google Gemini AI")