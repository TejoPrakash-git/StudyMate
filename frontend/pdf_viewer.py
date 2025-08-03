import streamlit as st
import os
import tempfile
from backend.ingest.pdf_loader import PDFLoader
from backend.retrieval.rag_chain import RAGChain
from api_layer.summary import DocumentSummarizer

def render_pdf_viewer():
    """Render the PDF viewer and study assistant UI component."""
    st.header("PDF Study Assistant")
    st.write("Upload a PDF document to study and ask questions about it.")
    
    # Initialize session state variables if they don't exist
    if "pdf_text" not in st.session_state:
        st.session_state.pdf_text = None
    if "pdf_file_path" not in st.session_state:
        st.session_state.pdf_file_path = None
    if "pdf_metadata" not in st.session_state:
        st.session_state.pdf_metadata = None
    if "rag_chain" not in st.session_state:
        st.session_state.rag_chain = RAGChain("pdf_documents")
    if "pdf_qa_history" not in st.session_state:
        st.session_state.pdf_qa_history = []
    
    # File uploader
    uploaded_file = st.file_uploader("Upload a PDF document", type="pdf")
    
    if uploaded_file is not None:
        # Save the uploaded file to a temporary file
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Check if this is a new file
        if st.session_state.pdf_file_path != temp_file_path:
            st.session_state.pdf_file_path = temp_file_path
            
            # Process the PDF
            with st.spinner("Processing PDF..."):
                try:
                    # Load the PDF
                    pdf_loader = PDFLoader()
                    pdf_text, pdf_metadata = pdf_loader.load_pdf(temp_file_path)
                    
                    # Store in session state
                    st.session_state.pdf_text = pdf_text
                    st.session_state.pdf_metadata = pdf_metadata
                    
                    # Chunk the text and add to vector database
                    chunks = pdf_loader.chunk_text(pdf_text)
                    
                    # Create metadata for each chunk
                    metadatas = [{
                        "source": uploaded_file.name,
                        "chunk_index": i
                    } for i in range(len(chunks))]
                    
                    # Add to RAG chain
                    st.session_state.rag_chain.add_documents(chunks, metadatas)
                    
                    st.success(f"PDF processed successfully: {uploaded_file.name}")
                except Exception as e:
                    st.error(f"Error processing PDF: {str(e)}")
        
        # Display PDF metadata
        if st.session_state.pdf_metadata:
            with st.expander("PDF Metadata"):
                metadata = st.session_state.pdf_metadata
                st.write(f"**Title:** {metadata.get('title', 'Not available')}")
                st.write(f"**Author:** {metadata.get('author', 'Not available')}")
                st.write(f"**Pages:** {metadata.get('page_count', 0)}")
                st.write(f"**File Size:** {metadata.get('file_size', 0) // 1024} KB")
        
        # PDF content tabs
        tab1, tab2, tab3 = st.tabs(["Ask Questions", "Summarize", "View Content"])
        
        with tab1:
            # Question answering
            st.subheader("Ask questions about the document")
            question = st.text_input("Your question:", key="pdf_question")
            
            if st.button("Ask", key="ask_button"):
                if question.strip():
                    with st.spinner("Finding answer..."):
                        try:
                            # Get answer with sources
                            result = st.session_state.rag_chain.answer_with_sources(question)
                            
                            # Add to QA history
                            st.session_state.pdf_qa_history.append({
                                "question": question,
                                "answer": result["response"],
                                "sources": result["sources"]
                            })
                        except Exception as e:
                            st.error(f"Error getting answer: {str(e)}")
            
            # Display QA history
            if st.session_state.pdf_qa_history:
                st.subheader("Previous Questions & Answers")
                for i, qa in enumerate(st.session_state.pdf_qa_history):
                    with st.expander(f"Q: {qa['question']}"):
                        st.markdown(qa["answer"])
        
        with tab2:
            # Document summarization
            st.subheader("Generate a summary")
            
            col1, col2 = st.columns(2)
            with col1:
                summary_length = st.selectbox("Summary Length", ["short", "medium", "long"], index=1)
            with col2:
                focus_area = st.text_input("Focus on (optional):", key="summary_focus")
            
            if st.button("Generate Summary", key="summary_button"):
                with st.spinner("Generating summary..."):
                    try:
                        # Initialize summarizer
                        summarizer = DocumentSummarizer()
                        
                        # Generate summary
                        summary_result = summarizer.summarize_pdf(
                            st.session_state.pdf_text,
                            length=summary_length,
                            focus=focus_area if focus_area.strip() else None
                        )
                        
                        # Display summary
                        st.subheader("Summary")
                        st.write(summary_result["summary"])
                        
                        st.subheader("Key Points")
                        for point in summary_result["key_points"]:
                            st.markdown(f"- {point}")
                    except Exception as e:
                        st.error(f"Error generating summary: {str(e)}")
        
        with tab3:
            # View PDF content
            if st.session_state.pdf_text:
                st.subheader("Document Content")
                with st.expander("View Full Text"):
                    st.text_area("PDF Content", st.session_state.pdf_text, height=400)
            else:
                st.info("Upload a PDF to view its content.")
    else:
        st.info("Please upload a PDF document to get started.")