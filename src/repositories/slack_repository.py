"""
Repository layer for Slack operations.
"""

import os
import ssl
import json
import re
from typing import List, Dict, Set, Optional, Any
from fastapi import HTTPException

import certifi
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

class SlackRepository:
    def __init__(self):
        try:
            token = os.getenv("SLACK_BOT_TOKEN")
            if not token:
                raise ValueError("SLACK_BOT_TOKEN environment variable is not set")
                
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            self.client = WebClient(token=token, ssl=ssl_context)
        except Exception as e:
            print(f"Error initializing Slack client: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to initialize Slack client. Please check your configuration."
            )

    async def fetch_messages(self, channel_id: str, limit: int = 20) -> str:
        try:
            # Get messages from the channel
            response = self.client.conversations_history(channel=channel_id, limit=limit)
            messages = response["messages"]
            
            # Extract all unique user IDs from messages
            user_ids: Set[str] = set()
            for msg in messages:
                if "user" in msg:
                    user_ids.add(msg["user"])
            
            # Get user info for all users
            users_map = {}
            for user_id in user_ids:
                user_data = await self.get_user_info(user_id)
                users_map[user_id] = user_data["display_name"]
            
            # Format messages as a conversation string
            conversation = []
            # Reverse messages to show oldest first
            for msg in reversed(messages):
                if "text" in msg and "user" in msg:
                    user_name = users_map.get(msg["user"], "Unknown")
                    conversation.append(f"{user_name}: {msg['text']}")
            
            # Join messages with newlines
            return "\n".join(conversation)

        except SlackApiError as e:
            print(f"Error fetching messages: {e.response['error']}")
            raise HTTPException(
                status_code=e.response.get("status_code", 500),
                detail=f"Failed to fetch messages: {e.response['error']}"
            )
        except Exception as e:
            print(f"Unexpected error fetching messages: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred while fetching messages."
            )
        
    async def get_user_info(self, user_id: str) -> Dict:
        try:
            response = self.client.users_info(user=user_id)
            user = response["user"]
            return {
                "id": user_id,
                "display_name": user["profile"].get("display_name") or user["real_name"],
                "real_name": user["real_name"],
                "email": user["profile"].get("email", ""),
                "is_bot": user.get("is_bot", False)
            }
        except SlackApiError as e:
            print(f"Error fetching user info for {user_id}: {e.response['error']}")
            return {
                "id": user_id,
                "display_name": "Unknown User",
                "real_name": "Unknown",
                "email": "",
                "is_bot": False
            }