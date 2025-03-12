from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import openai
import ssl
import certifi
from custom_types import (
    SlackEventWrapper,
    SlackUrlVerificationRequest,
    SlackRequestPayload
)

app = FastAPI()

SLACK_BOT_TOKEN = "xoxb-8591071324085-8614894465584-PzzEECRnmuPDbjDUtreOBxiS"  # Get from Slack API dashboard
OPENAI_API_KEY = "sk-..."  # Get from OpenAI

# Initialize the Slack client with SSL configuration
ssl_context = ssl.create_default_context(cafile=certifi.where())
slack_client = WebClient(
    token=SLACK_BOT_TOKEN,
    ssl=ssl_context
)

def fetch_messages(channel_id, limit=20):
    """Fetch recent messages from Slack."""
    try:
        response = slack_client.conversations_history(channel=channel_id, limit=limit)
        return "\n".join([msg["text"] for msg in response["messages"] if "text" in msg])
    except SlackApiError as e:
        print(f"Error fetching messages: {e.response['error']}")
        return ""

@app.post("/slack/events")
async def slack_events(request: Request):
    print("Received request at /slack/events")
    try:
        raw_data = await request.json()
        print(f"Received data: {raw_data}")

        # Handle URL verification
        if raw_data.get("type") == "url_verification":
            verification_data = SlackUrlVerificationRequest(**raw_data)
            return {"challenge": verification_data.challenge}

        # Handle events
        if raw_data.get("type") == "event_callback":
            event_data = SlackEventWrapper(**raw_data)
            print(f"Received event: {event_data.event}")

            if event_data.event.type == "app_mention":
                channel_id = event_data.event.channel
                user_question = event_data.event.text

                # Fetch messages for context
                context = fetch_messages(channel_id)

                # Send AI response to Slack
                slack_client.chat_postMessage(channel=channel_id, text="Hello")

        return {"status": "ok"}
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)
