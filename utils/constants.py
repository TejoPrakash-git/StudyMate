# Application constants for StudyMateZ

# Application settings
APP_TITLE = "StudyMateZ"
APP_ICON = "📚"
APP_DESCRIPTION = "Your AI-powered study assistant"

# UI settings
PRIMARY_COLOR = "#4F8BF9"  # Primary blue color
SECONDARY_COLOR = "#FF4B4B"  # Secondary red color
BACKGROUND_COLOR = "#F0F2F6"  # Light background color
TEXT_COLOR = "#262730"  # Dark text color

# Feature names
FEATURE_PDF_ASSISTANT = "PDF Study Assistant"
FEATURE_CHATBOT = "General Chatbot"
FEATURE_QUIZ = "Quiz Generator"
FEATURE_SUMMARIZER = "Summarizer"
FEATURE_CONCEPT_MAP = "Concept Map"
FEATURE_TUTOR = "Tutor Mode"
FEATURE_HANDWRITING = "Handwriting Recognition"
FEATURE_ANALYTICS = "Analytics"

# AI model settings
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TOP_P = 0.95
DEFAULT_TOP_K = 40
MAX_OUTPUT_TOKENS = 2048

# PDF processing settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
MAX_PDF_SIZE_MB = 10

# Vector database settings
COLLECTION_NAME_PREFIX = "studymatez_"
PERSISTENCE_DIRECTORY = "./chroma_db"

# Quiz generation settings
DEFAULT_NUM_QUESTIONS = 5
DEFAULT_NUM_OPTIONS = 4
QUIZ_DIFFICULTY_LEVELS = ["Easy", "Medium", "Hard"]

# Summary settings
SUMMARY_LENGTH_OPTIONS = ["Short", "Medium", "Long"]
SUMMARY_FOCUS_OPTIONS = ["Key Concepts", "Comprehensive", "Simplified"]

# Revision settings
FLASHCARD_DEFAULT_COUNT = 10
STUDY_GUIDE_SECTIONS = ["Key Concepts", "Definitions", "Summary", "Practice Questions"]

# Voice settings
AUDIO_SAMPLE_RATE = 16000
AUDIO_CHANNELS = 1

# Error messages
ERROR_API_KEY = "API key not found. Please check your .env file."
ERROR_PDF_UPLOAD = "Error uploading PDF. Please try again."
ERROR_MODEL_LOAD = "Error loading AI model. Please check your connection."
ERROR_VECTOR_DB = "Error connecting to vector database."

# Success messages
SUCCESS_PDF_UPLOAD = "PDF uploaded successfully!"
SUCCESS_QUIZ_GENERATION = "Quiz generated successfully!"
SUCCESS_SUMMARY_GENERATION = "Summary generated successfully!"