"""
Utility functions and constants for OpenAI operations.
"""

from typing import Dict, List

class SystemPrompts:
    """Collection of system prompts used for different OpenAI interactions."""

    CONVERSATION_ANALYSIS = """
    You are a helpful AI assistant in a Slack workspace.
    You will answer questions about the conversations in the Slack workspace.
    You will use the conversation messages to answer the user's question.
    Ignore trying to find out which conversation the user is asking about, assume the user is asking about the conversation that you already can see.
    Format your response in bullet points for clarity.
    If you can't find relevant information in the conversation, politely say so.
    """

def prepare_messages(messages: str) -> List[Dict[str, str]]:
    return [
        {
            "role": "system",
            "content": SystemPrompts.CONVERSATION_ANALYSIS
        },
        {
            "role": "user",
            "content": messages
        }
    ]