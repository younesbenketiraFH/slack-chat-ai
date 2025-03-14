"""
Service layer for Slack operations.
"""

import ssl
import json
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
            all_conversations = await self.slack_repository.list_conversations()

            system_prompt = "You are a helpful AI assistant in a Slack workspace. "
            system_prompt += "You will answer questions about the conversations in the Slack workspace. "
            system_prompt += "You will first understand which user is asking the question about and you will return ONLY the conversation id of the user that the question is about. "
            system_prompt += "You will return the conversation id in the format of '<conversation_id>' "
            system_prompt += "You will not return anything else. "
            system_prompt += "example prompt: 'Can you tell me about the conversation with <user_name>?' "
            system_prompt += "example response: Conversation ID: C98HD23QZRB"

            # Determine which conversation to use for context based on user question
            response_text = await self.openai_service.generate_response(
                system_prompt=system_prompt,
                prompt=user_question,
                context=all_conversations
            )

            # Get the conversation id from the response text
            print(f"Response Text: {response_text}")
            if "conversation id: " in response_text.lower():
                conversation_id = response_text.lower().split("conversation id: ")[1].strip()
            else:
                conversation_id = response_text

            print(f"Conversation ID: {conversation_id}")

            # Get the conversation messages
            conversation_messages = await self.slack_repository.fetch_messages(conversation_id)

            print(f"Conversation Messages: {conversation_messages}")

            # Get the response from the OpenAI service
            system_prompt = "You are a helpful AI assistant in a Slack workspace. "
            system_prompt += "You will answer questions about the conversations in the Slack workspace. "
            system_prompt += "You will use the conversation messages to answer the user's question. "
            system_prompt += "Ignore trying to find out which conversation the user is asking about. assume the user is asking about the conversation that you already can see. "
            system_prompt += "the conversation messages are in the format of example: <@U08J2SADPH6> Summarize the all-ai-bot-testing channel if you may. "
            system_prompt += "You will respond in bullet points"
            response_text = await self.openai_service.generate_response(
                system_prompt=system_prompt,
                prompt=user_question,
                context=conversation_messages
            )

            print(f"Response Text: {response_text}")

            # Send response back to Slack
            self.slack_repository.send_message(
                channel_id=channel_id,
                text=response_text,
                thread_ts=event_data.event.ts
            )
        except Exception as e:
            print(f"Error handling app mention: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e)) 