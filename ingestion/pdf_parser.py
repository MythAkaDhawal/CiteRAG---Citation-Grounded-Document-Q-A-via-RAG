"""
PDF processing and text extraction module.
"""

import logging
from pathlib import Path
from pypdf import PdfReader
from utils.text_utils import clean_text

logger = logging.getLogger(__name__)

class PDFParser:
    """Handles the extraction of raw text from PDF documents."""
    
    def __init__(self):
        pass

    def parse(self, file_path: str | Path) -> str:
        """
        Reads a PDF file and extracts its text content.
        
        Args:
            file_path: The path to the PDF file.
            
        Returns:
            The complete, cleaned text extracted from the document.
            
        Raises:
            FileNotFoundError: If the PDF does not exist.
            ValueError: If the file is not a valid PDF or is unreadable.
        """
        path = Path(file_path)
        if not path.exists():
            logger.error(f"File not found: {path}")
            raise FileNotFoundError(f"PDF file not found at {path}")
            
        logger.info(f"Parsing PDF: {path.name}")
        
        try:
            reader = PdfReader(path)
            extracted_text = []
            
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    extracted_text.append(clean_text(text))
                else:
                    logger.debug(f"No text found on page {page_num + 1}")
                    
            full_text = "\n\n".join(extracted_text)
            
            if not full_text.strip():
                logger.warning(f"No text could be extracted from {path.name}.")
                
            return full_text
            
        except Exception as e:
            logger.error(f"Failed to parse PDF {path}: {e}")
            raise ValueError(f"Error reading PDF file: {e}") from e
