"""
Text processing utilities for cleaning and standardizing text from PDFs.
"""

import re

def clean_text(text: str) -> str:
    """
    Cleans raw text extracted from a PDF.
    
    Args:
        text: The raw text string.
        
    Returns:
        A cleaned, standardized string.
    """
    if not text:
        return ""
        
    # Replace multiple spaces with a single space
    text = re.sub(r" +", " ", text)
    
    # Replace multiple newlines with a single newline or space depending on context
    # This is a naive approach; more sophisticated PDF parsing might retain paragraphs better.
    text = re.sub(r"\n{3,}", "\n\n", text)
    
    # Optional: remove soft hyphens
    text = text.replace("\xad", "")
    text = text.replace("\u00ad", "")
    
    return text.strip()
