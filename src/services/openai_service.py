"""
Service layer for OpenAI operations.
"""

import os
from typing import Optional, List, Dict

from openai import AzureOpenAI

class OpenAIService:
    def __init__(self):
        # Initialize Azure OpenAI client
        self.client = AzureOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            api_version="2024-02-15-preview",  # Use the latest API version
            azure_endpoint=os.getenv("OPENAI_API_DOMAIN")
        )
        
        # Use the deployment name from environment variable
        self.model = os.getenv("OPENAI_API_DEPLOYMENT", "gpt-4")
        self.max_tokens = 1000
        self.temperature = 0.7

    async def generate_response(self, system_prompt: str, prompt: str, context: Optional[str] = None) -> str:
        """
        Generate a response using Azure OpenAI's chat completion.
        
        Args:
            system_prompt: The system instructions
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
                "content": f"Channels and groups in the user's workspace:\n{context}"
            })

        # Add the user's prompt
        messages.append({
            "role": "user",
            "content": prompt
        })

        try:
            # Make the API call to Azure OpenAI
            response = self.client.chat.completions.create(
                model=self.model,  # This should be your deployment name
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                n=1,
                stream=False
            )

            # Extract and return the response text
            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"Error generating Azure OpenAI response: {str(e)}")
            return "I apologize, but I encountered an error processing your request. Please try again." 