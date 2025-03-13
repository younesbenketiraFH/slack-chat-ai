"""
Repository layer for Slack operations.
"""

import os
import ssl
from typing import List

import certifi
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

class SlackRepository:
    def __init__(self):
        token = os.getenv("SLACK_BOT_TOKEN")
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        self.client = WebClient(token=token, ssl=ssl_context)

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