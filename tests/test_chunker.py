import pytest
from ingestion.chunker import TextChunker

def test_chunker_initialization():
    """Test that chunker rejects invalid overlap configurations."""
    with pytest.raises(ValueError):
        TextChunker(chunk_size=100, overlap=100)
        
    with pytest.raises(ValueError):
        TextChunker(chunk_size=100, overlap=150)

def test_chunking_logic():
    """Test that text is chunked into appropriate sizes with overlap."""
    # Create text that is 50 chars long
    text = "A" * 50
    
    # We want chunks of 20 chars, with 5 char overlap
    # Chunk 1: 0-20
    # Chunk 2: 15-35
    # Chunk 3: 30-50
    chunker = TextChunker(chunk_size=20, overlap=5)
    chunks = chunker.chunk(text)
    
    assert len(chunks) == 3
    assert len(chunks[0].text) == 20
    assert len(chunks[1].text) == 20
    assert len(chunks[2].text) == 20
    
def test_empty_text():
    """Test chunker handles empty text gracefully."""
    chunker = TextChunker()
    chunks = chunker.chunk("")
    assert len(chunks) == 0

def test_metadata_injection():
    """Test that metadata is correctly attached and indexed."""
    chunker = TextChunker(chunk_size=10, overlap=2)
    text = "0123456789012345"
    meta = {"source": "test.pdf"}
    
    chunks = chunker.chunk(text, source_metadata=meta)
    
    assert len(chunks) > 0
    assert chunks[0].metadata["source"] == "test.pdf"
    assert "chunk_index" in chunks[0].metadata
    assert chunks[0].metadata["chunk_index"] == 0
    assert chunks[1].metadata["chunk_index"] == 1
