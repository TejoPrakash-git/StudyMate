from typing import List, Dict, Any, Optional
from api_layer.llm_interface import GeminiInterface
from backend.vector_db.chroma_db import ChromaDBManager

class RAGChain:
    """Implements Retrieval Augmented Generation for context-aware responses."""
    
    def __init__(self, collection_name: str = "default_collection"):
        """Initialize the RAG Chain.
        
        Args:
            collection_name: Name of the collection to use for retrieval
        """
        self.llm = GeminiInterface()
        self.vector_db = ChromaDBManager()
        self.collection_name = collection_name
    
    def add_documents(self, documents: List[str], 
                     metadatas: Optional[List[Dict[str, Any]]] = None, 
                     ids: Optional[List[str]] = None) -> None:
        """Add documents to the vector database.
        
        Args:
            documents: List of document texts
            metadatas: Optional list of metadata dictionaries
            ids: Optional list of document IDs
        """
        self.vector_db.add_documents(self.collection_name, documents, metadatas, ids)
    
    def retrieve(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """Retrieve relevant documents for a query.
        
        Args:
            query: Query text
            n_results: Number of results to retrieve
            
        Returns:
            List of retrieved documents with metadata
        """
        results = self.vector_db.query_collection(self.collection_name, query, n_results)
        
        retrieved_docs = []
        for i in range(len(results["ids"][0])):
            retrieved_docs.append({
                "id": results["ids"][0][i],
                "document": results["documents"][0][i],
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                "distance": results["distances"][0][i]
            })
        
        return retrieved_docs
    
    def generate_response(self, query: str, n_results: int = 3) -> Dict[str, Any]:
        """Generate a response based on retrieved context.
        
        Args:
            query: User query
            n_results: Number of context documents to retrieve
            
        Returns:
            Dictionary with response and retrieved context
        """
        # Retrieve relevant documents
        retrieved_docs = self.retrieve(query, n_results)
        
        # Combine retrieved documents into context
        context = "\n\n".join([doc["document"] for doc in retrieved_docs])
        
        # Generate response using the context
        response = self.llm.generate_with_context(query, context)
        
        return {
            "response": response,
            "context": retrieved_docs
        }
    
    def answer_with_sources(self, query: str, n_results: int = 3) -> Dict[str, Any]:
        """Generate a response with source citations.
        
        Args:
            query: User query
            n_results: Number of context documents to retrieve
            
        Returns:
            Dictionary with response and source information
        """
        # Retrieve relevant documents
        retrieved_docs = self.retrieve(query, n_results)
        
        # Combine retrieved documents into context
        context_parts = []
        for i, doc in enumerate(retrieved_docs):
            source_info = f"Source {i+1}: {doc['metadata'].get('source', 'Unknown')}"
            context_parts.append(f"{doc['document']}\n{source_info}")
        
        context = "\n\n".join(context_parts)
        
        # Create a prompt that asks for citations
        prompt = f"""Context information is below.
        ---------------------
        {context}
        ---------------------
        Given the context information and not prior knowledge, answer the query and cite your sources.
        Query: {query}
        Answer (include [Source X] citations):"""
        
        # Generate response
        response = self.llm.generate_text(prompt, temperature=0.3)
        
        return {
            "response": response,
            "sources": [{
                "id": doc["id"],
                "metadata": doc["metadata"]
            } for doc in retrieved_docs]
        }