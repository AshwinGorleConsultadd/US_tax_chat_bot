"""
Vector Database Module for US Tax Chatbot

This module handles Chroma DB operations for storing and retrieving
embeddings with metadata for semantic search functionality.
"""

import logging
import os
from typing import List, Dict, Any, Optional, Tuple
import chromadb
from chromadb.config import Settings
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorDatabase:
    """Handles Chroma DB operations for vector storage and retrieval."""
    
    def __init__(self, persist_directory: str = "./chroma_db", collection_name: str = "tax_documents"):
        """
        Initialize the vector database.
        
        Args:
            persist_directory: Directory to persist the database
            collection_name: Name of the Chroma collection
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Ensure persist directory exists
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize OpenAI embeddings
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=api_key
        )
        
        # Initialize Chroma DB
        self.vectordb = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings,
            collection_name=collection_name
        )
        
        logger.info(f"VectorDatabase initialized with persist_directory: {persist_directory}")
        logger.info(f"Collection name: {collection_name}")
    
    def add_chunks(self, chunks: List[Dict[str, Any]]) -> bool:
        """
        Add text chunks with embeddings to the vector database.
        
        Args:
            chunks: List of chunk dictionaries with 'text' and metadata
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Starting to add {len(chunks)} chunks to vector database")
        
        if not chunks:
            logger.warning("No chunks provided for adding to database")
            return False
        
        try:
            # Extract texts and metadata
            texts = []
            metadatas = []
            ids = []
            
            for i, chunk in enumerate(chunks):
                text = chunk.get('text', '')
                if not text.strip():
                    logger.warning(f"Skipping empty chunk {i}")
                    continue
                
                texts.append(text)
                
                # Prepare metadata (Chroma doesn't support nested dictionaries)
                metadata = {}
                for key, value in chunk.items():
                    if key != 'text' and key != 'embedding':
                        # Convert complex objects to strings
                        if isinstance(value, (dict, list)):
                            metadata[key] = str(value)
                        else:
                            metadata[key] = value
                
                metadatas.append(metadata)
                ids.append(chunk.get('chunk_id', f"chunk_{i}"))
            
            # Add to vector database
            self.vectordb.add_texts(
                texts=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            # Persist the database
            self.vectordb.persist()
            
            logger.info(f"Successfully added {len(texts)} chunks to vector database")
            return True
            
        except Exception as e:
            logger.error(f"Error adding chunks to database: {str(e)}")
            return False
    
    def search_similar(self, query: str, k: int = 5, filter_dict: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Search for similar documents using semantic similarity.
        
        Args:
            query: Search query
            k: Number of results to return
            filter_dict: Optional metadata filters
            
        Returns:
            List of similar documents with metadata
        """
        logger.info(f"Searching for similar documents to: '{query[:50]}...'")
        
        try:
            # Perform similarity search
            if filter_dict:
                results = self.vectordb.similarity_search_with_score(
                    query=query,
                    k=k,
                    filter=filter_dict
                )
            else:
                results = self.vectordb.similarity_search_with_score(
                    query=query,
                    k=k
                )
            
            # Format results
            formatted_results = []
            for doc, score in results:
                formatted_result = {
                    'text': doc.page_content,
                    'metadata': doc.metadata,
                    'similarity_score': float(score)
                }
                formatted_results.append(formatted_result)
            
            logger.info(f"Found {len(formatted_results)} similar documents")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching database: {str(e)}")
            return []
    
    def get_retriever(self, k: int = 5, filter_dict: Optional[Dict] = None):
        """
        Get a retriever for the vector database.
        
        Args:
            k: Number of documents to retrieve
            filter_dict: Optional metadata filters
            
        Returns:
            LangChain retriever object
        """
        logger.info(f"Creating retriever with k={k}")
        
        search_kwargs = {"k": k}
        if filter_dict:
            search_kwargs["filter"] = filter_dict
        
        retriever = self.vectordb.as_retriever(
            search_type="similarity",
            search_kwargs=search_kwargs
        )
        
        return retriever
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the current collection.
        
        Returns:
            Dictionary containing collection information
        """
        try:
            collection = self.vectordb._collection
            count = collection.count()
            
            info = {
                'collection_name': self.collection_name,
                'persist_directory': self.persist_directory,
                'document_count': count,
                'embedding_model': 'text-embedding-3-small'
            }
            
            logger.info(f"Collection info: {info}")
            return info
            
        except Exception as e:
            logger.error(f"Error getting collection info: {str(e)}")
            return {}
    
    def delete_collection(self) -> bool:
        """
        Delete the current collection.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Deleting collection: {self.collection_name}")
        
        try:
            # Get the Chroma client
            client = chromadb.PersistentClient(path=self.persist_directory)
            client.delete_collection(name=self.collection_name)
            
            logger.info("Collection deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting collection: {str(e)}")
            return False
    
    def reset_database(self) -> bool:
        """
        Reset the entire database by deleting and recreating the collection.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("Resetting vector database")
        
        try:
            # Delete existing collection
            self.delete_collection()
            
            # Reinitialize the vector database
            self.vectordb = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings,
                collection_name=self.collection_name
            )
            
            logger.info("Database reset successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting database: {str(e)}")
            return False
    
    def get_document_sources(self) -> List[str]:
        """
        Get list of unique document sources in the database.
        
        Returns:
            List of unique source file names
        """
        try:
            collection = self.vectordb._collection
            results = collection.get()
            
            sources = set()
            for metadata in results['metadatas']:
                if 'source_file' in metadata:
                    sources.add(metadata['source_file'])
            
            source_list = list(sources)
            logger.info(f"Found {len(source_list)} unique document sources")
            return source_list
            
        except Exception as e:
            logger.error(f"Error getting document sources: {str(e)}")
            return []


def main():
    """Test the vector database functionality."""
    try:
        # Initialize database
        db = VectorDatabase()
        
        # Get collection info
        info = db.get_collection_info()
        print(f"Collection info: {info}")
        
        # Test search (if there are documents)
        if info.get('document_count', 0) > 0:
            results = db.search_similar("tax deductions", k=3)
            print(f"Search results: {len(results)} documents found")
            for i, result in enumerate(results):
                print(f"Result {i+1}: {result['text'][:100]}...")
                print(f"Score: {result['similarity_score']}")
                print(f"Source: {result['metadata'].get('source_file', 'Unknown')}")
                print()
        else:
            print("No documents in database. Add some documents first.")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Make sure to set your OPENAI_API_KEY environment variable")


if __name__ == "__main__":
    main()
