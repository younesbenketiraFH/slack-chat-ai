"""
Service layer for OpenAI operations.
"""

import os
import openai
from typing import Optional

class OpenAIService:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")

    async def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        """Generate a response using OpenAI."""
        # TODO: Implement OpenAI chat completion
        return "Hello! I received your message." 