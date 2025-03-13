"""
Main FastAPI application.
"""

from fastapi import FastAPI, Request

from src.controllers import slack_router

# Initialize FastAPI app
app = FastAPI(
    title="Slack AI Bot",
    description="A Slack bot that uses OpenAI to respond to messages",
    version="1.0.0"
)

app.include_router(slack_router, prefix="/slack")