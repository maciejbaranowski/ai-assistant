import os
from datetime import datetime
from .integrations.googleTasksConnector import create_google_task
from .integrations.googleCalendarConnector import create_calendar_event
from .integrations.notionConnector import create_notion_page
from .prompts import extract_data_from_message
from .notifications import send_notifications

# Make sure to set these environment variables in your .env file
NOTION_NOTES_PAGE_ID = os.getenv("NOTION_NOTES_PAGE_ID")
NOTION_SHOPPING_LIST_PAGE_ID = os.getenv("NOTION_SHOPPING_LIST_PAGE_ID")

def process_tasks(tasks):
    responses = []
    for task in tasks:
        task_response = create_google_task(task)
        responses.append({
            "type": "google_task",
            "data": task,
            "response": task_response
        })
    return responses

def process_events(events):
    responses = []
    for event in events:
        event_response = create_calendar_event(event)
        responses.append({
            "type": "google_calendar",
            "data": event,
            "response": event_response
        })
    return responses

def process_notes(notes):
    responses = []
    for note in notes:
        note_response = create_notion_page(note, NOTION_NOTES_PAGE_ID)
        responses.append({
            "type": "notion_page",
            "data": note,
            "response": note_response
        })
    return responses

def process_shopping_lists(shopping_lists):
    responses = []
    for shopping_list in shopping_lists:
        shopping_data = {
            "title": f"Lista zakupów {datetime.now().strftime('%m-%d')}",
            "content": shopping_list.get("content", "No content")
        }
        shopping_response = create_notion_page(shopping_data, NOTION_SHOPPING_LIST_PAGE_ID)
        responses.append({
            "type": "notion_shopping_list",
            "data": shopping_data,
            "response": shopping_response
        })
    return responses

def process_text_and_get_response(text: str):
    data, total_tokens = extract_data_from_message(text)
    
    tasks = data.get("tasks", [])
    events = data.get("events", [])
    notes = data.get("notes", [])
    shopping_lists = data.get("shopping_lists", [])

    responses = []
    responses.extend(process_tasks(tasks))
    responses.extend(process_events(events))
    responses.extend(process_notes(notes))
    responses.extend(process_shopping_lists(shopping_lists))

    send_notifications(responses)

    return {
        "gemini_parsed_data": data,
        "integrations": responses,
        "summary": {
            "tasks_created": len(tasks),
            "events_created": len(events),
            "notes_created": len(notes),
            "shopping_lists_created": len(shopping_lists),
            "total_tokens_used": total_tokens
        }
    }