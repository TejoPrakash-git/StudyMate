# StudyMateZ - AI-Powered Study Assistant

## Overview

StudyMateZ is a comprehensive AI-powered study assistant application built with Streamlit and Google's Gemini AI. It provides a suite of tools to enhance the learning experience, including PDF analysis, quiz generation, summarization, concept mapping, and more.

## Features

### PDF Study Assistant
- Upload and analyze PDF documents
- Ask questions about the content using RAG (Retrieval Augmented Generation)
- View document metadata and structure

### General Chatbot
- Interact with the AI assistant for general questions
- Get help with various subjects and topics

### Quiz Generator
- Create quizzes based on PDF content or custom text
- Multiple-choice questions with automatic grading
- Adjustable difficulty levels

### Summarizer
- Generate concise summaries of documents
- Customize summary length and focus

### Concept Map
- Visualize relationships between concepts
- Identify key connections in study materials

### Tutor Mode
- Get personalized tutoring in various subjects
- Receive explanations and practice problems

### Handwriting Recognition
- Upload images of handwritten notes for digital conversion
- Edit, format, and summarize the extracted text

### Analytics
- Track study time and performance
- Analyze quiz results and identify areas for improvement

## Technical Implementation

### Architecture

The application follows a modular architecture:

- **api_layer/**: Interfaces for AI models and functionalities
- **backend/**: Core processing logic
- **frontend/**: User interface components
- **utils/**: Utility functions

### Key Components

- **LLM Interface**: Core component that interfaces with Gemini AI
- **Vector Database**: Uses ChromaDB for storing and retrieving document embeddings
- **RAG Chain**: Implements Retrieval Augmented Generation for context-aware responses

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

## Running the Application

Start the application with:

```
python -m streamlit run app.py
```

The application will be available at http://localhost:8501

## Dependencies

- streamlit
- python-dotenv
- google-generativeai
- langchain and langchain-google-genai
- pymupdf (for PDF processing)
- chromadb (for vector storage)
- nltk (for text processing)
- pandas, matplotlib, altair (for data visualization)
- pydub (for audio processing)

## License

MIT