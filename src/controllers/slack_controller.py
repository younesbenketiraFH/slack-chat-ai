"""
Controller layer for handling Slack event routes.
"""

from typing import Dict, Any
from datetime import datetime, timedelta
import json

from fastapi import APIRouter, Request

from src.repositories.slack_repository import SlackRepository
from src.services.slack_service import SlackService
from src.services.openai_service import OpenAIService
from src.models.slack_models import SlackEventWrapper
from src.utilities.slack_utilities import is_duplicate_event

router = APIRouter()

slack_repository = SlackRepository()
openai_service = OpenAIService()
slack_service = SlackService(slack_repository, openai_service)

@router.post("/events")
async def handle_slack_events(request: Request) -> Dict[str, Any]:
    """Handle incoming Slack events."""
    raw_data = await request.json()
    print(f"Received event: {json.dumps(raw_data, indent=2)}")
    
    event_type = raw_data.get("type", "")
    
    match event_type:
        case "url_verification":
            return await slack_service.handle_url_verification(raw_data)
        case "event_callback":
            # Check for duplicate events
            event_id = raw_data.get("event_id")
            if event_id and is_duplicate_event(event_id):
                return {"status": "ok", "message": "Duplicate event"}
            
            event_wrapper = SlackEventWrapper(**raw_data)
            event = event_wrapper.event
            
            # Check if this is a direct message event
            if (event.type == "message" and 
                getattr(event, "channel_type", None) == "im" and 
                not getattr(event, "subtype", None)):  # Ignore message subtypes like message_changed
                
                await slack_service.handle_direct_message(event_wrapper)
            
            return {"status": "ok"}
        case _:
            return {"status": "ok"}