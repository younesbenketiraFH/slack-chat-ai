# Slack Chat AI Bot

A Slack bot that provides AI-powered conversation summaries using OpenAI's GPT models

## Features

- 🤖 AI-powered conversation summaries
- 💬 Sends summaries directly to users in a private DM
- 🎯 Supports both public channels and private conversations (must be invited first)

## Prerequisites

- Python 3.8+
- Slack Bot Token with appropriate permissions
- OpenAI API Key
- Slack workspace with admin access

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/slack-chat-ai.git
cd slack-chat-ai
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the root directory with:
```env
SLACK_BOT_TOKEN=xoxb-your-bot-token
OPENAI_API_KEY=your-openai-api-key
```

4. Invite the bot to your workspace:
   - Go to your Slack workspace settings
   - Navigate to "Apps" → "Custom Integrations" → "Bots"
   - Add the bot to your workspace
   - Note down the Bot User OAuth Token

## Usage

### Basic Commands

1. **Generate Summary**
   - Type `/summary` in any channel where the bot is present, if not present it will try to join (you must manually invite for private DMs and group chats)
   - The bot will join the channel, analyze the conversation, and send you a DM with the summary

### Bot Permissions Required

The bot needs the following OAuth scopes:
- `chat:write` - To send messages
- `channels:join` - To join channels
- `channels:read` - To read channel messages
- `im:write` - To open DMs
- `im:read` - To read DM messages
- `groups:read` - To read private channel messages
- `groups:write` - To join private channels
- `users:read` - To get user information for message formatting
- `commands` - To handle slash commands

### Project Structure

```
slack-chat-ai/
├── src/
│   ├── services/
│   │   ├── slack_service.py
│   │   └── openai_service.py
│   └── repositories/
│       └── slack_repository.py
├── requirements.txt
└── README.md
```