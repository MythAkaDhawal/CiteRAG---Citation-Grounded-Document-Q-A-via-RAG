"""
Document segmentation module for splitting text into retrievable chunks.
"""

import logging
from dataclasses import dataclass
from typing import List

from utils.config import config

logger = logging.getLogger(__name__)

@dataclass
class DocumentChunk:
    """Represents a discrete segment of document text with associated metadata."""
    id: str
    text: str
    metadata: dict

class TextChunker:
    """
    Splits text into overlapping chunks. 
    A sliding window character-based approach is used for this prototype.
    """
    
    def __init__(self, chunk_size: int = config.CHUNK_SIZE, overlap: int = config.CHUNK_OVERLAP):
        """
        Args:
            chunk_size: Target maximum number of characters per chunk.
            overlap: Number of characters to overlap between chunks to preserve context.
        """
        if overlap >= chunk_size:
            raise ValueError("Overlap must be strictly less than chunk_size.")
            
        self.chunk_size = chunk_size
        self.overlap = overlap
        
    def chunk(self, text: str, source_metadata: dict | None = None) -> List[DocumentChunk]:
        """
        Segments the text into overlapping chunks.
        
        Args:
            text: The full text to split.
            source_metadata: Metadata to attach to each chunk (e.g., filename).
            
        Returns:
            A list of DocumentChunk objects.
        """
        if not text:
            return []
            
        logger.info(f"Chunking text (length: {len(text)}, chunk_size: {self.chunk_size}, overlap: {self.overlap})")
        
        chunks = []
        start = 0
        text_length = len(text)
        chunk_index = 0
        
        metadata = source_metadata or {}
        
        while start < text_length:
            end = start + self.chunk_size
            
            # If we are not at the very end of the text, try to snap to the nearest space
            # to avoid cutting words in half.
            if end < text_length:
                # Look backwards for a space within a reasonable window (e.g., 50 chars)
                last_space = text.rfind(' ', start, end)
                if last_space != -1 and (end - last_space) < 50:
                    end = last_space
                    
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunk_meta = metadata.copy()
                chunk_meta["chunk_index"] = chunk_index
                
                chunks.append(DocumentChunk(
                    id=f"chunk_{chunk_index}",
                    text=chunk_text,
                    metadata=chunk_meta
                ))
                chunk_index += 1
                
            # Move the start forward, accounting for overlap
            start = end - self.overlap
            
            # Prevent infinite loops if progress isn't being made
            if start <= start - self.overlap + 1:
               # Fallback to force strict advancement if space-snapping caused a stall
               start = end 
               
        logger.info(f"Generated {len(chunks)} chunks.")
        return chunks
