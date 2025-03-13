"""
Service layer for Slack operations.
"""

import ssl
import json
from typing import List, Dict, Any, Set
from fastapi import HTTPException
from datetime import datetime, timedelta

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
        # Store processed event IDs with timestamps
        self.processed_events: Dict[str, datetime] = {}
        # Clean up interval (5 minutes)
        self.cleanup_interval = timedelta(minutes=5)

    def _clean_old_events(self) -> None:
        """Clean up old event IDs to prevent memory growth."""
        current_time = datetime.now()
        self.processed_events = {
            event_id: timestamp 
            for event_id, timestamp in self.processed_events.items()
            if current_time - timestamp < self.cleanup_interval
        }

    def _is_duplicate_event(self, event_id: str) -> bool:
        """Check if an event has already been processed."""
        if event_id in self.processed_events:
            print(f"Duplicate event: {event_id}")
            return True
        self.processed_events[event_id] = datetime.now()
        self._clean_old_events()  # Periodically clean up old events
        print(f"Processed event: {event_id}")
        return False

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
            all_conversations = await self.slack_repository.list_conversations()

            system_prompt = "You are a helpful AI assistant in a Slack workspace. "
            system_prompt += "You will answer questions about the conversations in the Slack workspace. "
            # Determine which conversation to use for context based on user question
            response_text = await self.openai_service.generate_response(
                system_prompt=system_prompt,
                prompt=user_question,
                context=all_conversations
            )

            print(f"Response Text: {response_text}")

            # Fetch messages for context
            # context = await self.slack_repository.fetch_messages(channel_id)
            
            # # Generate response using OpenAI
            # response_text = await self.openai_service.generate_response(
            #     prompt=user_question,
            #     context=context
            # )
            
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
            # Check for duplicate events
            event_id = event_data.get("event_id")
            if event_id and self._is_duplicate_event(event_id):
                return {"status": "ok", "message": "Duplicate event"}
            
            event_wrapper = SlackEventWrapper(**event_data)
            
            if event_wrapper.event.type == "app_mention":
                # Process the event asynchronously
                await self.handle_app_mention(event_wrapper)
            
            return {"status": "ok"}
            
        return {"status": "ok"} 