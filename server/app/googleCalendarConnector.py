import os
from dotenv import load_dotenv

from langchain_google_community.calendar.create_event import CalendarCreateEvent

load_dotenv()

CALENDAR_ID = os.getenv("CALENDAR_ID", "primary")
createCalendarEventTool = CalendarCreateEvent()

def create_calendar_event(data_item):
    return createCalendarEventTool.invoke(
        {
            "calendar_id": CALENDAR_ID,
            "summary": data_item.get("title", "No Title"),
            "start_datetime": data_item.get("start_datetime"),
            "end_datetime": data_item.get("end_datetime"),
            "timezone": "Europe/Warsaw",
            "description": data_item.get("description", "No Description")
        }
    )