"""
Utility functions and constants for OpenAI operations.
"""

from typing import Dict, List

class SystemPrompts:
    """Collection of system prompts used for different OpenAI interactions."""
    
    CONVERSATION_IDENTIFIER = """
    You are a helpful AI assistant in a Slack workspace.
    You will answer questions about the conversations in the Slack workspace.
    You will first understand which user is asking the question about and you will return ONLY the conversation id of the user that the question is about.
    You will return the conversation id in the format of '<conversation_id>'
    You will not return anything else.
    example prompt: 'Can you tell me about the conversation with <user_name>?'
    example response: Conversation ID: C98HD23QZRB
    """

    CONVERSATION_ANALYSIS = """
    You are a helpful AI assistant in a Slack workspace.
    You will answer questions about the conversations in the Slack workspace.
    You will use the conversation messages to answer the user's question.
    Ignore trying to find out which conversation the user is asking about, assume the user is asking about the conversation that you already can see.
    Format your response in bullet points for clarity.
    If you can't find relevant information in the conversation, politely say so.
    """

def prepare_messages(system_prompt: str, user_prompt: str, context: str = None) -> List[Dict[str, str]]:
    """
    Prepare messages for OpenAI chat completion.
    
    Args:
        system_prompt: The system instructions
        user_prompt: The user's question or message
        context: Optional context to add as a system message
        
    Returns:
        List[Dict[str, str]]: Formatted messages for the chat completion API
    """
    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    if context:
        messages.append({
            "role": "system",
            "content": context
        })

    messages.append({
        "role": "user",
        "content": user_prompt
    })

    return messages

def extract_conversation_id(response: str) -> str:
    """
    Extract conversation ID from OpenAI response.
    
    Args:
        response: The response from OpenAI
        
    Returns:
        str: The extracted conversation ID
    """
    if "conversation id: " in response.lower():
        return response.lower().split("conversation id: ")[1].strip()
    return response.strip() 