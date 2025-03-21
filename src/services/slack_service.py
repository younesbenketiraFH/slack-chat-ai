import ssl
import certifi
import os
from slack_sdk import WebClient

from aiohttp import ClientSession
from src.repositories.slack_repository import SlackRepository
from src.services.openai_service import OpenAIService

class SlackService:
    def __init__(self, slack_repository: SlackRepository, openai_service: OpenAIService):
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        self.client = WebClient(
            token=os.getenv("SLACK_BOT_TOKEN"),
            ssl=ssl_context
        )
        self.slack_repository = slack_repository
        self.openai_service = openai_service
        
    async def get_bot_user_channel_id(self, user_id: str) -> str:
        """Create a group DM with the user and the bot."""
        try:
            result = self.client.conversations_open(users=[user_id])
            return result["channel"]["id"]
        except Exception as e:
            print(f"Error creating group DM: {str(e)}")
            raise e

    async def handle_summary(self, channel_id: str, user_id: str) -> None:
        """Handle the summary command."""
        try:
            # Get messages from the channel
            messages = await self.slack_repository.fetch_messages(channel_id)
                    
            # Generate summary using OpenAI
            summary = await self.openai_service.analyze_conversation(
                conversation_messages=messages
            )

            channel_id = await self.get_bot_user_channel_id(user_id)
            # Also send the summary in the new DM
            self.client.chat_postMessage(
                channel=channel_id,
                text=summary,
                mrkdwn=True
            )   

        except Exception as e:
            print(f"Error in handle_summary: {str(e)}")
            # If there's an error, update the message to show the error
            self.client.chat_postMessage(
                channel=channel_id,
                text=f"Error: {str(e)}"
            )
