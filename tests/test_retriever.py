import pytest
from retrieval.retriever import TFIDFRetriever
from ingestion.chunker import DocumentChunk

@pytest.fixture
def sample_chunks():
    return [
        DocumentChunk("chunk_0", "The capital of France is Paris and it is a beautiful city.", {}),
        DocumentChunk("chunk_1", "Quantum computing leverages the principles of quantum mechanics.", {}),
        DocumentChunk("chunk_2", "Machine learning models require large amounts of training data.", {})
    ]

def test_retrieval_ranking(sample_chunks):
    """Test that TF-IDF correctly ranks the most relevant chunk highest."""
    retriever = TFIDFRetriever()
    retriever.index(sample_chunks)
    
    # Query about France/Paris
    results = retriever.retrieve("What is the capital of France?")
    
    assert len(results) > 0
    # The most relevant chunk should be the first one
    assert results[0].id == "chunk_0"

def test_retrieval_empty_query(sample_chunks):
    """Test handling of irrelevant queries where no TF-IDF overlap occurs."""
    retriever = TFIDFRetriever()
    retriever.index(sample_chunks)
    
    # Query with no overlapping vocabulary (ignoring stopwords)
    results = retriever.retrieve("xylophone zebra yellow")
    
    # Should return empty list because similarity score is 0.0
    assert len(results) == 0

def test_unindexed_retriever():
    """Test that retrieving before indexing raises an error."""
    retriever = TFIDFRetriever()
    with pytest.raises(ValueError):
        retriever.retrieve("test query")
