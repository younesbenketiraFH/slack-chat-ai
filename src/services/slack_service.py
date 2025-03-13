"""
Service layer for Slack operations.
"""

import ssl
from typing import List, Dict, Any
from fastapi import HTTPException

import certifi
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from src.models.slack_models import SlackEventWrapper, SlackUrlVerificationRequest
from src.repositories.slack_repository import SlackRepository
from src.services.openai_service import OpenAIService

class SlackService:
    def __init__(self, slack_repository: SlackRepository, openai_service: OpenAIService):
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        self.client = WebClient(ssl=ssl_context)
        self.slack_repository = slack_repository
        self.openai_service = openai_service

    async def fetch_messages(self, channel_id: str, limit: int = 20) -> str:
        """Fetch recent messages from a Slack channel."""
        try:
            response = self.client.conversations_history(channel=channel_id, limit=limit)
            messages = [msg["text"] for msg in response["messages"] if "text" in msg]
            return "\n".join(messages)
        except SlackApiError as e:
            print(f"Error fetching messages: {e.response['error']}")
            raise

    def send_message(self, channel_id: str, text: str, thread_ts: str = None) -> None:
        """Send a message to a Slack channel."""
        try:
            self.client.chat_postMessage(
                channel=channel_id,
                text=text,
                thread_ts=thread_ts
            )
        except SlackApiError as e:
            print(f"Error sending message: {e.response['error']}")
            raise

    async def handle_url_verification(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Handle Slack URL verification challenge."""
        verification_data = SlackUrlVerificationRequest(**data)
        return {"challenge": verification_data.challenge}

    async def handle_app_mention(self, event_data: SlackEventWrapper) -> None:
        """Handle app mention events from Slack."""
        channel_id = event_data.event.channel
        user_question = event_data.event.text.strip()
        
        try:
            # Fetch messages for context
            context = await self.slack_repository.fetch_messages(channel_id)
            
            # Generate response using OpenAI
            response_text = await self.openai_service.generate_response(
                prompt=user_question,
                context=context
            )
            
            # Send response back to Slack
            self.slack_repository.send_message(
                channel_id=channel_id,
                text=response_text,
                thread_ts=event_data.event.ts
            )
        except Exception as e:
            print(f"Error handling app mention: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def handle_event(self, event_type: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle different types of Slack events."""
        if event_type == "url_verification":
            return await self.handle_url_verification(event_data)
            
        if event_type == "event_callback":
            event_wrapper = SlackEventWrapper(**event_data)
            
            if event_wrapper.event.type == "app_mention":
                await self.handle_app_mention(event_wrapper)
            
            return {"status": "ok"}
            
        return {"status": "ok"} 