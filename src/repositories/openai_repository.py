"""
Repository layer for OpenAI operations.
"""

import os
from typing import List
from fastapi import HTTPException
from openai import AzureOpenAI, APIError, RateLimitError, APIConnectionError
from openai.types.chat import ChatCompletionMessageParam
from typing import List, Union
from openai.types.chat import ChatCompletion
from openai._streaming import Stream
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk

class OpenAIRepository:
    def __init__(self):
        try:
            # Initialize Azure OpenAI client
            self.client = AzureOpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                api_version="2024-02-15-preview",
                azure_endpoint=os.getenv("OPENAI_API_DOMAIN") or ""
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
        messages: List[ChatCompletionMessageParam],
        max_tokens: int = 1000,
        temperature: float = 0.7,
        n: int = 1,
        stream: bool = False
    ) -> Union[ChatCompletion, Stream[ChatCompletionChunk]]:
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