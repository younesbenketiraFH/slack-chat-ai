"""
Service layer for OpenAI operations.
"""

import json
from src.repositories.openai_repository import OpenAIRepository
from src.utilities.openai_utilities import SystemPrompts, prepare_messages

class OpenAIService:
    def __init__(self):
        self.repository = OpenAIRepository()
        self.max_tokens = 1000
        self.temperature = 0

    async def analyze_conversation(self, conversation_messages: str) -> str:
        messages = prepare_messages(conversation_messages)

        print(json.dumps(messages, indent=4))
        response = await self.repository.create_chat_completion(
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )

        if not response.choices[0].message.content:
            raise Exception("No response from OpenAI")

        return response.choices[0].message.content.strip()