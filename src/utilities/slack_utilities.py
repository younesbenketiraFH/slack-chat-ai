"""
Utility functions for Slack event processing.
"""

from typing import Dict
from datetime import datetime, timedelta

# Store processed event IDs with timestamps
processed_events: Dict[str, datetime] = {}
# Clean up interval (5 minutes)
cleanup_interval = timedelta(minutes=5)

def clean_old_events() -> None:
    """Clean up old event IDs to prevent memory growth."""
    current_time = datetime.now()
    global processed_events
    processed_events = {
        event_id: timestamp 
        for event_id, timestamp in processed_events.items()
        if current_time - timestamp < cleanup_interval
    }

def is_duplicate_event(event_id: str) -> bool:
    """Check if an event has already been processed."""
    if event_id in processed_events:
        print(f"Duplicate event: {event_id}")
        return True
    processed_events[event_id] = datetime.now()
    clean_old_events()  # Periodically clean up old events
    print(f"Processing new event: {event_id}")
    return False 

