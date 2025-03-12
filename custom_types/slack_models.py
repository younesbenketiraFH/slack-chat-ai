from pydantic import BaseModel
from typing import List, Literal, Union, Optional

class SlackEventBase(BaseModel):
    type: str
    user: str
    text: str
    ts: str
    channel: str
    event_ts: str

class AppMentionEvent(SlackEventBase):
    type: Literal["app_mention"]

class SlackEventWrapper(BaseModel):
    token: str
    team_id: str
    api_app_id: str
    event: AppMentionEvent
    type: Literal["event_callback"]
    event_id: str
    event_time: int
    authed_users: Optional[List[str]] = None

class SlackUrlVerificationRequest(BaseModel):
    token: str
    challenge: str
    type: Literal["url_verification"]

SlackRequestPayload = Union[SlackEventWrapper, SlackUrlVerificationRequest] 