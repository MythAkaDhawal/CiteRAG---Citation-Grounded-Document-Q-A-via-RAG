"""
Prompt engineering module for RAG context framing.
"""

from typing import List
from ingestion.chunker import DocumentChunk

class PromptBuilder:
    """
    Constructs highly constrained prompts that force the LLM to ground its
    answers exclusively in the provided document chunks.
    """
    
    SYSTEM_INSTRUCTION = (
        "You are an expert Research Assistant. Your task is to answer the user's "
        "question based STRICTLY and ONLY on the provided document context.\n\n"
        "CRITICAL INSTRUCTIONS:\n"
        "1. DO NOT rely on your pre-trained knowledge. If the answer is not contained "
        "within the provided context, you must state: 'I cannot answer this based on the provided document.'\n"
        "2. You MUST cite your sources. After every factual claim, append the citation using the "
        "exact chunk ID provided (e.g., [chunk_4]).\n"
        "3. Do not invent, hallucinate, or extrapolate information.\n"
        "4. Be concise and direct."
    )
    
    def build_prompt(self, query: str, retrieved_chunks: List[DocumentChunk]) -> str:
        """
        Assembles the final prompt string from the query and retrieved chunks.
        
        Args:
            query: The user's question.
            retrieved_chunks: The chunks retrieved from the document.
            
        Returns:
            A formatted prompt string ready for the Gemini API.
        """
        if not retrieved_chunks:
            return (
                f"{self.SYSTEM_INSTRUCTION}\n\n"
                "CONTEXT:\n"
                "No relevant document context was found for this query.\n\n"
                f"QUESTION: {query}\n\n"
                "ANSWER:"
            )
            
        # Format the context blocks clearly
        context_blocks = []
        for chunk in retrieved_chunks:
            # We enforce the [chunk_x] ID format for traceability
            context_blocks.append(f"--- START [{chunk.id}] ---\n{chunk.text}\n--- END [{chunk.id}] ---")
            
        context_str = "\n\n".join(context_blocks)
        
        # Assemble the final prompt
        prompt = (
            f"{self.SYSTEM_INSTRUCTION}\n\n"
            "CONTEXT:\n"
            f"{context_str}\n\n"
            f"QUESTION: {query}\n\n"
            "ANSWER:"
        )
        
        return prompt
