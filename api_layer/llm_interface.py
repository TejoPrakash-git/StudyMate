import os
import google.generativeai as genai
from typing import List, Dict, Any, Optional

class GeminiInterface:
    """Interface for Google's Gemini AI model."""
    
    def __init__(self):
        """Initialize the Gemini interface with API key from environment variables."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.0-pro')
        self.embedding_model = 'embedding-001'
    
    def generate_text(self, prompt: str, temperature: float = 0.7, 
                     max_output_tokens: int = 1024, top_k: int = 40, 
                     top_p: float = 0.95) -> str:
        """Generate text using Gemini Pro model.
        
        Args:
            prompt: The input prompt for text generation
            temperature: Controls randomness (higher = more random)
            max_output_tokens: Maximum number of tokens to generate
            top_k: Sample from top k likely tokens
            top_p: Sample from tokens comprising top p probability mass
            
        Returns:
            Generated text response
        """
        generation_config = {
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "max_output_tokens": max_output_tokens,
        }
        
        response = self.model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        return response.text
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to generate embeddings for
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        for text in texts:
            embedding = genai.embed_content(
                model=self.embedding_model,
                content=text,
                task_type="retrieval_document"
            )
            embeddings.append(embedding['embedding'])
        
        return embeddings
    
    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """Have a chat conversation with the model.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            temperature: Controls randomness (higher = more random)
            
        Returns:
            Model's response text
        """
        # Convert messages to Gemini format
        gemini_messages = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            gemini_messages.append({"role": role, "parts": [msg["content"]]})
        
        chat = self.model.start_chat(history=gemini_messages)
        response = chat.send_message(
            gemini_messages[-1]["parts"][0],
            generation_config={"temperature": temperature}
        )
        
        return response.text
    
    def generate_with_context(self, query: str, context: str, 
                            temperature: float = 0.3) -> str:
        """Generate a response based on a query and context.
        
        Args:
            query: The user's question
            context: The context information to inform the response
            temperature: Controls randomness (lower = more deterministic)
            
        Returns:
            Generated response based on the context
        """
        prompt = f"""Context information is below.
        ---------------------
        {context}
        ---------------------
        Given the context information and not prior knowledge, answer the query.
        Query: {query}
        Answer:"""
        
        return self.generate_text(prompt, temperature=temperature)