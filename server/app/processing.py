from datetime import datetime
from .integrations.googleTasksConnector import create_google_task
from .integrations.googleCalendarConnector import create_calendar_event
from .integrations.notionConnector import create_notion_page

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
        note_response = create_notion_page(note)
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
        shopping_response = create_notion_page(shopping_data)
        responses.append({
            "type": "notion_shopping_list",
            "data": shopping_data,
            "response": shopping_response
        })
    return responses
