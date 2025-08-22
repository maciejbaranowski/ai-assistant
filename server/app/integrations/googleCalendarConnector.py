import os
import re
from dotenv import load_dotenv
from langchain_google_community.calendar.create_event import CalendarCreateEvent
from ..auth_manager import auth_manager

load_dotenv()

CALENDAR_ID = os.getenv("CALENDAR_ID", "primary")

# Ensure we have proper authentication before initializing
try:
    auth_manager.get_credentials()  # This ensures we have all required scopes
    createCalendarEventTool = CalendarCreateEvent()
except Exception as e:
    print(f"Warning: Could not initialize calendar tool: {e}")
    createCalendarEventTool = None

def create_calendar_event(data_item):
    if not createCalendarEventTool:
        return {
            'success': False,
            'error': 'Calendar tool not initialized'
        }
    
    result_string = createCalendarEventTool.invoke(
        {
            "calendar_id": CALENDAR_ID,
            "summary": data_item.get("title", "No Title"),
            "start_datetime": data_item.get("start_datetime"),
            "end_datetime": data_item.get("end_datetime"),
            "timezone": "Europe/Warsaw",
            "description": data_item.get("description", "No Description")
        }
    )
    
    # Extract URL using regex
    match = re.search(r'\[here\]\((.*?)\)', result_string)
    html_link = match.group(1) if match else None

    return {
        'success': True,
        'htmlLink': html_link,
        'event_data': result_string
    }