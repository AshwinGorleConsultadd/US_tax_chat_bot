#!/usr/bin/env python3
"""
Start Web Interface Script for US Tax Chatbot

This script starts the web server for the US Tax Chatbot interface.
It provides a simple way to launch the web-based chat interface.

Usage:
    python start_web_interface.py

The web interface will be available at http://localhost:5000
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_dependencies():
    """Check if required dependencies are installed."""
    print("Checking dependencies...")
    
    try:
        import flask
        import flask_cors
        print("✅ Flask dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing Flask dependencies: {e}")
        print("Please install Flask dependencies: pip install flask flask-cors")
        return False

def check_environment():
    """Check if environment is properly configured."""
    print("Checking environment...")
    
    # Check OpenAI API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable is not set")
        print("Please set your OpenAI API key in the .env file")
        return False
    
    print("✅ Environment configuration looks good")
    return True

def check_vector_database():
    """Check if vector database exists."""
    print("Checking vector database...")
    
    db_path = "./chroma_db"
    if not os.path.exists(db_path):
        print("⚠️  Vector database not found")
        print("The chatbot will still work but may not have access to your documents")
        print("Run 'python upload_documents.py' to add documents to the database")
    else:
        print("✅ Vector database found")
    
    return True

def main():
    """Main function to start the web interface."""
    print("=" * 60)
    print("US Tax Chatbot - Web Interface Startup")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        print("\nDependency check failed. Please install the required packages.")
        sys.exit(1)
    
    # Check environment
    if not check_environment():
        print("\nEnvironment check failed. Please fix the configuration.")
        sys.exit(1)
    
    # Check vector database
    check_vector_database()
    
    print("\nStarting web server...")
    print("The web interface will be available at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        # Start the web server
        subprocess.run([sys.executable, "web_server.py"], check=True)
    except KeyboardInterrupt:
        print("\n\nWeb server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"\nError starting web server: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
