"""
Controller layer for handling Slack event routes.
"""

from typing import Dict, Any, Union, Optional
import json
from urllib.parse import parse_qs
from aiohttp import ClientSession
import asyncio

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse

from src.repositories.slack_repository import SlackRepository
from src.services.slack_service import SlackService
from src.services.openai_service import OpenAIService
from src.models.slack_models import SlackEventWrapper
from src.utilities.slack_utilities import is_duplicate_event

router = APIRouter()

slack_repository = SlackRepository()
openai_service = OpenAIService()
slack_service = SlackService(slack_repository, openai_service)

@router.post("/events", response_model=None)
async def handle_slack_events(request: Request) -> Union[Dict[str, Any], JSONResponse]:
    """Handle incoming Slack events."""
    try:
        # Get the raw body first to debug
        body = await request.body()
        print(f"Raw request body: {body}")
        
        if not body:
            return JSONResponse(
                status_code=400,
                content={"error": "Empty request body"}
            )

        # Check content type to determine how to parse the request
        content_type = request.headers.get("content-type", "").lower()
        
        if "application/x-www-form-urlencoded" in content_type:
            # Handle Slack commands
            form_data = parse_qs(body.decode())
            command = form_data.get("command", [None])[0]
            channel_id = form_data.get("channel_id", [None])[0]
            text = form_data.get("text", [""])[0]
            user_id = form_data.get("user_id", [None])[0]
            
            print(f"Received command: {command} with text: {text} in channel: {channel_id} from user: {user_id}")
            
            # Validate required parameters
            if not command:
                return {
                    "response_type": "ephemeral",
                    "text": "Error: No command provided"
                }
            
            if not channel_id:
                return {
                    "response_type": "ephemeral",
                    "text": "Error: No channel ID provided"
                }
            
            if command == "/summarize":
                # ✅ 1. **Immediately acknowledge Slack** to avoid timeout
                ack_response = {
                    "response_type": "ephemeral",
                    "text": "⏳ Summarizing messages... I'll post the summary soon!"
                }

                response_url = form_data.get("response_url", [None])[0]
                if not response_url:
                    return {
                        "response_type": "ephemeral",
                        "text": "Error: No response URL provided"
                    }
                
                asyncio.create_task(handle_summary(channel_id, response_url))

                # Send response back to Slack
                return ack_response
            
            return {
                "response_type": "ephemeral",  # Only visible to the user who triggered the command
                "text": f"Unhandled command: {command}"
            }
            
        else:
            # Handle JSON events
            try:
                raw_data = await request.json()
                print(f"Parsed JSON data: {json.dumps(raw_data, indent=2)}")
            except json.JSONDecodeError as e:
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": "Invalid JSON in request body",
                        "detail": str(e),
                        "body": body.decode() if body else None
                    }
                )
            
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
                    return {"status": "ok", "message": f"Unhandled event type: {event_type}"}
                    
    except Exception as e:
        print(f"Error handling Slack event: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
    
async def handle_summary(channel_id: str, response_url: str) -> None:
    """Generate a summary and send it to the response URL."""
    try:
        # Get messages from the channel
        messages = await slack_repository.fetch_messages(channel_id)
                
        # Generate summary using OpenAI
        summary = await openai_service.analyze_conversation(
            user_question="Please summarize these messages",
            conversation_messages=messages
        )

        # Prepare the response
        response_payload = {
            "response_type": "ephemeral",  # Only visible to the user who triggered the command
            "text": summary
        }

        # Send the response to the response_url
        # Import this at the top of the file: from aiohttp import ClientSession
        async with ClientSession() as session:
            async with session.post(
                response_url,
                json=response_payload,
                headers={"Content-Type": "application/json"}
            ) as resp:
                if resp.status != 200:
                    print(f"Error sending response to Slack: {await resp.text()}")
    except Exception as e:
        print(f"Error in handle_summary: {str(e)}")