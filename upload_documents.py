#!/usr/bin/env python3
"""
Document Upload Script for US Tax Chatbot

This script processes PDF files from the input directory and uploads them
to the vector database for semantic search functionality.

Usage:
    python upload_documents.py

The script will process all PDF files listed in the PDF_FILES array
and store them in the vector database.
"""

import logging
import os
import sys
from typing import List
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


def main():
    """Main function to process and upload PDF documents."""
    
    # List of PDF files to process (modify this array as needed)
    PDF_FILES = [
        "p561.pdf"
    ]
    
    logger.info("Starting document upload process")
    logger.info(f"PDF files to process: {PDF_FILES}")
    
    # Check if input directory exists
    input_dir = "input"
    if not os.path.exists(input_dir):
        logger.error(f"Input directory '{input_dir}' does not exist")
        logger.info("Please create the 'input' directory and place your PDF files there")
        return False
    
    # Check if PDF files exist
    existing_files = []
    missing_files = []
    
    for pdf_file in PDF_FILES:
        file_path = os.path.join(input_dir, pdf_file)
        if os.path.exists(file_path):
            existing_files.append(file_path)
            logger.info(f"Found PDF file: {pdf_file}")
        else:
            missing_files.append(pdf_file)
            logger.warning(f"PDF file not found: {pdf_file}")
    
    if not existing_files:
        logger.error("No PDF files found to process")
        logger.info("Please place PDF files in the 'input' directory")
        return False
    
    if missing_files:
        logger.warning(f"Missing files: {missing_files}")
        logger.info("Continuing with available files...")
    
    try:
        # Import required modules
        from pdf_extractor import PDFExtractor
        from text_splitter import TextSplitter
        from embeddings_generator import EmbeddingsGenerator
        from vector_database import VectorDatabase
        
        logger.info("Successfully imported all required modules")
        
        # Initialize components
        logger.info("Initializing PDF extractor...")
        pdf_extractor = PDFExtractor()
        
        logger.info("Initializing text splitter...")
        text_splitter = TextSplitter(chunk_size=300, chunk_overlap=50)
        
        logger.info("Initializing embeddings generator...")
        embeddings_generator = EmbeddingsGenerator()
        
        logger.info("Initializing vector database...")
        vector_database = VectorDatabase()
        
        # Process each PDF file
        all_chunks = []
        
        for pdf_path in existing_files:
            logger.info(f"Processing PDF: {os.path.basename(pdf_path)}")
            
            try:
                # Extract text from PDF
                logger.info("Extracting text from PDF...")
                extraction_result = pdf_extractor.extract_text_from_pdf(pdf_path)
                
                logger.info(f"Extracted {extraction_result['metadata']['total_characters']} characters")
                logger.info(f"Total pages: {extraction_result['metadata']['total_pages']}")
                
                # Split text into chunks
                logger.info("Splitting text into chunks...")
                chunks = text_splitter.split_text(
                    extraction_result['text'],
                    extraction_result['metadata']
                )
                
                logger.info(f"Created {len(chunks)} chunks")
                
                # Add chunks to the list
                all_chunks.extend(chunks)
                
                logger.info(f"Successfully processed {os.path.basename(pdf_path)}")
                
            except Exception as e:
                logger.error(f"Error processing {pdf_path}: {str(e)}")
                continue
        
        if not all_chunks:
            logger.error("No chunks created from any PDF files")
            return False
        
        logger.info(f"Total chunks created: {len(all_chunks)}")
        
        # Generate embeddings for all chunks
        logger.info("Generating embeddings for all chunks...")
        enhanced_chunks = embeddings_generator.generate_embeddings_with_metadata(
            all_chunks,
            batch_size=50
        )
        
        logger.info(f"Generated embeddings for {len(enhanced_chunks)} chunks")
        
        # Validate embeddings
        embeddings = [chunk.get('embedding', []) for chunk in enhanced_chunks]
        is_valid = embeddings_generator.validate_embeddings(embeddings)
        
        if not is_valid:
            logger.error("Embedding validation failed")
            return False
        
        logger.info("Embeddings validation passed")
        
        # Add chunks to vector database
        logger.info("Adding chunks to vector database...")
        success = vector_database.add_chunks(enhanced_chunks)
        
        if not success:
            logger.error("Failed to add chunks to vector database")
            return False
        
        logger.info("Successfully added all chunks to vector database")
        
        # Get database statistics
        db_info = vector_database.get_collection_info()
        logger.info(f"Database info: {db_info}")
        
        # Get document sources
        sources = vector_database.get_document_sources()
        logger.info(f"Document sources in database: {sources}")
        
        logger.info("Document upload process completed successfully!")
        return True
        
    except ImportError as e:
        logger.error(f"Import error: {str(e)}")
        logger.info("Make sure all required modules are installed: pip install -r requirements.txt")
        return False
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return False


def check_environment():
    """Check if the environment is properly configured."""
    logger.info("Checking environment configuration...")
    
    # Check OpenAI API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        logger.error("OPENAI_API_KEY environment variable is not set")
        logger.info("Please set your OpenAI API key in the .env file")
        return False
    
    logger.info("Environment configuration looks good")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("US Tax Chatbot - Document Upload Script")
    print("=" * 60)
    
    # Check environment
    if not check_environment():
        print("\nEnvironment check failed. Please fix the issues above.")
        sys.exit(1)
    
    # Run main process
    success = main()
    
    if success:
        print("\n✅ Document upload completed successfully!")
        print("You can now start chatting with the bot using the chat script.")
    else:
        print("\n❌ Document upload failed. Please check the logs above.")
        sys.exit(1)
