"""
Repository layer for OpenAI operations.
"""

import os
from typing import Optional, List, Dict, Any
from fastapi import HTTPException
from openai import AzureOpenAI, APIError, RateLimitError, APIConnectionError
from openai.types.chat import ChatCompletion

class OpenAIRepository:
    def __init__(self):
        try:
            # Initialize Azure OpenAI client
            self.client = AzureOpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                api_version="2024-02-15-preview",
                azure_endpoint=os.getenv("OPENAI_API_DOMAIN")
            )
            
            # Use the deployment name from environment variable
            self.model = os.getenv("OPENAI_API_DEPLOYMENT", "gpt-4")
        except Exception as e:
            print(f"Error initializing OpenAI client: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to initialize OpenAI client. Please check your configuration."
            )

    async def create_chat_completion(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7,
        n: int = 1,
        stream: bool = False
    ) -> ChatCompletion:
        """
        Make a base request to Azure OpenAI's chat completion API.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 2.0)
            n: Number of completions to generate
            stream: Whether to stream the response
            
        Returns:
            ChatCompletion: The raw response from OpenAI
            
        Raises:
            HTTPException: If the API call fails
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                n=n,
                stream=stream
            )
            return response
            
        except RateLimitError as e:
            print(f"Rate limit exceeded: {str(e)}")
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
            
        except APIConnectionError as e:
            print(f"Connection error: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail="Failed to connect to OpenAI API. Please try again later."
            )
            
        except APIError as e:
            print(f"OpenAI API error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="OpenAI API error occurred. Please try again."
            )
            
        except Exception as e:
            print(f"Unexpected error in OpenAI request: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred while processing your request."
            ) 