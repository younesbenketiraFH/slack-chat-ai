"""
Controller layer for handling Slack event routes.
"""

from typing import Dict, Any, Union
from urllib.parse import parse_qs
import asyncio

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from src.repositories.slack_repository import SlackRepository
from src.services.slack_service import SlackService
from src.services.openai_service import OpenAIService

router = APIRouter()

slack_repository = SlackRepository()
openai_service = OpenAIService()
slack_service = SlackService(slack_repository, openai_service)

@router.post("/events", response_model=None)
async def handle_slack_events(request: Request) -> Union[Dict[str, Any], JSONResponse]:
    """Handle incoming Slack events."""
    # Get the raw body first to debug
    raw_data = await request.json()
    event_type = raw_data.get("type")
    
    match event_type:
        case "url_verification":
            return {
                "challenge": raw_data.get("challenge")
            }
        case _:
            raise Exception(f"Unhandled event type: {event_type}")

@router.post("/commands", response_model=None)
async def handle_slack_commands(request: Request) -> Union[Dict[str, Any], JSONResponse]:
    """Handle incoming Slack commands."""

    body = await request.body()

    # Parse form data
    form_data = parse_qs(body.decode())
    command = form_data.get("command", [None])[0]
    channel_id = form_data.get("channel_id", [None])[0]
    text = form_data.get("text", [""])[0]
    user_id = form_data.get("user_id", [None])[0]
    
    print(f"Received command: {command} with text: {text} in channel: {channel_id} from user: {user_id}")
    
    # Validate required parameters
    if not command:
        raise Exception("No command provided")
    
    if not channel_id:
        raise Exception("No channel ID provided")
    
    match command:
        case "/summarize":
            response_url = form_data.get("response_url", [None])[0]
            if not response_url:
                raise Exception("No response URL provided")
            
            # Start the summary task
            asyncio.create_task(slack_service.handle_summary(channel_id, response_url, None))
            
            # Send initial response
            return {
                "response_type": "ephemeral",
                "text": "⏳ Summarizing messages... I'll post the summary soon!"
            }

        case _:
            raise Exception(f"Unhandled command: {command}")


