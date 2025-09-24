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


def write_progress(progress_file: str, data: dict):
    """Write progress data to file for polling."""
    if progress_file:
        try:
            import json
            with open(progress_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logger.warning(f"Failed to write progress: {e}")


def process_uploaded_files(file_paths: List[str], progress_file: str = None) -> bool:
    """
    Process uploaded PDF files and add them to the vector database.
    
    Args:
        file_paths: List of file paths to process
        progress_file: Optional file path to write progress updates
        
    Returns:
        True if successful, False otherwise
    """
    logger.info("Starting document upload process")
    logger.info(f"PDF files to process: {[os.path.basename(f) for f in file_paths]}")
    
    # Initialize progress
    total_files = len(file_paths)
    write_progress(progress_file, {
        'status': 'starting',
        'percentage': 0,
        'message': f'Starting upload of {total_files} files',
        'currentFile': '',
        'currentStage': 'initializing',
        'totalFiles': total_files,
        'processedFiles': 0
    })
    
    # Validate file paths
    existing_files = []
    missing_files = []
    
    for file_path in file_paths:
        if os.path.exists(file_path):
            existing_files.append(file_path)
            logger.info(f"Found PDF file: {os.path.basename(file_path)}")
        else:
            missing_files.append(file_path)
            logger.warning(f"PDF file not found: {file_path}")
    
    if not existing_files:
        logger.error("No PDF files found to process")
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
        
        # Process each PDF file completely (extract → split → embed → store)
        total_processed_chunks = 0
        
        for file_index, pdf_path in enumerate(existing_files):
            current_file = os.path.basename(pdf_path)
            logger.info(f"Processing PDF: {current_file}")
            
            # Update progress for file start
            file_progress = (file_index / total_files) * 100
            write_progress(progress_file, {
                'status': 'processing',
                'percentage': int(file_progress),
                'message': f'Processing file {file_index + 1} of {total_files}: {current_file}',
                'currentFile': current_file,
                'currentStage': 'extracting',
                'totalFiles': total_files,
                'processedFiles': file_index
            })
            
            try:
                # Step 1: Extract text from PDF
                logger.info("Extracting text from PDF...")
                extraction_result = pdf_extractor.extract_text_from_pdf(pdf_path)
                
                logger.info(f"Extracted {extraction_result['metadata']['total_characters']} characters")
                logger.info(f"Total pages: {extraction_result['metadata']['total_pages']}")
                
                # Step 2: Split text into chunks
                chunking_progress = int(file_progress + (10 / total_files))
                write_progress(progress_file, {
                    'status': 'processing',
                    'percentage': chunking_progress,
                    'message': f'Chunking text from {current_file}',
                    'currentFile': current_file,
                    'currentStage': 'chunking',
                    'totalFiles': total_files,
                    'processedFiles': file_index
                })
                
                logger.info("Splitting text into chunks...")
                chunks = text_splitter.split_text(
                    extraction_result['text'],
                    extraction_result['metadata']
                )
                
                logger.info(f"Created {len(chunks)} chunks for {current_file}")
                
                if not chunks:
                    logger.warning(f"No chunks created from {current_file}")
                    continue
                
                # Step 3: Generate embeddings for this PDF's chunks
                embedding_progress = int(file_progress + (20 / total_files))
                write_progress(progress_file, {
                    'status': 'processing',
                    'percentage': embedding_progress,
                    'message': f'Generating embeddings for {current_file}',
                    'currentFile': current_file,
                    'currentStage': 'embedding',
                    'totalFiles': total_files,
                    'processedFiles': file_index
                })
                
                logger.info(f"Generating embeddings for {len(chunks)} chunks from {current_file}")
                enhanced_chunks = embeddings_generator.generate_embeddings_with_metadata(
                    chunks,
                    batch_size=100
                )
                
                logger.info(f"Generated embeddings for {len(enhanced_chunks)} chunks from {current_file}")
                
                # Step 4: Store chunks in vector database
                storing_progress = int(file_progress + (30 / total_files))
                write_progress(progress_file, {
                    'status': 'processing',
                    'percentage': storing_progress,
                    'message': f'Storing {current_file} in database',
                    'currentFile': current_file,
                    'currentStage': 'storing',
                    'totalFiles': total_files,
                    'processedFiles': file_index
                })
                
                logger.info(f"Adding {len(enhanced_chunks)} chunks from {current_file} to vector database")
                success = vector_database.add_chunks(enhanced_chunks)
                
                if not success:
                    logger.error(f"Failed to add chunks from {current_file} to vector database")
                    continue
                
                total_processed_chunks += len(enhanced_chunks)
                logger.info(f"Successfully processed {current_file} - {len(enhanced_chunks)} chunks stored")
                
                # Update progress for file completion
                completion_progress = ((file_index + 1) / total_files) * 100
                write_progress(progress_file, {
                    'status': 'processing',
                    'percentage': int(completion_progress),
                    'message': f'{current_file} processed successfully',
                    'currentFile': current_file,
                    'currentStage': 'completed_file',
                    'totalFiles': total_files,
                    'processedFiles': file_index + 1
                })
                
            except Exception as e:
                logger.error(f"Error processing {pdf_path}: {str(e)}")
                continue
        
        if total_processed_chunks == 0:
            logger.error("No chunks processed from any PDF files")
            return False
        
        logger.info(f"Total chunks processed and stored: {total_processed_chunks}")
        
        # Update progress for completion
        write_progress(progress_file, {
            'status': 'completed',
            'percentage': 100,
            'message': f'All {total_files} files uploaded successfully!',
            'currentFile': '',
            'currentStage': 'completed',
            'totalFiles': total_files,
            'processedFiles': total_files
        })
        
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
    
    # Use the new process_uploaded_files function
    return process_uploaded_files(existing_files)


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
