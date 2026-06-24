"""
Configuration management for the RAG Document Q&A prototype.
"""

import logging
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Config:
    """Application configuration variables."""
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Model configuration
    GEMINI_MODEL: str = "gemini-2.5-flash"  # Flash is excellent for standard RAG
    
    # Chunking configuration
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

def setup_logging() -> None:
    """Configure the root logger according to config settings."""
    numeric_level = getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO)
    
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Suppress verbose loggers from external libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)

# Expose a default instance or function
config = Config()
setup_logging()
