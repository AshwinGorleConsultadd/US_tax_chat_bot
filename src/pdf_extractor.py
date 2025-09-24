"""
PDF Text Extraction Module for US Tax Chatbot

This module handles PDF text extraction with metadata preservation.
Supports multiple PDF libraries for robust text extraction.
"""

import logging
import os
from typing import List, Dict, Any, Optional
import PyPDF2
import pdfplumber
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFExtractor:
    """Handles PDF text extraction with metadata preservation."""
    
    def __init__(self):
        self.supported_extensions = ['.pdf']
        logger.info("PDFExtractor initialized")
    
    def extract_text_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract text from PDF with metadata.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing text, metadata, and extraction info
        """
        logger.info(f"Starting text extraction from: {pdf_path}")
        
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        if not pdf_path.lower().endswith('.pdf'):
            raise ValueError(f"File is not a PDF: {pdf_path}")
        
        # Try different extraction methods for robustness
        extraction_methods = [
            self._extract_with_pdfplumber,
            self._extract_with_pypdf2
        ]
        
        for method in extraction_methods:
            try:
                result = method(pdf_path)
                if result and result.get('text', '').strip():
                    logger.info(f"Successfully extracted text using {method.__name__}")
                    return result
            except Exception as e:
                logger.warning(f"Extraction method {method.__name__} failed: {str(e)}")
                continue
        
        raise Exception(f"All extraction methods failed for {pdf_path}")
    
    def _extract_with_pdfplumber(self, pdf_path: str) -> Dict[str, Any]:
        """Extract text using pdfplumber library."""
        logger.info("Attempting extraction with pdfplumber")
        
        text_content = []
        page_metadata = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        # Clean up the text
                        cleaned_text = self._clean_text(page_text)
                        text_content.append(cleaned_text)
                        page_metadata.append({
                            'page_number': page_num,
                            'char_count': len(cleaned_text),
                            'word_count': len(cleaned_text.split())
                        })
                except Exception as e:
                    logger.warning(f"Error extracting page {page_num}: {str(e)}")
                    continue
        
        full_text = '\n\n'.join(text_content)
        
        return {
            'text': full_text,
            'metadata': {
                'source_file': os.path.basename(pdf_path),
                'file_path': pdf_path,
                'total_pages': len(page_metadata),
                'page_metadata': page_metadata,
                'extraction_method': 'pdfplumber',
                'extraction_timestamp': datetime.now().isoformat(),
                'total_characters': len(full_text),
                'total_words': len(full_text.split())
            }
        }
    
    def _extract_with_pypdf2(self, pdf_path: str) -> Dict[str, Any]:
        """Extract text using PyPDF2 library."""
        logger.info("Attempting extraction with PyPDF2")
        
        text_content = []
        page_metadata = []
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            for page_num, page in enumerate(pdf_reader.pages, 1):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        cleaned_text = self._clean_text(page_text)
                        text_content.append(cleaned_text)
                        page_metadata.append({
                            'page_number': page_num,
                            'char_count': len(cleaned_text),
                            'word_count': len(cleaned_text.split())
                        })
                except Exception as e:
                    logger.warning(f"Error extracting page {page_num}: {str(e)}")
                    continue
        
        full_text = '\n\n'.join(text_content)
        
        return {
            'text': full_text,
            'metadata': {
                'source_file': os.path.basename(pdf_path),
                'file_path': pdf_path,
                'total_pages': len(page_metadata),
                'page_metadata': page_metadata,
                'extraction_method': 'pypdf2',
                'extraction_timestamp': datetime.now().isoformat(),
                'total_characters': len(full_text),
                'total_words': len(full_text.split())
            }
        }
    
    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text by removing unwanted elements.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Remove common PDF artifacts
        text = text.replace('\x00', '')  # Remove null characters
        text = text.replace('\ufeff', '')  # Remove BOM
        
        # Remove page numbers that appear alone on lines
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip lines that are just numbers (likely page numbers)
            if line.isdigit() and len(line) <= 3:
                continue
            # Skip very short lines that are likely headers/footers
            if len(line) < 3:
                continue
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def extract_multiple_pdfs(self, pdf_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Extract text from multiple PDF files.
        
        Args:
            pdf_paths: List of PDF file paths
            
        Returns:
            List of extraction results
        """
        logger.info(f"Starting extraction of {len(pdf_paths)} PDF files")
        
        results = []
        for pdf_path in pdf_paths:
            try:
                result = self.extract_text_from_pdf(pdf_path)
                results.append(result)
                logger.info(f"Successfully processed: {pdf_path}")
            except Exception as e:
                logger.error(f"Failed to process {pdf_path}: {str(e)}")
                continue
        
        logger.info(f"Completed extraction of {len(results)} out of {len(pdf_paths)} files")
        return results


def main():
    """Test the PDF extraction functionality."""
    extractor = PDFExtractor()
    
    # Test with a sample PDF if available
    test_pdf = "input/test.pdf"
    if os.path.exists(test_pdf):
        try:
            result = extractor.extract_text_from_pdf(test_pdf)
            print(f"Extracted {len(result['text'])} characters from {result['metadata']['source_file']}")
            print(f"Total pages: {result['metadata']['total_pages']}")
        except Exception as e:
            print(f"Error: {str(e)}")
    else:
        print("No test PDF found. Place a PDF file in the 'input' directory to test.")


if __name__ == "__main__":
    main()
