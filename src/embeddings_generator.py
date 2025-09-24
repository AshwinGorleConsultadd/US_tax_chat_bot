"""
Embeddings Generation Module for US Tax Chatbot

This module handles OpenAI embeddings generation for text chunks
using the text-embedding-3-small model for optimal performance and cost.
"""

import logging
import os
from typing import List, Dict, Any, Optional
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingsGenerator:
    """Handles OpenAI embeddings generation for text chunks."""
    
    def __init__(self, model_name: str = "text-embedding-3-small", api_key: Optional[str] = None):
        """
        Initialize the embeddings generator.
        
        Args:
            model_name: OpenAI embedding model to use
            api_key: OpenAI API key (if not provided, will use environment variable)
        """
        self.model_name = model_name
        
        # Get API key from parameter or environment
        api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        # Initialize OpenAI embeddings
        self.embeddings = OpenAIEmbeddings(
            model=model_name,
            openai_api_key=api_key
        )
        
        logger.info(f"EmbeddingsGenerator initialized with model: {model_name}")
    
    def generate_embeddings(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            batch_size: Number of texts to process in each batch
            
        Returns:
            List of embedding vectors
        """
        logger.info(f"Starting embeddings generation for {len(texts)} texts")
        
        if not texts:
            logger.warning("No texts provided for embedding generation")
            return []
        
        all_embeddings = []
        
        # Process texts in batches to avoid rate limits
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(texts) + batch_size - 1) // batch_size
            
            logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} texts)")
            
            try:
                # Generate embeddings for the batch
                batch_embeddings = self.embeddings.embed_documents(batch)
                all_embeddings.extend(batch_embeddings)
                
                logger.info(f"Successfully generated embeddings for batch {batch_num}")
                
                # Add delay between batches to respect rate limits
                if i + batch_size < len(texts):
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"Error generating embeddings for batch {batch_num}: {str(e)}")
                # Add empty embeddings for failed batch
                all_embeddings.extend([[] for _ in batch])
                continue
        
        logger.info(f"Completed embeddings generation: {len(all_embeddings)} embeddings created")
        return all_embeddings
    
    def generate_single_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text string to embed
            
        Returns:
            Embedding vector
        """
        logger.info("Generating single embedding")
        
        try:
            embedding = self.embeddings.embed_query(text)
            logger.info("Successfully generated single embedding")
            return embedding
        except Exception as e:
            logger.error(f"Error generating single embedding: {str(e)}")
            raise
    
    def generate_embeddings_with_metadata(self, chunks: List[Dict[str, Any]], batch_size: int = 100) -> List[Dict[str, Any]]:
        """
        Generate embeddings for chunks while preserving metadata.
        
        Args:
            chunks: List of chunk dictionaries with 'text' and metadata
            batch_size: Number of chunks to process in each batch
            
        Returns:
            List of chunk dictionaries with embeddings added
        """
        logger.info(f"Starting embeddings generation for {len(chunks)} chunks")
        
        if not chunks:
            logger.warning("No chunks provided for embedding generation")
            return []
        
        # Extract texts from chunks
        texts = [chunk.get('text', '') for chunk in chunks]
        
        # Generate embeddings
        embeddings = self.generate_embeddings(texts, batch_size)
        
        # Add embeddings to chunks
        enhanced_chunks = []
        for i, chunk in enumerate(chunks):
            enhanced_chunk = chunk.copy()
            enhanced_chunk['embedding'] = embeddings[i] if i < len(embeddings) else []
            enhanced_chunks.append(enhanced_chunk)
        
        logger.info(f"Successfully enhanced {len(enhanced_chunks)} chunks with embeddings")
        return enhanced_chunks
    
    def validate_embeddings(self, embeddings: List[List[float]]) -> bool:
        """
        Validate that embeddings are properly generated.
        
        Args:
            embeddings: List of embedding vectors
            
        Returns:
            True if embeddings are valid, False otherwise
        """
        logger.info("Validating embeddings...")
        
        if not embeddings:
            logger.warning("No embeddings to validate")
            return False
        
        valid_embeddings = 0
        for i, embedding in enumerate(embeddings):
            # Check if embedding is a list
            if not isinstance(embedding, list):
                logger.warning(f"Embedding {i} is not a list")
                continue
            
            # Check if embedding has expected dimensions
            if len(embedding) == 0:
                logger.warning(f"Embedding {i} is empty")
                continue
            
            # Check if embedding contains numbers
            if not all(isinstance(x, (int, float)) for x in embedding):
                logger.warning(f"Embedding {i} contains non-numeric values")
                continue
            
            valid_embeddings += 1
        
        validation_passed = valid_embeddings == len(embeddings)
        logger.info(f"Validation {'passed' if validation_passed else 'failed'}: {valid_embeddings}/{len(embeddings)} embeddings valid")
        
        return validation_passed
    
    def get_embedding_statistics(self, embeddings: List[List[float]]) -> Dict[str, Any]:
        """
        Get statistics about the generated embeddings.
        
        Args:
            embeddings: List of embedding vectors
            
        Returns:
            Dictionary containing embedding statistics
        """
        if not embeddings:
            return {}
        
        dimensions = [len(emb) for emb in embeddings if emb]
        if not dimensions:
            return {}
        
        stats = {
            'total_embeddings': len(embeddings),
            'valid_embeddings': len([emb for emb in embeddings if emb]),
            'embedding_dimensions': dimensions[0] if dimensions else 0,
            'avg_dimension': sum(dimensions) / len(dimensions),
            'min_dimension': min(dimensions),
            'max_dimension': max(dimensions)
        }
        
        logger.info(f"Embedding statistics: {stats}")
        return stats


def main():
    """Test the embeddings generation functionality."""
    try:
        generator = EmbeddingsGenerator()
        
        # Test with sample texts
        sample_texts = [
            "Tax regulations in the United States are complex and require careful attention.",
            "There are many types of deductions available to taxpayers.",
            "Tax credits can significantly reduce your tax liability."
        ]
        
        print("Testing embeddings generation...")
        embeddings = generator.generate_embeddings(sample_texts)
        
        print(f"Generated {len(embeddings)} embeddings")
        
        stats = generator.get_embedding_statistics(embeddings)
        print(f"Statistics: {stats}")
        
        is_valid = generator.validate_embeddings(embeddings)
        print(f"Validation passed: {is_valid}")
        
        # Test single embedding
        single_embedding = generator.generate_single_embedding("Sample tax text")
        print(f"Single embedding dimension: {len(single_embedding)}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Make sure to set your OPENAI_API_KEY environment variable")


if __name__ == "__main__":
    main()
