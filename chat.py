#!/usr/bin/env python3
"""
Terminal Chat Script for US Tax Chatbot

This script provides a terminal-based interface for chatting with the
US Tax Chatbot. It maintains conversation context and provides
helpful commands for interaction.

Usage:
    python chat.py

Commands:
    /help - Show available commands
    /reset - Reset chat history
    /stats - Show chat statistics
    /history - Show chat history
    /quit or /exit - Exit the chat
"""

import logging
import os
import sys
from typing import List, Dict, Any
from dotenv import load_dotenv

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ChatInterface:
    """Terminal-based chat interface for the US Tax Chatbot."""
    
    def __init__(self):
        """Initialize the chat interface."""
        self.running = True
        self.chat_manager = None
        
        # Commands dictionary
        self.commands = {
            '/help': self.show_help,
            '/reset': self.reset_chat,
            '/stats': self.show_stats,
            '/history': self.show_history,
            '/quit': self.quit_chat,
            '/exit': self.quit_chat,
            '/clear': self.clear_screen
        }
        
        logger.info("ChatInterface initialized")
    
    def initialize_chat_manager(self) -> bool:
        """Initialize the chat manager."""
        try:
            from chat_functions import get_chat_manager
            
            self.chat_manager = get_chat_manager()
            
            if not self.chat_manager.is_initialized():
                logger.info("Initializing chat components...")
                if not self.chat_manager.initialize_components():
                    return False
            
            logger.info("Chat manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing chat manager: {str(e)}")
            return False
    
    def show_welcome_message(self):
        """Display welcome message."""
        print("=" * 70)
        print("🤖 US Tax Chatbot - Terminal Interface")
        print("=" * 70)
        print("Welcome! I'm your AI assistant for US tax regulations.")
        print("I can help you with questions about tax deductions, credits, and more.")
        print()
        print("Commands:")
        print("  /help     - Show available commands")
        print("  /reset    - Reset chat history")
        print("  /stats    - Show chat statistics")
        print("  /history  - Show chat history")
        print("  /clear    - Clear screen")
        print("  /quit     - Exit the chat")
        print()
        print("Type your tax questions below, or use a command.")
        print("=" * 70)
    
    def show_help(self):
        """Show help information."""
        print("\n📚 Available Commands:")
        print("  /help     - Show this help message")
        print("  /reset    - Reset the chat history and start fresh")
        print("  /stats    - Show statistics about the current chat session")
        print("  /history  - Display the conversation history")
        print("  /clear    - Clear the terminal screen")
        print("  /quit     - Exit the chat application")
        print()
        print("💡 Tips:")
        print("  - Ask specific questions about tax topics")
        print("  - I maintain context throughout our conversation")
        print("  - Use /reset if you want to start a new topic")
        print("  - Be specific for better answers (e.g., 'What are itemized deductions?' vs 'Tell me about deductions')")
        print()
    
    def reset_chat(self):
        """Reset the chat history."""
        if self.chat_manager:
            success = self.chat_manager.reset_chat()
            if success:
                print("\n🔄 Chat history has been reset. Starting fresh!")
            else:
                print("\n❌ Failed to reset chat history.")
        else:
            print("\n❌ Chat manager not initialized.")
    
    def show_stats(self):
        """Show chat statistics."""
        if self.chat_manager:
            stats = self.chat_manager.get_chat_stats()
            print(f"\n📊 Chat Statistics:")
            print(f"  Total messages: {stats['total_messages']}")
            print(f"  User messages: {stats['user_messages']}")
            print(f"  Assistant messages: {stats['assistant_messages']}")
            print(f"  Conversation turns: {stats['conversation_turns']}")
        else:
            print("\n❌ Chat manager not initialized.")
    
    def show_history(self):
        """Show chat history."""
        if self.chat_manager:
            history = self.chat_manager.get_chat_history()
            if not history:
                print("\n📝 No chat history available.")
                return
            
            print(f"\n📝 Chat History ({len(history)} messages):")
            print("-" * 50)
            
            for i, message in enumerate(history, 1):
                role = message['role']
                content = message['content']
                
                if role == 'user':
                    print(f"👤 You: {content}")
                else:
                    print(f"🤖 Bot: {content}")
                
                if i < len(history):
                    print()
            
            print("-" * 50)
        else:
            print("\n❌ Chat manager not initialized.")
    
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('clear' if os.name == 'posix' else 'cls')
        self.show_welcome_message()
    
    def quit_chat(self):
        """Quit the chat application."""
        print("\n👋 Thank you for using the US Tax Chatbot!")
        print("Have a great day!")
        self.running = False
    
    def process_user_input(self, user_input: str) -> str:
        """Process user input and return response."""
        if not self.chat_manager:
            return "❌ Chat manager not initialized. Please restart the application."
        
        try:
            response = self.chat_manager.send_message(user_input)
            return response
        except Exception as e:
            logger.error(f"Error processing user input: {str(e)}")
            return f"❌ I encountered an error: {str(e)}"
    
    def run(self):
        """Run the chat interface."""
        # Show welcome message
        self.show_welcome_message()
        
        # Initialize chat manager
        print("🔄 Initializing chat system...")
        if not self.initialize_chat_manager():
            print("❌ Failed to initialize chat system.")
            print("Please check your configuration and try again.")
            return
        
        print("✅ Chat system initialized successfully!")
        print()
        
        # Main chat loop
        while self.running:
            try:
                # Get user input
                user_input = input("👤 You: ").strip()
                
                # Check if input is empty
                if not user_input:
                    continue
                
                # Check if it's a command
                if user_input.startswith('/'):
                    if user_input in self.commands:
                        self.commands[user_input]()
                    else:
                        print(f"\n❌ Unknown command: {user_input}")
                        print("Type /help for available commands.")
                    continue
                
                # Process regular message
                print("\n🤖 Bot: ", end="", flush=True)
                response = self.process_user_input(user_input)
                print(response)
                print()
                
            except KeyboardInterrupt:
                print("\n\n👋 Chat interrupted. Goodbye!")
                break
            except EOFError:
                print("\n\n👋 Chat ended. Goodbye!")
                break
            except Exception as e:
                logger.error(f"Unexpected error in chat loop: {str(e)}")
                print(f"\n❌ Unexpected error: {str(e)}")
                print("Please try again or restart the application.")


def check_environment():
    """Check if the environment is properly configured."""
    print("🔍 Checking environment configuration...")
    
    # Check OpenAI API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable is not set")
        print("Please set your OpenAI API key in the .env file")
        return False
    
    # Check if vector database exists
    chroma_dir = "chroma_db"
    if not os.path.exists(chroma_dir):
        print("⚠️  Vector database not found. Please run upload_documents.py first.")
        return False
    
    print("✅ Environment configuration looks good")
    return True


def main():
    """Main function."""
    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed. Please fix the issues above.")
        sys.exit(1)
    
    # Create and run chat interface
    chat_interface = ChatInterface()
    chat_interface.run()


if __name__ == "__main__":
    main()
