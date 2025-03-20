import ssl
import certifi
from slack_sdk import WebClient

from aiohttp import ClientSession
from src.repositories.slack_repository import SlackRepository
from src.services.openai_service import OpenAIService

class SlackService:
    def __init__(self, slack_repository: SlackRepository, openai_service: OpenAIService):
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        self.client = WebClient(ssl=ssl_context)
        self.slack_repository = slack_repository
        self.openai_service = openai_service

    async def handle_summary(self, channel_id: str, response_url: str) -> None:
        """Handle the summary command."""
        # Get messages from the channel
        messages = await self.slack_repository.fetch_messages(channel_id)
                
        # Generate summary using OpenAI
        summary = await self.openai_service.analyze_conversation(
            conversation_messages=messages
        )

        # Send the response to the response_url
        async with ClientSession() as session:
            async with session.post(
                response_url,
                json={
                    "response_type": "ephemeral",  # Only visible to the user who triggered the command
                    "text": summary
                },
                headers={"Content-Type": "application/json"}
            ) as resp:
                if resp.status != 200:
                    print(f"Error sending response to Slack: {await resp.text()}")
                    raise Exception(f"Error sending response to Slack: {await resp.text()}")
