import streamlit as st
import json
import random
from api_layer.revision import RevisionHelper

def render_flashcards():
    """Render the flashcard UI component."""
    st.header("Flashcards")
    st.write("Create and study flashcards generated from your study materials.")
    
    # Initialize session state variables if they don't exist
    if "flashcards" not in st.session_state:
        st.session_state.flashcards = []
    if "current_card_index" not in st.session_state:
        st.session_state.current_card_index = 0
    if "card_flipped" not in st.session_state:
        st.session_state.card_flipped = False
    if "revision_helper" not in st.session_state:
        st.session_state.revision_helper = RevisionHelper()
    
    # Flashcard generation options
    st.subheader("Generate Flashcards")
    
    # Source selection
    flashcard_source = st.radio(
        "Flashcard Source",
        ["From PDF", "From Text Input"]
    )
    
    # Number of cards to generate
    num_cards = st.slider("Number of Flashcards", min_value=5, max_value=20, value=10)
    
    # Source-specific inputs
    if flashcard_source == "From PDF":
        if "pdf_text" in st.session_state and st.session_state.pdf_text:
            st.success("Using the currently loaded PDF.")
            content_source = st.session_state.pdf_text
        else:
            st.warning("No PDF loaded. Please upload a PDF in the PDF Study Assistant section first.")
            content_source = None
    
    elif flashcard_source == "From Text Input":
        content_source = st.text_area("Enter the study material text:", height=200)
    
    # Generate flashcards button
    if st.button("Generate Flashcards", key="generate_flashcards_button"):
        if content_source:
            with st.spinner("Generating flashcards..."):
                try:
                    # Generate flashcards
                    flashcards = st.session_state.revision_helper.generate_flashcards(
                        content_source, num_cards
                    )
                    
                    if flashcards and len(flashcards) > 0:
                        st.session_state.flashcards = flashcards
                        st.session_state.current_card_index = 0
                        st.session_state.card_flipped = False
                        st.success(f"Generated {len(flashcards)} flashcards!")
                    else:
                        st.error("Failed to generate flashcards. Please try again.")
                except Exception as e:
                    st.error(f"Error generating flashcards: {str(e)}")
        else:
            st.warning("Please provide content to generate flashcards from.")
    
    # Display flashcards if available
    if st.session_state.flashcards:
        st.subheader("Study Flashcards")
        
        # Flashcard navigation
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col1:
            if st.button("Previous", key="prev_card"):
                st.session_state.current_card_index = (st.session_state.current_card_index - 1) % len(st.session_state.flashcards)
                st.session_state.card_flipped = False
        
        with col3:
            if st.button("Next", key="next_card"):
                st.session_state.current_card_index = (st.session_state.current_card_index + 1) % len(st.session_state.flashcards)
                st.session_state.card_flipped = False
        
        # Display current card
        current_card = st.session_state.flashcards[st.session_state.current_card_index]
        card_progress = f"Card {st.session_state.current_card_index + 1} of {len(st.session_state.flashcards)}"
        
        # Flashcard display
        with st.container():
            st.markdown(f"<p style='text-align: center; color: gray;'>{card_progress}</p>", unsafe_allow_html=True)
            
            # Card styling
            card_style = """
            <style>
            .flashcard {
                background-color: #ffffff;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                padding: 20px;
                min-height: 200px;
                display: flex;
                align-items: center;
                justify-content: center;
                text-align: center;
                margin: 20px 0;
                cursor: pointer;
            }
            .flashcard-content {
                font-size: 1.2rem;
                font-weight: 500;
            }
            </style>
            """
            st.markdown(card_style, unsafe_allow_html=True)
            
            # Card content
            if st.session_state.card_flipped:
                card_content = current_card.get("back", "No answer available")
                card_label = "Answer"
            else:
                card_content = current_card.get("front", "No question available")
                card_label = "Question"
            
            # Display the card
            card_html = f"""
            <div class='flashcard' onclick="this.classList.toggle('flipped')">
                <div class='flashcard-content'>
                    <p><strong>{card_label}:</strong></p>
                    <p>{card_content}</p>
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            
            # Flip button
            if st.button("Flip Card", key="flip_card"):
                st.session_state.card_flipped = not st.session_state.card_flipped
        
        # Shuffle button
        if st.button("Shuffle Cards", key="shuffle_cards"):
            random.shuffle(st.session_state.flashcards)
            st.session_state.current_card_index = 0
            st.session_state.card_flipped = False
        
        # Export flashcards
        if st.button("Export Flashcards", key="export_cards"):
            flashcards_json = json.dumps(st.session_state.flashcards, indent=2)
            st.download_button(
                label="Download Flashcards (JSON)",
                data=flashcards_json,
                file_name="flashcards.json",
                mime="application/json"
            )