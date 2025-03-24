import ssl
import certifi
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import json
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

    def _convert_markdown_to_mrkdwn(self, text: str) -> str:
        """Convert markdown syntax to Slack mrkdwn syntax."""
        # Bold
        text = text.replace("**", "*")
        # Italic
        text = text.replace("*", "_")
        # Strikethrough
        text = text.replace("~~", "~")
        # Code blocks
        text = text.replace("```", "`")
        # Inline code
        text = text.replace("`", "`")
        # Bullet points
        text = text.replace("- ", "• ")
        # Numbered lists
        text = text.replace("1. ", "1. ")
        text = text.replace("2. ", "2. ")
        text = text.replace("3. ", "3. ")
        # Links
        text = text.replace("[", "<")
        text = text.replace("]", "|")
        text = text.replace(")", ">")
        # Blockquotes
        text = text.replace("> ", ">")
        # Headers (convert to bold)
        text = text.replace("# ", "*")
        text = text.replace("## ", "*")
        text = text.replace("### ", "*")
        return text

    async def handle_summary(self, channel_id: str, user_id: str) -> None:
        """Handle the summary command."""
        try:
            try:
                joinResponse = self.client.conversations_join(channel=channel_id)
                print(joinResponse)
            except SlackApiError as e:
                print(e.response)
                raise e
            
            # Get messages from the channel
            messages = await self.slack_repository.fetch_messages(channel_id)
                    
            # Generate summary using OpenAI
            summary = await self.openai_service.analyze_conversation(
                conversation_messages=messages
            )

            channel_id = await self.get_bot_user_channel_id(user_id)
            # Format the summary using markdown conversion
            formatted_summary = self._convert_markdown_to_mrkdwn(summary)
            
            # Convert ** text to header block
            blocks = []
            parts = summary.split("**")
            for i, part in enumerate(parts):
                if i % 2 == 1:  # Odd indices are the bold text
                    blocks.append({
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": part
                        }
                    })
                elif part.strip():  # Only add non-empty content
                    blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": self._convert_markdown_to_mrkdwn(part)
                        }
                    })
            
            self.client.chat_postMessage(
                channel=channel_id,
                text=formatted_summary,
                blocks=blocks,
                mrkdwn=True
            )   

        except SlackApiError as e:
            print(e.response)
            channel_id = await self.get_bot_user_channel_id(user_id)
            self.client.chat_postMessage(
                channel=channel_id,
                text=f"Error: {str(e.response['error'])}"
            )
        except Exception as e:
            print(f"Error in handle_summary: {str(e)}")
            # If there's an error, update the message to show the error
            channel_id = await self.get_bot_user_channel_id(user_id)
            self.client.chat_postMessage(
                channel=channel_id,
                text=f"Error: {str(e)}"
            )
