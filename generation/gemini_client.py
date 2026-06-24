"""
Gemini API integration module.
"""

import logging
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.api_core.exceptions import ResourceExhausted, InternalServerError, ServiceUnavailable

from utils.config import config

logger = logging.getLogger(__name__)

class GeminiClient:
    """
    Wrapper for the Google Gemini API with robust error handling and retries.
    """
    
    def __init__(self, api_key: str | None = None, model_name: str | None = None):
        """
        Initializes the Gemini client.
        
        Args:
            api_key: The API key. If None, falls back to config.
            model_name: The model to use. If None, falls back to config.
        """
        key = api_key or config.GEMINI_API_KEY
        if not key:
            raise ValueError("GEMINI_API_KEY is not set. Please provide it in the environment or .env file.")
            
        genai.configure(api_key=key)
        self.model_name = model_name or config.GEMINI_MODEL
        self.model = genai.GenerativeModel(self.model_name)
        logger.info(f"Initialized GeminiClient with model: {self.model_name}")

    # Retry on specific transient/rate-limit Google API exceptions
    @retry(
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ResourceExhausted, InternalServerError, ServiceUnavailable)),
        before_sleep=lambda retry_state: logger.warning(f"Retrying Gemini API call (attempt {retry_state.attempt_number})...")
    )
    def generate_response(self, prompt: str) -> str:
        """
        Sends a prompt to the Gemini API and returns the generated text.
        Includes exponential backoff retries for transient errors.
        
        Args:
            prompt: The full, formatted prompt string.
            
        Returns:
            The generated response string.
        """
        logger.debug("Sending prompt to Gemini API...")
        
        try:
            # Enforce deterministic/grounded behavior via temperature 0
            generation_config = GenerationConfig(
                temperature=0.0,
                top_p=0.8,
                top_k=40
            )
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Note: Depending on the API version, the safety ratings might block content.
            # In a production system, we should handle response.prompt_feedback properly.
            if response.text:
                return response.text.strip()
            else:
                logger.error("Gemini returned an empty response. Check safety settings or prompt structure.")
                return "Error: The model returned an empty response."
                
        except Exception as e:
            logger.error(f"Gemini API Error: {e}")
            raise
