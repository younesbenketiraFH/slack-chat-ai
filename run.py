#!/usr/bin/env python3

import os
import sys
import uvicorn
from dotenv import load_dotenv

def check_environment():
    """Check if all required environment variables are set."""
    required_vars = ["SLACK_BOT_TOKEN", "OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"- {var}")
        print("\nPlease set these variables in your .env file or environment.")
        sys.exit(1)

def main():
    """Main entry point for running the Slack AI Bot."""
    # Load environment variables
    load_dotenv()
    
    # Check environment variables
    check_environment()
    
    # Get configuration from environment or use defaults
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "3000"))
    reload = os.getenv("DEBUG", "false").lower() == "true"
    
    print(f"Starting Slack AI Bot server on {host}:{port}")
    print(f"Debug mode (reload): {reload}")
    
    # Run the server with the new module path
    uvicorn.run(
        "src.app:app",  # Updated import path
        host=host,
        port=port,
        reload=reload,
        ssl_keyfile=os.getenv("SSL_KEYFILE"),
        ssl_certfile=os.getenv("SSL_CERTFILE"),
    )

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1) 