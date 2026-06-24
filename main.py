#!/usr/bin/env python3
"""
CLI Entry Point for the RAG Document Q&A Prototype.
"""

import argparse
import sys
import logging
import json

from utils.config import setup_logging
from pipeline.qa_pipeline import DocumentQAPipeline

logger = logging.getLogger(__name__)

def print_result(result: dict) -> None:
    """Formats and prints the pipeline result to stdout."""
    print("\n" + "="*50)
    print("🤖 RAG DOCUMENT Q&A PROTOTYPE")
    print("="*50)
    
    print(f"\n📄 Document : {result['document']}")
    print(f"❓ Question : {result['query']}\n")
    
    print("-" * 50)
    print("💡 Answer:\n")
    print(result['answer'])
    print("-" * 50)
    
    print("\n📚 Citations Used:")
    if not result['citations']:
        print("  None. Answer was not grounded in document text.")
    else:
        for citation in result['citations']:
            print(f"\n  [{citation['id']}]:")
            # Truncate text for display if it's too long
            display_text = citation['text']
            if len(display_text) > 150:
                display_text = display_text[:147] + "..."
            print(f"  {display_text}")
            
    print("\n" + "="*50 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Run the RAG Document Q&A prototype.")
    parser.add_argument("--pdf", type=str, required=True, help="Path to the PDF document to ingest.")
    parser.add_argument("--query", type=str, required=True, help="The natural language question to ask.")
    parser.add_argument("--json", action="store_true", help="Output raw JSON instead of formatted text.")
    
    args = parser.parse_args()
    
    # Initialize logging based on config
    setup_logging()
    
    try:
        # Initialize and run pipeline
        pipeline = DocumentQAPipeline()
        
        logger.info("Initializing pipeline...")
        pipeline.ingest(args.pdf)
        
        logger.info("Evaluating query...")
        result = pipeline.answer(args.query)
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print_result(result)
            
    except Exception as e:
        logger.error(f"Fatal error during execution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
