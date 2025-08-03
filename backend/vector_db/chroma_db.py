import os
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
from api_layer.llm_interface import GeminiInterface

class ChromaDBManager:
    """Manages interactions with ChromaDB for vector storage and retrieval."""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize the ChromaDB Manager.
        
        Args:
            persist_directory: Directory to persist the database
        """
        # Create the persist directory if it doesn't exist
        if not os.path.exists(persist_directory):
            os.makedirs(persist_directory)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Initialize Gemini interface for embeddings
        self.llm = GeminiInterface()
    
    def create_collection(self, collection_name: str) -> Any:
        """Create a new collection or get an existing one.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            ChromaDB collection object
        """
        try:
            # Try to get the collection if it exists
            collection = self.client.get_collection(collection_name)
            return collection
        except:
            # Create a new collection if it doesn't exist
            collection = self.client.create_collection(collection_name)
            return collection
    
    def add_documents(self, collection_name: str, documents: List[str], 
                     metadatas: Optional[List[Dict[str, Any]]] = None, 
                     ids: Optional[List[str]] = None) -> None:
        """Add documents to a collection.
        
        Args:
            collection_name: Name of the collection
            documents: List of document texts
            metadatas: Optional list of metadata dictionaries
            ids: Optional list of document IDs
        """
        # Get or create the collection
        collection = self.create_collection(collection_name)
        
        # Generate embeddings for the documents
        embeddings = self.llm.get_embeddings(documents)
        
        # Generate IDs if not provided
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(documents))]
        
        # Add documents to the collection
        collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    
    def query_collection(self, collection_name: str, query_text: str, 
                        n_results: int = 5) -> Dict[str, Any]:
        """Query a collection for similar documents.
        
        Args:
            collection_name: Name of the collection
            query_text: Query text to find similar documents
            n_results: Number of results to return
            
        Returns:
            Dictionary with query results
        """
        # Get the collection
        collection = self.create_collection(collection_name)
        
        # Generate embedding for the query
        query_embedding = self.llm.get_embeddings([query_text])[0]
        
        # Query the collection
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        
        return results
    
    def delete_collection(self, collection_name: str) -> None:
        """Delete a collection.
        
        Args:
            collection_name: Name of the collection to delete
        """
        self.client.delete_collection(collection_name)
    
    def list_collections(self) -> List[str]:
        """List all collections in the database.
        
        Returns:
            List of collection names
        """
        return self.client.list_collections()
    
    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get information about a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Dictionary with collection information
        """
        collection = self.create_collection(collection_name)
        return {
            "name": collection_name,
            "count": collection.count()
        }