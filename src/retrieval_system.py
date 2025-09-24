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
    
    def retrieve_documents(self, query: str, k: int = 20, filter_dict: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query with enhanced retrieval strategy.
        
        Args:
            query: Search query
            k: Number of documents to retrieve (increased default)
            filter_dict: Optional metadata filters
            
        Returns:
            List of relevant documents with metadata
        """
        logger.info(f"Retrieving documents for query: '{query[:50]}...'")
        
        try:
            # Use vector database search with increased k for more comprehensive results
            results = self.vector_database.search_similar(
                query=query,
                k=k,
                filter_dict=filter_dict
            )
            
            # Filter out very low relevance documents
            filtered_results = []
            for doc in results:
                similarity_score = doc.get('similarity_score', 0)
                # Only include documents with reasonable relevance (adjust threshold as needed)
                if similarity_score > 0.3:  # Minimum relevance threshold
                    filtered_results.append(doc)
            
            logger.info(f"Retrieved {len(results)} documents, filtered to {len(filtered_results)} relevant documents")
            return filtered_results
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            return []
    
    def create_context_from_documents(self, documents: List[Dict[str, Any]], max_context_length: int = 15000) -> str:
        """
        Create a context string from retrieved documents with enhanced source attribution.
        
        Args:
            documents: List of retrieved documents
            max_context_length: Maximum length of context string
            
        Returns:
            Formatted context string with detailed source information
        """
        logger.info(f"Creating context from {len(documents)} documents")
        
        if not documents:
            return ""
        
        context_parts = []
        current_length = 0
        
        for i, doc in enumerate(documents):
            doc_text = doc['text']
            metadata = doc['metadata']
            doc_source = metadata.get('source_file', 'Unknown Document')
            page_number = metadata.get('page_number', 'Unknown Page')
            chunk_index = metadata.get('chunk_index', 'Unknown Section')
            doc_score = doc.get('similarity_score', 0)
            
            # Create enhanced source attribution
            source_info = f"[Document {i+1}: {doc_source}"
            if page_number != 'Unknown Page':
                source_info += f", Page {page_number}"
            if chunk_index != 'Unknown Section':
                source_info += f", Section {chunk_index}"
            source_info += f" (Relevance: {doc_score:.3f})]"
            
            # Format document with enhanced source information
            formatted_doc = f"{source_info}\n{doc_text}\n"
            
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
            Generated answer with source attribution
        """
        logger.info("Generating answer with LLM")
        
        try:
            # Determine if we have sufficient context
            has_context = bool(context and len(context.strip()) > 100)
            
            # Create enhanced system prompt
            system_prompt = """You are an expert US Tax Assistant with deep knowledge of tax regulations, IRS publications, and tax law. You provide comprehensive, accurate, and well-structured answers to tax-related questions.

            Your response style should be:
            1. DETAILED and EXPLANATORY - Provide thorough explanations, not just brief answers
            2. STRUCTURED - Use clear headings, bullet points, and organized sections
            3. AUTHORITATIVE - Cite specific sources, publications, or sections when referencing documents
            4. PRACTICAL - Include relevant examples, scenarios, and actionable advice
            5. COMPREHENSIVE - Cover all relevant aspects of the question

            When you have access to relevant documents:
            - Use both the provided context AND your extensive tax knowledge
            - Always mention when information comes from specific documents/publications
            - Provide detailed explanations even when context is available
            - Structure your response with clear sections and subsections

            When context is limited or insufficient:
            - Rely on your comprehensive tax knowledge
            - Provide detailed explanations based on general tax principles
            - Clearly indicate when you're using general knowledge vs. specific documents
            - Still provide structured, comprehensive answers

            Always be professional, accurate, and helpful. If asked about non-tax topics, politely redirect to tax-related questions."""
            
            # Create messages list
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add chat history if provided
            if chat_history:
                for message in chat_history:
                    messages.append(message)
            
            # Create enhanced context message with source attribution
            if has_context:
                context_message = f"""CONTEXT FROM TAX DOCUMENTS:
{context}

USER QUESTION: {query}

INSTRUCTIONS:
- FIRST, evaluate whether the provided context contains useful and relevant information to answer the user's question
- If the context is relevant and contains useful information:
  - Provide a DETAILED, STRUCTURED, and COMPREHENSIVE answer
  - Use BOTH the provided context AND your extensive tax knowledge to enhance and improve the answer
  - When referencing information from the documents, mention the specific source (e.g., "According to [Publication Name]" or "As stated in [Document Title]")
  - Structure your response with clear headings and organized sections
  - Include relevant examples and practical guidance
  - Enhance the provided context with your additional tax expertise and knowledge
  - Start your response with: "**Source: context + reasoning**"
- If the context does NOT contain relevant or useful information for answering the question:
  - Provide a DETAILED, STRUCTURED, and COMPREHENSIVE answer using only your extensive tax knowledge
  - Structure your response with clear headings and organized sections
  - Include relevant examples, scenarios, and practical guidance
  - Start your response with: "**Source: reasoning**"
  - Do NOT mention that the context lacks information - just provide the answer directly

RESPONSE FORMAT:
Choose the appropriate source attribution based on context relevance:
- "**Source: context + reasoning**" (if context is useful)
- "**Source: reasoning**" (if context is not useful)
Then provide your comprehensive answer."""
            else:
                context_message = f"""USER QUESTION: {query}

INSTRUCTIONS:
- Provide a DETAILED, STRUCTURED, and COMPREHENSIVE answer using your extensive tax knowledge
- Structure your response with clear headings and organized sections
- Include relevant examples, scenarios, and practical guidance
- Be thorough and explanatory in your response
- Do NOT mention that the knowledge base lacks context - just provide the answer directly

RESPONSE FORMAT:
Start your response with: "**Source: reasoning**"
Then provide your comprehensive answer."""
            
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
    
    def process_query(self, query: str, k: int = 20, chat_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
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
