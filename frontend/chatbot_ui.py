import streamlit as st
from api_layer.llm_interface import GeminiInterface
from typing import List, Dict

def render_chatbot():
    """Render the chatbot UI component."""
    st.header("General Chatbot")
    st.write("Ask me anything about your studies or general knowledge!")
    
    # Initialize session state for chat history if it doesn't exist
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Initialize Gemini interface
    if "llm" not in st.session_state:
        try:
            st.session_state.llm = GeminiInterface()
        except Exception as e:
            st.error(f"Error initializing Gemini AI: {str(e)}")
            st.info("Please check your API key in the .env file.")
            return
    
    # Display chat history
    display_chat_history(st.session_state.chat_history)
    
    # Chat input
    user_input = st.text_input("Your question:", key="chat_input")
    
    # Send button
    if st.button("Send", key="send_button"):
        if user_input.strip():
            # Add user message to chat history
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            # Get AI response
            try:
                with st.spinner("Thinking..."):
                    # Convert chat history to format expected by the model
                    messages = [{"role": msg["role"], "content": msg["content"]} 
                              for msg in st.session_state.chat_history]
                    
                    # Get response from Gemini
                    response = st.session_state.llm.chat(messages)
                    
                    # Add AI response to chat history
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    
                    # Rerun to update the display
                    st.experimental_rerun()
            except Exception as e:
                st.error(f"Error getting response: {str(e)}")
    
    # Clear chat button
    if st.button("Clear Chat", key="clear_chat"):
        st.session_state.chat_history = []
        st.experimental_rerun()

def display_chat_history(chat_history: List[Dict[str, str]]):
    """Display the chat history in a conversational format.
    
    Args:
        chat_history: List of message dictionaries with 'role' and 'content' keys
    """
    for message in chat_history:
        if message["role"] == "user":
            st.markdown(f"<div style='background-color: #e6f7ff; padding: 10px; border-radius: 10px; margin-bottom: 10px;'>"
                      f"<strong>You:</strong><br>{message['content']}</div>", unsafe_allow_html=True)
        else:  # assistant
            st.markdown(f"<div style='background-color: #f0f0f0; padding: 10px; border-radius: 10px; margin-bottom: 10px;'>"
                      f"<strong>StudyMateZ:</strong><br>{message['content']}</div>", unsafe_allow_html=True)