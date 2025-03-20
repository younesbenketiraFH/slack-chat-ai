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

    async def handle_summary(self, channel_id: str, response_url: str, ts: str | None = None) -> None:
        """Handle the summary command."""
        try:
            # Get messages from the channel
            messages = await self.slack_repository.fetch_messages(channel_id)
                    
            # Generate summary using OpenAI
            summary = await self.openai_service.analyze_conversation(
                conversation_messages=messages
            )

            # Update the ephemeral message using response_url
            async with ClientSession() as session:
                await session.post(
                    response_url,
                    json={
                        "response_type": "ephemeral",
                        "text": summary,
                        "replace_original": True
                    }
                )
        except Exception as e:
            print(f"Error in handle_summary: {str(e)}")
            # If there's an error, update the message to show the error
            async with ClientSession() as session:
                await session.post(
                    response_url,
                    json={
                        "response_type": "ephemeral",
                        "text": f"❌ Error generating summary: {str(e)}",
                        "replace_original": True
                    }
                )
