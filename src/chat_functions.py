"""
Chat Functions Module for US Tax Chatbot

This module provides the main chat interface functions including
send_message and reset_chat with proper context management.
"""

import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatManager:
    """Manages chat sessions with context preservation."""
    
    def __init__(self):
        """Initialize the chat manager."""
        self.chat_history: List[Dict[str, str]] = []
        self.retrieval_system = None
        self.vector_database = None
        
        logger.info("ChatManager initialized")
    
    def initialize_components(self):
        """Initialize the retrieval system and vector database."""
        try:
            from vector_database import VectorDatabase
            from retrieval_system import RetrievalSystem
            
            # Initialize vector database
            self.vector_database = VectorDatabase()
            
            # Initialize retrieval system
            self.retrieval_system = RetrievalSystem(self.vector_database)
            
            logger.info("Chat components initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing chat components: {str(e)}")
            return False
    
    def send_message(self, message: str) -> str:
        """
        Send a message and get a response with context preservation.
        
        Args:
            message: User message
            
        Returns:
            AI response
        """
        logger.info(f"Processing message: '{message[:50]}...'")
        
        # Initialize components if not already done
        if not self.retrieval_system:
            if not self.initialize_components():
                return "Error: Unable to initialize chat components. Please check your configuration."
        
        try:
            # Process the query with chat history
            result = self.retrieval_system.process_query(
                query=message,
                k=5,
                chat_history=self.chat_history
            )
            
            # Add user message and AI response to chat history
            self.chat_history.append({"role": "user", "content": message})
            self.chat_history.append({"role": "assistant", "content": result['answer']})
            
            # Limit chat history to prevent context overflow (keep last 10 exchanges)
            max_history = 20  # 10 user + 10 assistant messages
            if len(self.chat_history) > max_history:
                self.chat_history = self.chat_history[-max_history:]
            
            logger.info(f"Successfully processed message, chat history length: {len(self.chat_history)}")
            return result['answer']
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return f"I apologize, but I encountered an error while processing your message: {str(e)}"
    
    def reset_chat(self) -> bool:
        """
        Reset the chat session history.
        
        Returns:
            True if successful
        """
        logger.info("Resetting chat session")
        
        try:
            self.chat_history = []
            logger.info("Chat session reset successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting chat: {str(e)}")
            return False
    
    def get_chat_history(self) -> List[Dict[str, str]]:
        """
        Get the current chat history.
        
        Returns:
            List of chat messages
        """
        return self.chat_history.copy()
    
    def get_chat_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current chat session.
        
        Returns:
            Dictionary containing chat statistics
        """
        user_messages = [msg for msg in self.chat_history if msg['role'] == 'user']
        assistant_messages = [msg for msg in self.chat_history if msg['role'] == 'assistant']
        
        stats = {
            'total_messages': len(self.chat_history),
            'user_messages': len(user_messages),
            'assistant_messages': len(assistant_messages),
            'conversation_turns': len(user_messages)
        }
        
        logger.info(f"Chat stats: {stats}")
        return stats
    
    def is_initialized(self) -> bool:
        """
        Check if the chat manager is properly initialized.
        
        Returns:
            True if initialized, False otherwise
        """
        return self.retrieval_system is not None and self.vector_database is not None


# Global chat manager instance
_chat_manager = None


def get_chat_manager() -> ChatManager:
    """Get the global chat manager instance."""
    global _chat_manager
    if _chat_manager is None:
        _chat_manager = ChatManager()
    return _chat_manager


def send_message(message: str) -> str:
    """
    Send a message to the chatbot and get a response.
    
    Args:
        message: User message
        
    Returns:
        AI response
    """
    chat_manager = get_chat_manager()
    return chat_manager.send_message(message)


def reset_chat() -> bool:
    """
    Reset the chat session history.
    
    Returns:
        True if successful
    """
    chat_manager = get_chat_manager()
    return chat_manager.reset_chat()


def get_chat_history() -> List[Dict[str, str]]:
    """
    Get the current chat history.
    
    Returns:
        List of chat messages
    """
    chat_manager = get_chat_manager()
    return chat_manager.get_chat_history()


def get_chat_stats() -> Dict[str, Any]:
    """
    Get statistics about the current chat session.
    
    Returns:
        Dictionary containing chat statistics
    """
    chat_manager = get_chat_manager()
    return chat_manager.get_chat_stats()


def main():
    """Test the chat functions."""
    try:
        print("Testing chat functions...")
        
        # Test send_message
        response1 = send_message("What are tax deductions?")
        print(f"Response 1: {response1[:100]}...")
        
        # Test context preservation
        response2 = send_message("Can you tell me more about itemized deductions?")
        print(f"Response 2: {response2[:100]}...")
        
        # Get chat stats
        stats = get_chat_stats()
        print(f"Chat stats: {stats}")
        
        # Test reset
        reset_success = reset_chat()
        print(f"Reset successful: {reset_success}")
        
        # Check stats after reset
        stats_after_reset = get_chat_stats()
        print(f"Stats after reset: {stats_after_reset}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Make sure to set your OPENAI_API_KEY environment variable")


if __name__ == "__main__":
    main()
