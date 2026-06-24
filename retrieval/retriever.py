"""
Document retrieval module.
Provides abstract interfaces and a concrete non-vector implementation for prototype ranking.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple
import logging
import numpy as np

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:
    logging.warning("scikit-learn is not installed. Please install it to use TFIDFRetriever.")

from ingestion.chunker import DocumentChunk

logger = logging.getLogger(__name__)

class DocumentRetriever(ABC):
    """Abstract base class for document retrievers."""
    
    @abstractmethod
    def index(self, chunks: List[DocumentChunk]) -> None:
        """
        Indexes the provided chunks for future retrieval.
        
        Args:
            chunks: A list of DocumentChunk objects to index.
        """
        pass

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 3) -> List[DocumentChunk]:
        """
        Retrieves the top_k most relevant chunks for the given query.
        
        Args:
            query: The user's search query.
            top_k: The maximum number of chunks to return.
            
        Returns:
            A list of the most relevant DocumentChunk objects.
        """
        pass


class TFIDFRetriever(DocumentRetriever):
    """
    A concrete implementation of DocumentRetriever using TF-IDF and Cosine Similarity.
    This serves as a robust baseline for content-based retrieval before upgrading
    to dense vector embeddings.
    
    [FUTURE VECTOR RETRIEVAL INTEGRATION POINT]
    To upgrade to vector-based semantic search, create a new class (e.g., VectorRetriever)
    that implements DocumentRetriever. It should encode chunks into embeddings during `index()` 
    (storing them in a vector DB like Chroma or Pinecone) and encode the query during `retrieve()` 
    to perform an Approximate Nearest Neighbor (ANN) search.
    """
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english', lowercase=True)
        self.chunks: List[DocumentChunk] = []
        self.tfidf_matrix = None
        self.is_indexed = False

    def index(self, chunks: List[DocumentChunk]) -> None:
        """
        Fits the TF-IDF vectorizer on the provided chunks and transforms them.
        """
        if not chunks:
            logger.warning("Attempted to index an empty list of chunks.")
            return
            
        logger.info(f"Indexing {len(chunks)} chunks using TF-IDF...")
        self.chunks = chunks
        
        # Extract plain text for vectorization
        corpus = [chunk.text for chunk in self.chunks]
        
        # Fit and transform
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
        self.is_indexed = True
        logger.info("Indexing complete.")

    def retrieve(self, query: str, top_k: int = 3) -> List[DocumentChunk]:
        """
        Transforms the query and computes cosine similarity against the indexed chunks.
        Returns the top_k scoring chunks.
        """
        if not self.is_indexed or self.tfidf_matrix is None:
            logger.error("Cannot retrieve before indexing.")
            raise ValueError("Retriever has not been indexed with any documents.")
            
        logger.debug(f"Retrieving top {top_k} chunks for query: '{query}'")
        
        query_vector = self.vectorizer.transform([query])
        
        # Compute similarities between the query and all indexed chunks
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        
        # Get the indices of the top_k highest scoring chunks
        # argsort sorts ascending, so we take the last top_k and reverse
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            # Only return chunks with a non-zero similarity score
            if score > 0.0:
                chunk = self.chunks[idx]
                logger.debug(f"Retrieved chunk '{chunk.id}' with score: {score:.4f}")
                results.append(chunk)
                
        if not results:
            logger.info("No relevant chunks found for the query.")
            
        return results
