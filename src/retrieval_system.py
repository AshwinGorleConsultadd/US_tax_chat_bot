"""
Retrieval System Module for US Tax Chatbot

This module handles semantic similarity search and retrieval
of relevant documents from the vector database.
"""

import logging
from typing import List, Dict, Any, Optional
from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RetrievalSystem:
    """Handles semantic retrieval and document search functionality."""
    
    def __init__(self, vector_database, model_name: str = "gpt-3.5-turbo"):
        """
        Initialize the retrieval system.
        
        Args:
            vector_database: VectorDatabase instance
            model_name: OpenAI model name for chat completion
        """
        self.vector_database = vector_database
        self.model_name = model_name
        
        # Initialize ChatOpenAI
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        self.llm = ChatOpenAI(
            model=model_name,
            openai_api_key=api_key,
            temperature=0.1  # Low temperature for factual responses
        )
        
        logger.info(f"RetrievalSystem initialized with model: {model_name}")
    
    def retrieve_documents(self, query: str, k: int = 5, filter_dict: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Search query
            k: Number of documents to retrieve
            filter_dict: Optional metadata filters
            
        Returns:
            List of relevant documents with metadata
        """
        logger.info(f"Retrieving documents for query: '{query[:50]}...'")
        
        try:
            # Use vector database search
            results = self.vector_database.search_similar(
                query=query,
                k=k,
                filter_dict=filter_dict
            )
            
            logger.info(f"Retrieved {len(results)} documents")
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            return []
    
    def create_context_from_documents(self, documents: List[Dict[str, Any]], max_context_length: int = 15000) -> str:
        """
        Create a context string from retrieved documents.
        
        Args:
            documents: List of retrieved documents
            max_context_length: Maximum length of context string
            
        Returns:
            Formatted context string
        """
        logger.info(f"Creating context from {len(documents)} documents")
        
        if not documents:
            return ""
        
        context_parts = []
        current_length = 0
        
        for i, doc in enumerate(documents):
            doc_text = doc['text']
            doc_source = doc['metadata'].get('source_file', 'Unknown')
            doc_score = doc.get('similarity_score', 0)
            
            # Format document with source and score
            formatted_doc = f"[Document {i+1} from {doc_source} (Relevance: {doc_score:.3f})]\n{doc_text}\n"
            
            # Check if adding this document would exceed max length
            if current_length + len(formatted_doc) > max_context_length:
                logger.info(f"Context length limit reached, using {i} documents")
                break
            
            context_parts.append(formatted_doc)
            current_length += len(formatted_doc)
        
        context = "\n".join(context_parts)
        logger.info(f"Created context with {len(context_parts)} documents, {len(context)} characters")
        
        return context
    
    def generate_answer(self, query: str, context: str, chat_history: List[Dict[str, str]] = None) -> str:
        """
        Generate an answer using the LLM with context and chat history.
        
        Args:
            query: User query
            context: Retrieved context
            chat_history: Previous conversation history
            
        Returns:
            Generated answer
        """
        logger.info("Generating answer with LLM")
        
        try:
            # Create system prompt
            system_prompt = """You are a helpful AI assistant specialized in US tax regulations. 
            You have access to authoritative tax documents and can provide accurate, context-aware answers.
            
            Instructions:
            1. Use only the provided context to answer questions
            2. If the context doesn't contain enough information, say "I don't have enough context in the available documents to answer this question accurately"
            3. Be precise and cite relevant sections when possible
            4. If asked about something not related to taxes, politely redirect to tax-related questions
            5. Always be helpful and professional"""
            
            # Create messages list
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add chat history if provided
            if chat_history:
                for message in chat_history:
                    messages.append(message)
            
            # Add current context and query
            if context:
                context_message = f"""Context from tax documents:
                {context}
                
                User Question: {query}
                
                Please answer the user's question based on the provided context. If the context doesn't contain enough information to answer the question accurately, please say so."""
            else:
                context_message = f"""User Question: {query}
                
                I don't have access to any relevant tax documents to answer this question. Please upload some tax documents first."""
            
            messages.append({"role": "user", "content": context_message})
            
            # Generate response
            response = self.llm.invoke(messages)
            
            # Extract content from response
            if hasattr(response, 'content'):
                answer = response.content
            else:
                answer = str(response)
            
            logger.info("Successfully generated answer")
            return answer
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return "I apologize, but I encountered an error while generating a response. Please try again."
    
    def process_query(self, query: str, k: int = 12, chat_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Process a complete query: retrieve documents, create context, and generate answer.
        
        Args:
            query: User query
            k: Number of documents to retrieve
            chat_history: Previous conversation history
            
        Returns:
            Dictionary containing answer, retrieved documents, and metadata
        """
        logger.info(f"Processing query: '{query[:50]}...'")
        
        try:
            # Retrieve relevant documents
            documents = self.retrieve_documents(query, k=k)
            
            # Create context
            context = self.create_context_from_documents(documents)
            
            # Generate answer
            answer = self.generate_answer(query, context, chat_history)
            
            result = {
                'answer': answer,
                'retrieved_documents': documents,
                'context_length': len(context),
                'num_documents': len(documents),
                'query': query
            }
            
            logger.info(f"Successfully processed query, retrieved {len(documents)} documents")
            return result
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                'answer': "I apologize, but I encountered an error while processing your query. Please try again.",
                'retrieved_documents': [],
                'context_length': 0,
                'num_documents': 0,
                'query': query,
                'error': str(e)
            }
    
    def get_retrieval_stats(self, query: str, k: int = 5) -> Dict[str, Any]:
        """
        Get statistics about retrieval performance for a query.
        
        Args:
            query: Search query
            k: Number of documents to retrieve
            
        Returns:
            Dictionary containing retrieval statistics
        """
        logger.info(f"Getting retrieval stats for query: '{query[:50]}...'")
        
        try:
            documents = self.retrieve_documents(query, k=k)
            
            if not documents:
                return {'num_documents': 0, 'avg_score': 0, 'min_score': 0, 'max_score': 0}
            
            scores = [doc.get('similarity_score', 0) for doc in documents]
            
            stats = {
                'num_documents': len(documents),
                'avg_score': sum(scores) / len(scores),
                'min_score': min(scores),
                'max_score': max(scores),
                'scores': scores
            }
            
            logger.info(f"Retrieval stats: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error getting retrieval stats: {str(e)}")
            return {'error': str(e)}


def main():
    """Test the retrieval system functionality."""
    try:
        from vector_database import VectorDatabase
        
        # Initialize components
        db = VectorDatabase()
        retrieval_system = RetrievalSystem(db)
        
        # Test query
        query = "What are the different types of tax deductions?"
        
        print(f"Testing retrieval system with query: '{query}'")
        
        # Process query
        result = retrieval_system.process_query(query, k=3)
        
        print(f"Answer: {result['answer']}")
        print(f"Retrieved {result['num_documents']} documents")
        print(f"Context length: {result['context_length']} characters")
        
        # Get retrieval stats
        stats = retrieval_system.get_retrieval_stats(query, k=3)
        print(f"Retrieval stats: {stats}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Make sure to set your OPENAI_API_KEY environment variable and have documents in the database")


if __name__ == "__main__":
    main()
