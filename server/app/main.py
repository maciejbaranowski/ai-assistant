import os, json, re
from fastapi import Body, FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from langchain_google_community import CalendarToolkit
from datetime import datetime

from .integrations.notionConnector import create_notion_page
from .prompts import invoke_data_extraction_prompt
from .integrations.googleCalendarConnector import create_calendar_event
from .integrations.googleTasksConnector import create_google_task
from .integrations.ntfyConnector import send_ntfy_notification

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AUTH_TOKEN_SECRET = os.getenv("AUTH_TOKEN_SECRET")

calendarToolkit = CalendarToolkit(token_path="token.json")

def verify_token(x_auth: str = Header(..., alias="x-auth")):
    if x_auth != f"{AUTH_TOKEN_SECRET}":
        raise HTTPException(status_code=401, detail="Unauthorized")

def extract_data_from_message(message: str):
    response = invoke_data_extraction_prompt(message) 
    if not response or not response.content:
        raise HTTPException(status_code=500, detail="No response from Gemini")
    match = re.search(r"\{.*\}", response.content, re.DOTALL)
    if not match:
        raise HTTPException(status_code=500, detail="Could not find JSON array in Gemini response")
    return json.loads(match.group(0))

@app.post("/gemini")
def gemini_endpoint(
    token: None = Depends(verify_token),
    body: dict = Body(...)
):
    message = body.get("message")
    if not message:
        raise HTTPException(status_code=400, detail="Missing 'message' in request body")

    data = extract_data_from_message(message)
    responses = []
    
    # Process tasks - create Google Tasks
    for task in data.get("tasks", []):
        task_response = create_google_task(task)
        responses.append({
            "type": "google_task",
            "data": task,
            "response": task_response
        })
    
    # Process events - create Google Calendar events
    for event in data.get("events", []):
        event_response = create_calendar_event(event)
        responses.append({
            "type": "google_calendar",
            "data": event,
            "response": event_response
        })
    
    # Process notes - create Notion pages
    for note in data.get("notes", []):
        note_response = create_notion_page(note)
        responses.append({
            "type": "notion_page",
            "data": note,
            "response": note_response
        })
    
    # Process shopping lists - create Notion pages
    for shopping_list in data.get("shopping_lists", []):
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

    for response in responses:
        if response.get("type") == "google_task":
            send_ntfy_notification(
                title="Nowe zadanie w Google Tasks",
                message=f'Zadanie "{response.get("data", {}).get("title", "bez tytułu")}" zostało utworzone.',
                tags=["white_check_mark"],
                actions=[f'view, Otwórz zadanie, {response.get("response", {}).get("webViewLink", "")}']
            )
        elif response.get("type") == "google_calendar":
            send_ntfy_notification(
                title="Nowe wydarzenie w Kalendarzu Google",
                message=f'Wydarzenie "{response.get("data", {}).get("title", "bez tytułu")}" zostało utworzone na {response.get("data", {}).get("start_datetime", "nieznana data")}.',
                tags=["calendar"],
                actions=[f'view, Otwórz wydarzenie, {response.get("response", {}).get("htmlLink", "")}']
            )
        elif response.get("type") == "notion_page":
            send_ntfy_notification(
                title="Nowa strona w Notion",
                message=f'Notatka "{response.get("data", {}).get("title", "bez tytułu")}" została utworzona.',
                tags=["notebook_with_decorative_cover"],
                actions=[f'view, Otwórz stronę, {response.get("response", {}).get("url", "")}']
            )
        elif response.get("type") == "notion_shopping_list":
            send_ntfy_notification(
                title="Nowa lista zakupów w Notion",
                message=f'Lista zakupów "{response.get("data", {}).get("title", "bez tytułu")}" została utworzona.',
                tags=["shopping_trolley"],
                actions=[f'view, Otwórz listę, {response.get("response", {}).get("url", "")}']
            )

    return {
        "success": True,
        "gemini_parsed_data": data,
        "integrations": responses,
        "summary": {
            "tasks_created": len(data.get("tasks", [])),
            "events_created": len(data.get("events", [])),
            "notes_created": len(data.get("notes", [])),
            "shopping_lists_created": len(data.get("shopping_lists", []))
        }
    }