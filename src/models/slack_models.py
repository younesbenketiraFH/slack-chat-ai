"""
Slack event models and type definitions.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel

class SlackEventType(BaseModel):
    """Model for Slack event data."""
    type: str
    user: Optional[str] = None
    text: Optional[str] = None
    ts: Optional[str] = None
    channel: Optional[str] = None
    event_ts: Optional[str] = None
    channel_type: Optional[str] = None  # Added for message.im events
    subtype: Optional[str] = None  # Added to handle message subtypes

class SlackEventWrapper(BaseModel):
    """Wrapper model for Slack events."""
    token: str
    team_id: str
    api_app_id: str
    event: SlackEventType
    type: str
    event_id: str
    event_time: int
    authorizations: List[Dict[str, Any]]
    is_ext_shared_channel: Optional[bool] = None
    event_context: Optional[str] = None

# Requests & Responses
