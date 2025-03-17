"""
Service layer for Slack operations.
"""

import ssl
import json
from typing import List, Dict, Any

import certifi
from slack_sdk import WebClient

from src.models.slack_models import SlackEventWrapper, SlackUrlVerificationRequest
from src.repositories.slack_repository import SlackRepository
from src.services.openai_service import OpenAIService

class SlackService:
    def __init__(self, slack_repository: SlackRepository, openai_service: OpenAIService):
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        self.client = WebClient(ssl=ssl_context)
        self.slack_repository = slack_repository
        self.openai_service = openai_service

    async def handle_url_verification(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Handle Slack URL verification challenge."""
        verification_data = SlackUrlVerificationRequest(**data)
        return {"challenge": verification_data.challenge}

    async def handle_direct_message(self, event_data: SlackEventWrapper) -> None:
        """Handle direct message events from Slack."""
        channel_id = event_data.event.channel

        if not channel_id:
            print("No channel ID found in event data")
            return
        
        if not event_data.event.ts:
            print("No thread timestamp found in event data")
            return
        
        if not event_data.event.text:
            print("No text found in event data")
            return

        user_question = event_data.event.text.strip()
        
        # Example question: "38972 can you give me a summary of what X said?"
        conversation_id = user_question.split(":")[0]

        # Get all conversations for context
        # all_conversations = await self.slack_repository.list_conversations()
        # conversations_json = json.dumps(all_conversations, indent=2)
        # # Identify which conversation the user is asking about
        # conversation_id = await self.openai_service.identify_conversation(
        #     user_question=user_question,
        #     conversations_context=conversations_json
        # )
        # print(f"Identified Conversation ID: {conversation_id}")

        # Get the messages from the identified conversation
        conversation_messages = await self.slack_repository.fetch_messages(conversation_id)
        print(f"Retrieved messages from conversation: {conversation_messages}")

        # Generate the final response
        # final_response = await self.openai_service.analyze_conversation(
        #     user_question=user_question.split(":")[1],
        #     conversation_messages=conversation_messages
        # )
        final_response = f"Here is the summary of the conversation:"
        print(f"Final Response: {final_response}")

        # Send the response back to the user
        await self.slack_repository.send_message(
            channel_id=channel_id,
            text=final_response,
            thread_ts=event_data.event.ts
        ) 