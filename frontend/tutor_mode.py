import streamlit as st
from api_layer.llm_interface import GeminiInterface
from typing import List, Dict

def render_tutor():
    """Render the tutor mode UI component."""
    st.header("Tutor Mode")
    st.write("Get personalized tutoring on any subject.")
    
    # Initialize session state variables if they don't exist
    if "tutor_history" not in st.session_state:
        st.session_state.tutor_history = []
    if "tutor_subject" not in st.session_state:
        st.session_state.tutor_subject = ""
    if "tutor_level" not in st.session_state:
        st.session_state.tutor_level = "high school"
    if "tutor_llm" not in st.session_state:
        try:
            st.session_state.tutor_llm = GeminiInterface()
        except Exception as e:
            st.error(f"Error initializing Gemini AI: {str(e)}")
            st.info("Please check your API key in the .env file.")
            return
    
    # Tutor configuration
    with st.sidebar:
        st.subheader("Tutor Settings")
        
        # Subject selection
        subject = st.text_input("Subject", value=st.session_state.tutor_subject, 
                              placeholder="e.g., Calculus, Physics, Programming")
        
        # Education level
        level = st.selectbox(
            "Education Level",
            ["elementary", "middle school", "high school", "undergraduate", "graduate"],
            index=["elementary", "middle school", "high school", "undergraduate", "graduate"].index(st.session_state.tutor_level)
        )
        
        # Update session state if changed
        if subject != st.session_state.tutor_subject or level != st.session_state.tutor_level:
            st.session_state.tutor_subject = subject
            st.session_state.tutor_level = level
            
            # Add system message to history if subject is provided
            if subject and not st.session_state.tutor_history:
                system_message = f"You are now a {level} level tutor for {subject}. Provide clear explanations, examples, and guidance appropriate for this level."
                st.session_state.tutor_history = [{"role": "system", "content": system_message}]
    
    # Main tutor interface
    if st.session_state.tutor_subject:
        st.subheader(f"{st.session_state.tutor_subject} Tutor ({st.session_state.tutor_level} level)")
    else:
        st.info("Please enter a subject in the sidebar to begin tutoring.")
    
    # Display chat history
    display_tutor_history(st.session_state.tutor_history)
    
    # User input
    user_input = st.text_area("Your question:", height=100, key="tutor_input")
    
    col1, col2 = st.columns([1, 5])
    with col1:
        # Send button
        if st.button("Send", key="tutor_send_button"):
            if user_input.strip():
                # Check if we need to initialize with system message
                if not st.session_state.tutor_history and st.session_state.tutor_subject:
                    system_message = f"You are now a {st.session_state.tutor_level} level tutor for {st.session_state.tutor_subject}. Provide clear explanations, examples, and guidance appropriate for this level."
                    st.session_state.tutor_history.append({"role": "system", "content": system_message})
                
                # Add user message to history
                st.session_state.tutor_history.append({"role": "user", "content": user_input})
                
                # Get AI response
                try:
                    with st.spinner("Thinking..."):
                        # Get response from Gemini
                        messages = st.session_state.tutor_history.copy()
                        
                        # If no system message, add one
                        if messages[0]["role"] != "system":
                            system_message = f"You are now a {st.session_state.tutor_level} level tutor for {st.session_state.tutor_subject}. Provide clear explanations, examples, and guidance appropriate for this level."
                            messages.insert(0, {"role": "system", "content": system_message})
                        
                        response = st.session_state.tutor_llm.generate_text(
                            f"As a {st.session_state.tutor_level} level tutor for {st.session_state.tutor_subject}, respond to this student question: {user_input}"
                        )
                        
                        # Add AI response to history
                        st.session_state.tutor_history.append({"role": "assistant", "content": response})
                        
                        # Rerun to update the display
                        st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error getting response: {str(e)}")
    
    with col2:
        # Clear chat button
        if st.button("Start New Session", key="tutor_clear_button"):
            st.session_state.tutor_history = []
            st.experimental_rerun()
    
    # Additional tutor features
    if st.session_state.tutor_subject:
        with st.expander("Tutor Tools"):
            tool_tab1, tool_tab2, tool_tab3 = st.tabs(["Practice Problems", "Concept Explanation", "Learning Resources"])
            
            with tool_tab1:
                st.subheader("Generate Practice Problems")
                difficulty = st.select_slider(
                    "Difficulty",
                    options=["Easy", "Medium", "Hard"],
                    value="Medium"
                )
                
                if st.button("Generate Problems", key="generate_problems_button"):
                    with st.spinner("Generating practice problems..."):
                        try:
                            prompt = f"Generate 3 {difficulty.lower()} {st.session_state.tutor_subject} practice problems appropriate for {st.session_state.tutor_level} level. Include the solution for each problem."
                            
                            response = st.session_state.tutor_llm.generate_text(prompt, temperature=0.7)
                            
                            st.markdown(response)
                        except Exception as e:
                            st.error(f"Error generating problems: {str(e)}")
            
            with tool_tab2:
                st.subheader("Explain a Concept")
                concept = st.text_input("Enter a concept to explain:", placeholder="e.g., Derivatives, Newton's Laws")
                
                if st.button("Explain", key="explain_concept_button") and concept:
                    with st.spinner("Generating explanation..."):
                        try:
                            prompt = f"Explain the concept of {concept} in {st.session_state.tutor_subject} at a {st.session_state.tutor_level} level. Include examples and visual descriptions where appropriate."
                            
                            response = st.session_state.tutor_llm.generate_text(prompt, temperature=0.3)
                            
                            st.markdown(response)
                        except Exception as e:
                            st.error(f"Error explaining concept: {str(e)}")
            
            with tool_tab3:
                st.subheader("Learning Resources")
                
                if st.button("Recommend Resources", key="recommend_resources_button"):
                    with st.spinner("Finding resources..."):
                        try:
                            prompt = f"Recommend learning resources for {st.session_state.tutor_subject} at a {st.session_state.tutor_level} level. Include books, websites, videos, and online courses. Format as a bulleted list with brief descriptions."
                            
                            response = st.session_state.tutor_llm.generate_text(prompt, temperature=0.3)
                            
                            st.markdown(response)
                        except Exception as e:
                            st.error(f"Error recommending resources: {str(e)}")

def display_tutor_history(tutor_history: List[Dict[str, str]]):
    """Display the tutor conversation history.
    
    Args:
        tutor_history: List of message dictionaries with 'role' and 'content' keys
    """
    for message in tutor_history:
        if message["role"] == "system":
            # Don't display system messages to the user
            continue
        elif message["role"] == "user":
            st.markdown(f"<div style='background-color: #e6f7ff; padding: 10px; border-radius: 10px; margin-bottom: 10px;'>"
                      f"<strong>You:</strong><br>{message['content']}</div>", unsafe_allow_html=True)
        else:  # assistant
            st.markdown(f"<div style='background-color: #f0f0f0; padding: 10px; border-radius: 10px; margin-bottom: 10px;'>"
                      f"<strong>Tutor:</strong><br>{message['content']}</div>", unsafe_allow_html=True)