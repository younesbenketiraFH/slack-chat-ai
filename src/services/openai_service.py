"""
Service layer for OpenAI operations.
"""

from src.repositories.openai_repository import OpenAIRepository
from src.utilities.openai_utilities import prepare_messages
from typing import Dict, Any
class OpenAIService:
    def __init__(self, max_tokens=1024, temperature=0.1):
        """
        Initialize the conversation analyzer.
        
        Args:
            repository: OpenAI API repository/client
            max_tokens: Maximum tokens for response
            temperature: Temperature for response generation (lower = more deterministic)
        """
        self.repository = OpenAIRepository()
        self.max_tokens = max_tokens
        self.temperature = temperature
    
    async def analyze_conversation(self, conversation_messages: str) -> str:
        """
        Analyze a conversation and return a summary.
        
        Args:
            conversation_messages: String containing conversation messages
            
        Returns:
            A string containing the summary
        """
        try:
            messages = prepare_messages(conversation_messages)
            
            response = await self.repository.create_chat_completion(
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # Extract the response content
            if hasattr(response, 'choices') and len(response.choices) > 0:
                if hasattr(response.choices[0], 'message') and hasattr(response.choices[0].message, 'content'):
                    return response.choices[0].message.content
                else:
                    return self._extract_content_from_dict(response.choices[0])
            else:
                return "No summary could be generated."
                
        except Exception as e:
            error_message = f"Error generating summary: {str(e)}"
            return error_message
    
    def _extract_content_from_dict(self, choice_dict: Dict[str, Any]) -> str:
        """
        Extract content from response when it's in dictionary format.
        
        Args:
            choice_dict: Dictionary representation of a choice
            
        Returns:
            Content string or error message
        """
        try:
            if isinstance(choice_dict, dict):
                if 'message' in choice_dict and 'content' in choice_dict['message']:
                    return choice_dict['message']['content']
            return "Content could not be extracted from response format."
        except Exception as e:
            return f"Error extracting content: {str(e)}"