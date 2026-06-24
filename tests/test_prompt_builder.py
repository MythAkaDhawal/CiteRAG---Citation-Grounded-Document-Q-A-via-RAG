import pytest
from generation.prompt_builder import PromptBuilder
from ingestion.chunker import DocumentChunk

def test_prompt_construction():
    """Test that the prompt builder correctly formats context and constraints."""
    builder = PromptBuilder()
    
    chunks = [
        DocumentChunk("chunk_0", "The sky is blue.", {}),
        DocumentChunk("chunk_1", "Grass is green.", {})
    ]
    query = "What color is the sky?"
    
    prompt = builder.build_prompt(query, chunks)
    
    # Check that system instructions are present
    assert "STRICTLY and ONLY" in prompt
    assert "cite your sources" in prompt
    
    # Check that context blocks are correctly formatted
    assert "--- START [chunk_0] ---" in prompt
    assert "The sky is blue." in prompt
    assert "--- START [chunk_1] ---" in prompt
    
    # Check that the query is present
    assert f"QUESTION: {query}" in prompt

def test_empty_context_prompt():
    """Test prompt construction when no chunks are retrieved."""
    builder = PromptBuilder()
    query = "What color is the sky?"
    
    prompt = builder.build_prompt(query, [])
    
    assert "No relevant document context was found" in prompt
    assert f"QUESTION: {query}" in prompt
