"""
Controller layer for handling Slack event routes.
"""

from typing import Dict, Any
from datetime import datetime, timedelta

from fastapi import APIRouter, Request

from src.repositories.slack_repository import SlackRepository
from src.services.slack_service import SlackService
from src.services.openai_service import OpenAIService
from src.models.slack_models import SlackEventWrapper

router = APIRouter()

slack_repository = SlackRepository()
openai_service = OpenAIService()
slack_service = SlackService(slack_repository, openai_service)

# Store processed event IDs with timestamps
processed_events: Dict[str, datetime] = {}
# Clean up interval (5 minutes)
cleanup_interval = timedelta(minutes=5)

def _clean_old_events() -> None:
    """Clean up old event IDs to prevent memory growth."""
    current_time = datetime.now()
    global processed_events
    processed_events = {
        event_id: timestamp 
        for event_id, timestamp in processed_events.items()
        if current_time - timestamp < cleanup_interval
    }

def _is_duplicate_event(event_id: str) -> bool:
    """Check if an event has already been processed."""
    if event_id in processed_events:
        print(f"Duplicate event: {event_id}")
        return True
    processed_events[event_id] = datetime.now()
    _clean_old_events()  # Periodically clean up old events
    print(f"Processing new event: {event_id}")
    return False

@router.post("/events")
async def handle_slack_events(request: Request) -> Dict[str, Any]:
    """Handle incoming Slack events."""
    raw_data = await request.json()
    event_type = raw_data.get("type", "")
    
    # Handle URL verification
    if event_type == "url_verification":
        return await slack_service.handle_url_verification(raw_data)
        
    # Handle event callbacks
    if event_type == "event_callback":
        # Check for duplicate events
        event_id = raw_data.get("event_id")
        if event_id and _is_duplicate_event(event_id):
            return {"status": "ok", "message": "Duplicate event"}
        
        event_wrapper = SlackEventWrapper(**raw_data)
        
        # Route to appropriate service method based on event type
        if event_wrapper.event.type == "app_mention":
            await slack_service.handle_app_mention(event_wrapper)
        
        return {"status": "ok"}
        
    return {"status": "ok"}