from typing import Dict, Any, Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import openai
import ssl
import certifi
import os
from dotenv import load_dotenv

from custom_types import (
    SlackEventWrapper,
    SlackUrlVerificationRequest,
    SlackRequestPayload
)

# Load environment variables
load_dotenv()

# Environment variables
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
if not SLACK_BOT_TOKEN:
    raise ValueError("SLACK_BOT_TOKEN environment variable is not set")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

PORT = int(os.getenv("PORT", "3000"))
HOST = os.getenv("HOST", "0.0.0.0")

# Initialize FastAPI app
app = FastAPI(
    title="Slack AI Bot",
    description="A Slack bot that uses OpenAI to respond to messages",
    version="1.0.0"
)

# Initialize Slack client
ssl_context = ssl.create_default_context(cafile=certifi.where())
slack_client = WebClient(
    token=SLACK_BOT_TOKEN,
    ssl=ssl_context
)

async def fetch_messages(channel_id: str, limit: int = 20) -> str:
    """
    Fetch recent messages from a Slack channel.
    
    Args:
        channel_id (str): The ID of the channel to fetch messages from
        limit (int, optional): Maximum number of messages to fetch. Defaults to 20.
    
    Returns:
        str: A string containing all messages concatenated with newlines
    """
    try:
        response = slack_client.conversations_history(channel=channel_id, limit=limit)
        return "\n".join([msg["text"] for msg in response["messages"] if "text" in msg])
    except SlackApiError as e:
        print(f"Error fetching messages: {e.response['error']}")
        return ""

async def handle_url_verification(data: Dict[str, Any]) -> Dict[str, str]:
    """
    Handle Slack URL verification challenge.
    
    Args:
        data (Dict[str, Any]): The verification request data
    
    Returns:
        Dict[str, str]: The challenge response
    """
    verification_data = SlackUrlVerificationRequest(**data)
    return {"challenge": verification_data.challenge}

async def handle_app_mention(event_data: SlackEventWrapper) -> None:
    """
    Handle app mention events from Slack.
    
    Args:
        event_data (SlackEventWrapper): The event data from Slack
    """
    channel_id = event_data.event.channel
    user_question = event_data.event.text

    # Fetch messages for context
    context = await fetch_messages(channel_id)

    # TODO: Implement OpenAI integration
    # For now, just send a simple response
    slack_client.chat_postMessage(channel=channel_id, text="Hello! I received your message.")

@app.post("/slack/events")
async def slack_events(request: Request) -> Dict[str, Any]:
    """
    Handle incoming Slack events.
    
    Args:
        request (Request): The incoming request object
    
    Returns:
        Dict[str, Any]: The response to send back to Slack
    
    Raises:
        HTTPException: If there's an error processing the request
    """
    try:
        raw_data = await request.json()
        print(f"Received data: {raw_data}")

        # Handle URL verification
        if raw_data.get("type") == "url_verification":
            return await handle_url_verification(raw_data)

        # Handle events
        if raw_data.get("type") == "event_callback":
            event_data = SlackEventWrapper(**raw_data)
            print(f"Received event: {event_data.event}")

            if event_data.event.type == "app_mention":
                await handle_app_mention(event_data)

        return {"status": "ok"}
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print(f"Starting server on {HOST}:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT)
