"""
Service layer for OpenAI operations.
"""

import os
from typing import Optional, List, Dict

from openai import OpenAI

class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"  # Using the latest free model
        self.max_tokens = 1000
        self.temperature = 0.7

    async def generate_response(self, system_prompt: str, prompt: str, context: Optional[str] = None) -> str:
        """
        Generate a response using OpenAI's chat completion.
        
        Args:
            prompt: The user's question or message
            context: Optional previous conversation context
        
        Returns:
            str: The generated response
        """
        # Prepare the messages array
        messages: List[Dict[str, str]] = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]

        # Add context if provided
        if context:
            messages.append({
                "role": "system",
                "content": f"Previous conversation context:\n{context}"
            })

        # Add the user's prompt
        messages.append({
            "role": "user",
            "content": prompt
        })

        try:
            # Make the API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                n=1,
                stream=False
            )

            # Extract and return the response text
            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"Error generating OpenAI response: {str(e)}")
            return "I apologize, but I encountered an error processing your request. Please try again." 