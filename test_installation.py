#!/usr/bin/env python3
"""
Test Script for US Tax Chatbot

This script tests the basic functionality of the chatbot components
to ensure everything is properly installed and configured.

Usage:
    python test_installation.py
"""

import sys
import os
from dotenv import load_dotenv

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
load_dotenv()

def test_imports():
    """Test if all required modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        import langchain
        print("✅ langchain imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import langchain: {e}")
        return False
    
    try:
        import langchain_openai
        print("✅ langchain_openai imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import langchain_openai: {e}")
        return False
    
    try:
        import chromadb
        print("✅ chromadb imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import chromadb: {e}")
        return False
    
    try:
        import PyPDF2
        print("✅ PyPDF2 imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import PyPDF2: {e}")
        return False
    
    try:
        import pdfplumber
        print("✅ pdfplumber imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import pdfplumber: {e}")
        return False
    
    try:
        import fitz
        print("✅ PyMuPDF (fitz) imported successfully")
    except ImportError as e:
        print(f"⚠️  PyMuPDF not available (optional): {e}")
        # PyMuPDF is optional, so we don't return False here
    
    try:
        import openai
        print("✅ openai imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import openai: {e}")
        return False
    
    return True

def test_environment():
    """Test environment configuration."""
    print("\n🔍 Testing environment configuration...")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key and api_key != 'your_openai_api_key_here':
        print("✅ OPENAI_API_KEY is set")
        return True
    else:
        print("❌ OPENAI_API_KEY is not set or is placeholder")
        print("   Please set your OpenAI API key in the .env file")
        return False

def test_project_modules():
    """Test if project modules can be imported."""
    print("\n🔍 Testing project modules...")
    
    try:
        from pdf_extractor import PDFExtractor
        print("✅ pdf_extractor imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import pdf_extractor: {e}")
        return False
    
    try:
        from text_splitter import TextSplitter
        print("✅ text_splitter imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import text_splitter: {e}")
        return False
    
    try:
        from embeddings_generator import EmbeddingsGenerator
        print("✅ embeddings_generator imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import embeddings_generator: {e}")
        return False
    
    try:
        from vector_database import VectorDatabase
        print("✅ vector_database imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import vector_database: {e}")
        return False
    
    try:
        from retrieval_system import RetrievalSystem
        print("✅ retrieval_system imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import retrieval_system: {e}")
        return False
    
    try:
        from chat_functions import send_message, reset_chat
        print("✅ chat_functions imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import chat_functions: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic functionality of components."""
    print("\n🔍 Testing basic functionality...")
    
    try:
        # Test PDF extractor
        from pdf_extractor import PDFExtractor
        extractor = PDFExtractor()
        print("✅ PDFExtractor initialized successfully")
    except Exception as e:
        print(f"❌ PDFExtractor initialization failed: {e}")
        return False
    
    try:
        # Test text splitter
        from text_splitter import TextSplitter
        splitter = TextSplitter()
        print("✅ TextSplitter initialized successfully")
    except Exception as e:
        print(f"❌ TextSplitter initialization failed: {e}")
        return False
    
    try:
        # Test text splitting with sample text
        sample_text = "This is a sample tax document for testing purposes."
        sample_metadata = {'source_file': 'test.pdf', 'total_pages': 1}
        chunks = splitter.split_text(sample_text, sample_metadata)
        print(f"✅ Text splitting works: created {len(chunks)} chunks")
    except Exception as e:
        print(f"❌ Text splitting failed: {e}")
        return False
    
    return True

def main():
    """Main test function."""
    print("=" * 60)
    print("🧪 US Tax Chatbot - Installation Test")
    print("=" * 60)
    
    all_tests_passed = True
    
    # Test imports
    if not test_imports():
        all_tests_passed = False
    
    # Test environment
    if not test_environment():
        all_tests_passed = False
    
    # Test project modules
    if not test_project_modules():
        all_tests_passed = False
    
    # Test basic functionality
    if not test_basic_functionality():
        all_tests_passed = False
    
    print("\n" + "=" * 60)
    if all_tests_passed:
        print("🎉 All tests passed! The installation is working correctly.")
        print("\nNext steps:")
        print("1. Place PDF files in the 'input' directory")
        print("2. Run: python upload_documents.py")
        print("3. Run: python chat.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\nCommon solutions:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Set OPENAI_API_KEY in .env file")
        print("3. Check Python version compatibility")
    print("=" * 60)

if __name__ == "__main__":
    main()
