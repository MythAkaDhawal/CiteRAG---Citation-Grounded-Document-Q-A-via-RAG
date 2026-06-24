"""
End-to-end orchestration pipeline for the RAG Document Q&A prototype.
"""

import logging
from pathlib import Path
from typing import Dict, Any

from ingestion.pdf_parser import PDFParser
from ingestion.chunker import TextChunker
from retrieval.retriever import TFIDFRetriever, DocumentRetriever
from generation.prompt_builder import PromptBuilder
from generation.gemini_client import GeminiClient

logger = logging.getLogger(__name__)

class DocumentQAPipeline:
    """
    Coordinates the document parsing, text chunking, retrieval, prompt construction, 
    and LLM generation steps into a single, cohesive workflow.
    """
    
    def __init__(self):
        """Initializes all pipeline components."""
        self.parser = PDFParser()
        self.chunker = TextChunker()
        # Note: TFIDFRetriever requires scikit-learn. For a production vector DB,
        # we would inject a VectorRetriever here instead.
        self.retriever: DocumentRetriever = TFIDFRetriever()
        self.prompt_builder = PromptBuilder()
        self.llm_client = GeminiClient()
        
        self.is_ready = False
        self.current_document_path = None

    def ingest(self, pdf_path: str | Path) -> None:
        """
        Processes a PDF document and indexes its contents for retrieval.
        
        Args:
            pdf_path: Path to the PDF file.
        """
        logger.info(f"--- Starting Ingestion Pipeline for: {pdf_path} ---")
        
        # 1. Parse PDF
        raw_text = self.parser.parse(pdf_path)
        
        # 2. Chunk Text
        metadata = {"source": str(pdf_path)}
        chunks = self.chunker.chunk(raw_text, source_metadata=metadata)
        
        # 3. Index Chunks
        self.retriever.index(chunks)
        
        self.is_ready = True
        self.current_document_path = str(pdf_path)
        logger.info("--- Ingestion Pipeline Complete ---")

    def answer(self, query: str) -> Dict[str, Any]:
        """
        Answers a user query based on the ingested document.
        
        Args:
            query: The user's question.
            
        Returns:
            A dictionary containing the answer and the retrieved context/citations.
        """
        if not self.is_ready:
            raise RuntimeError("Pipeline is not ready. Please ingest a document first.")
            
        logger.info(f"--- Starting Q&A Pipeline for query: '{query}' ---")
        
        # 1. Retrieve Context
        top_chunks = self.retriever.retrieve(query, top_k=3)
        
        # 2. Construct Prompt
        prompt = self.prompt_builder.build_prompt(query, top_chunks)
        
        # 3. Generate Answer
        answer_text = self.llm_client.generate_response(prompt)
        
        logger.info("--- Q&A Pipeline Complete ---")
        
        # Return structured result
        return {
            "query": query,
            "answer": answer_text,
            "document": self.current_document_path,
            "citations": [
                {"id": chunk.id, "text": chunk.text} for chunk in top_chunks
            ]
        }
