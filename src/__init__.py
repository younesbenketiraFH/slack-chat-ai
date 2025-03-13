"""
Slack AI Bot Application Package

A FastAPI application that integrates Slack with OpenAI to provide
AI-powered responses to messages in Slack channels.
"""

__version__ = "1.0.0"
__author__ = "Your Name"

from .controllers import *
from .models import *
from .repositories import *
from .services import *

__all__ = ["SlackController", "SlackEventWrapper", "SlackUrlVerificationRequest", "SlackRequestPayload", "SlackRepository", "SlackService", "OpenAIService"]
