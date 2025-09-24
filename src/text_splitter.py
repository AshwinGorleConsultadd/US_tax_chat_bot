"""
Text Splitting Module for US Tax Chatbot

This module handles text chunking using RecursiveCharacterTextSplitter
with hierarchical splitting strategy for optimal semantic retrieval.
"""

import logging
import os
from typing import List, Dict, Any, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
import tiktoken

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextSplitter:
    """Handles text splitting into semantically meaningful chunks."""
    
    def __init__(self, chunk_size: int = 300, chunk_overlap: int = 50):
        """
        Initialize the text splitter.
        
        Args:
            chunk_size: Maximum number of tokens per chunk
            chunk_overlap: Number of tokens to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize the recursive character text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=[
                "\n\n",  # Split by paragraphs first
                "\n",    # Then by lines
                " ",     # Then by spaces
                "",      # Finally by characters
            ],
            is_separator_regex=False,
        )
        
        logger.info(f"TextSplitter initialized with chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")
    
    def split_text(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Split text into chunks with metadata preservation.
        
        Args:
            text: Text to split
            metadata: Metadata associated with the text
            
        Returns:
            List of text chunks with metadata
        """
        logger.info(f"Starting text splitting for document: {metadata.get('source_file', 'Unknown')}")
        
        if not text or not text.strip():
            logger.warning("Empty text provided for splitting")
            return []
        
        # Split the text into chunks
        chunks = self.text_splitter.split_text(text)
        logger.info(f"Created {len(chunks)} chunks from text")
        
        # Create chunk metadata with text content
        chunk_metadata_list = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = {
                'text': chunk,  # Include the actual text content
                'chunk_id': f"{metadata.get('source_file', 'unknown')}_chunk_{i}",
                'chunk_index': i,
                'source_file': metadata.get('source_file', 'unknown'),
                'file_path': metadata.get('file_path', ''),
                'total_chunks': len(chunks),
                'chunk_size': len(chunk),
                'chunk_word_count': len(chunk.split()),
                'extraction_method': metadata.get('extraction_method', 'unknown'),
                'extraction_timestamp': metadata.get('extraction_timestamp', ''),
                'total_pages': metadata.get('total_pages', 0),
                'total_characters': metadata.get('total_characters', 0),
                'total_words': metadata.get('total_words', 0)
            }
            
            # Add page information if available
            if 'page_metadata' in metadata:
                chunk_metadata['page_metadata'] = metadata['page_metadata']
            
            chunk_metadata_list.append(chunk_metadata)
        
        logger.info(f"Successfully created {len(chunk_metadata_list)} chunks with metadata")
        return chunk_metadata_list
    
    def split_multiple_texts(self, text_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Split multiple texts into chunks.
        
        Args:
            text_data: List of dictionaries containing 'text' and 'metadata' keys
            
        Returns:
            List of all chunks with metadata
        """
        logger.info(f"Starting splitting of {len(text_data)} documents")
        
        all_chunks = []
        for i, data in enumerate(text_data):
            try:
                chunks = self.split_text(data['text'], data['metadata'])
                all_chunks.extend(chunks)
                logger.info(f"Processed document {i+1}/{len(text_data)}: {data['metadata'].get('source_file', 'Unknown')}")
            except Exception as e:
                logger.error(f"Error splitting document {i+1}: {str(e)}")
                continue
        
        logger.info(f"Total chunks created: {len(all_chunks)}")
        return all_chunks
    
    def get_chunk_statistics(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get statistics about the created chunks.
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            Dictionary containing chunk statistics
        """
        if not chunks:
            return {}
        
        chunk_sizes = [chunk['chunk_size'] for chunk in chunks]
        word_counts = [chunk['chunk_word_count'] for chunk in chunks]
        
        stats = {
            'total_chunks': len(chunks),
            'avg_chunk_size': sum(chunk_sizes) / len(chunk_sizes),
            'min_chunk_size': min(chunk_sizes),
            'max_chunk_size': max(chunk_sizes),
            'avg_word_count': sum(word_counts) / len(word_counts),
            'min_word_count': min(word_counts),
            'max_word_count': max(word_counts),
            'unique_sources': len(set(chunk['source_file'] for chunk in chunks))
        }
        
        logger.info(f"Chunk statistics: {stats}")
        return stats
    
    def validate_chunks(self, chunks: List[Dict[str, Any]]) -> bool:
        """
        Validate that chunks meet quality criteria.
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            True if chunks are valid, False otherwise
        """
        logger.info("Validating chunks...")
        
        if not chunks:
            logger.warning("No chunks to validate")
            return False
        
        valid_chunks = 0
        for chunk in chunks:
            # Check if chunk has required fields
            required_fields = ['chunk_id', 'chunk_index', 'source_file']
            if not all(field in chunk for field in required_fields):
                logger.warning(f"Chunk missing required fields: {chunk.get('chunk_id', 'unknown')}")
                continue
            
            # Check chunk size is reasonable
            chunk_size = chunk.get('chunk_size', 0)
            if chunk_size < 10:  # Too small
                logger.warning(f"Chunk too small: {chunk['chunk_id']} ({chunk_size} chars)")
                continue
            
            if chunk_size > self.chunk_size * 2:  # Too large
                logger.warning(f"Chunk too large: {chunk['chunk_id']} ({chunk_size} chars)")
                continue
            
            valid_chunks += 1
        
        validation_passed = valid_chunks == len(chunks)
        logger.info(f"Validation {'passed' if validation_passed else 'failed'}: {valid_chunks}/{len(chunks)} chunks valid")
        
        return validation_passed


def main():
    """Test the text splitting functionality."""
    splitter = TextSplitter(chunk_size=300, chunk_overlap=50)
    
    # Test with sample text
    sample_text = """
    This is a sample tax document for testing purposes.
    
    Section 1: Introduction
    Tax regulations in the United States are complex and require careful attention to detail.
    This document provides guidance on various tax matters.
    
    Section 2: Deductions
    There are many types of deductions available to taxpayers.
    These include standard deductions, itemized deductions, and business deductions.
    
    Section 3: Credits
    Tax credits can significantly reduce your tax liability.
    Common credits include the Earned Income Tax Credit and Child Tax Credit.
    """
    
    sample_metadata = {
        'source_file': 'test_document.pdf',
        'file_path': '/path/to/test_document.pdf',
        'total_pages': 3,
        'extraction_method': 'test',
        'extraction_timestamp': '2024-01-01T00:00:00',
        'total_characters': len(sample_text),
        'total_words': len(sample_text.split())
    }
    
    try:
        chunks = splitter.split_text(sample_text, sample_metadata)
        print(f"Created {len(chunks)} chunks")
        
        stats = splitter.get_chunk_statistics(chunks)
        print(f"Statistics: {stats}")
        
        is_valid = splitter.validate_chunks(chunks)
        print(f"Validation passed: {is_valid}")
        
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
