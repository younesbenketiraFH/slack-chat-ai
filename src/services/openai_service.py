"""
Service layer for OpenAI operations.
"""

from typing import Optional, List, Dict
from src.repositories.openai_repository import OpenAIRepository
from src.utilities.openai_utilities import SystemPrompts, prepare_messages, extract_conversation_id

class OpenAIService:
    # System prompts for different purposes
    CONVERSATION_IDENTIFIER_PROMPT = """
    You are a helpful AI assistant in a Slack workspace.
    You will answer questions about the conversations in the Slack workspace.
    You will first understand which user is asking the question about and you will return ONLY the conversation id of the user that the question is about.
    You will return the conversation id in the format of '<conversation_id>'
    You will not return anything else.
    example prompt: 'Can you tell me about the conversation with <user_name>?'
    example response: Conversation ID: C98HD23QZRB
    """

    CONVERSATION_ANALYSIS_PROMPT = """
    You are a helpful AI assistant in a Slack workspace.
    You will answer questions about the conversations in the Slack workspace.
    You will use the conversation messages to answer the user's question.
    Ignore trying to find out which conversation the user is asking about, assume the user is asking about the conversation that you already can see.
    Format your response in bullet points for clarity.
    If you can't find relevant information in the conversation, politely say so.
    """

    def __init__(self):
        self.repository = OpenAIRepository()
        self.max_tokens = 1000
        self.temperature = 0.7

    async def _generate_response(self, system_prompt: str, prompt: str, context: str = '') -> str:
        """
        Base method to generate a response using Azure OpenAI's chat completion.
        
        Args:
            system_prompt: The system instructions
            prompt: The user's question or message
            context: Optional previous conversation context
        
        Returns:
            str: The generated response
        """
        messages = prepare_messages(system_prompt, prompt, context)
        response = await self.repository.create_chat_completion(
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )

        print(f"Response: {response}")
        if not response.choices[0].message.content:
            raise ValueError("No response from OpenAI")

        print(f"Response Content: {response.choices[0].message.content}")
        return response.choices[0].message.content.strip()

    async def analyze_conversation(self, user_question: str, conversation_messages: str) -> str:
        """
        Analyze conversation messages and answer user's question.
        
        Args:
            user_question: The user's question
            conversation_messages: String of conversation messages to analyze
            
        Returns:
            str: The analysis response
        """
        return await self._generate_response(
            system_prompt=SystemPrompts.CONVERSATION_ANALYSIS,
            prompt=user_question,
            context=conversation_messages
        ) 