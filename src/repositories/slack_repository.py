"""
Repository layer for Slack operations.
"""

import os
import ssl
import json
from typing import List, Dict
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

    async def get_user_info(self, user_id: str) -> Dict:
        """Fetch user information including display name."""
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

    async def list_conversations(self) -> List[Dict]:
        """
        Fetch all conversations (channels, groups, DMs) that the bot is part of.
        Returns a list of conversations with their IDs and members.
        """
        try:
            # Get all conversations (channels, private channels, DMs)
            response = self.client.conversations_list(
                types="public_channel,private_channel,im,mpim"
            )
            
            conversations = []
            for channel in response["channels"]:
                print(f"Channel: {json.dumps(channel, indent=2)}\n\n")
                try:
                    members_response = self.client.conversations_members(channel=channel["id"])
                    member_ids = members_response["members"]
                    
                    # Get detailed info for each member
                    members = []
                    for member_id in member_ids:
                        member_info = await self.get_user_info(member_id)
                        members.append(member_info)
                    
                except SlackApiError as e:
                    print(f"Error fetching members for channel {channel['id']}: {e.response['error']}")
                    members = []

                conversation_info = {
                    "id": channel["id"],
                    "name": channel.get("name", "Direct Message"),
                    "type": channel["is_im"] and "dm" or channel["is_mpim"] and "group_dm" or channel["is_private"] and "private" or "public",
                    "members": members,
                    "member_count": len(members)
                }
                conversations.append(conversation_info)
                
            print(f"Conversations List:\n{json.dumps(conversations, indent=2)}")
            return conversations
            
        except SlackApiError as e:
            print(f"Error listing conversations: {e.response['error']}")
            raise HTTPException(
                status_code=e.response.get("status_code", 500),
                detail=f"Failed to list conversations: {e.response['error']}"
            )
        except Exception as e:
            print(f"Unexpected error listing conversations: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred while listing conversations."
            )

    async def fetch_messages(self, channel_id: str, limit: int = 20) -> str:
        """Fetch recent messages from a Slack channel."""
        try:
            response = self.client.conversations_history(channel=channel_id, limit=limit)
            print(f"Response: {response}")
            messages = [msg["text"] for msg in response["messages"] if "text" in msg]
            print(f"Messages: {json.dumps(messages, indent=2)}")
            return "\n".join(messages)
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

    async def send_message(self, channel_id: str, text: str, thread_ts: str = None) -> None:
        """Send a message to a Slack channel."""
        try:
            self.client.chat_postMessage(
                channel=channel_id,
                text=text,
                thread_ts=thread_ts
            )
        except SlackApiError as e:
            print(f"Error sending message: {e.response['error']}")
            raise HTTPException(
                status_code=e.response.get("status_code", 500),
                detail=f"Failed to send message: {e.response['error']}"
            )
        except Exception as e:
            print(f"Unexpected error sending message: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred while sending the message."
            ) 