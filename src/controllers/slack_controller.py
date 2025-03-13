"""
Controller layer for handling Slack event routes.
"""

from typing import Dict, Any

from fastapi import APIRouter, Request

from src.repositories.slack_repository import SlackRepository
from src.services.slack_service import SlackService
from src.services.openai_service import OpenAIService

router = APIRouter()

slack_repository = SlackRepository()
openai_service = OpenAIService()
slack_service = SlackService(slack_repository, openai_service)

@router.post("/events")
async def handle_slack_events(request: Request) -> Dict[str, Any]:
    """Handle incoming Slack events."""
    raw_data = await request.json()
    
    event_type = raw_data.get("type", "")
    return await slack_service.handle_event(event_type, raw_data)