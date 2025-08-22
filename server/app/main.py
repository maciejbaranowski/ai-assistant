import os, json, re
from fastapi import Body, FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from langchain_google_community import CalendarToolkit

from .prompts import invoke_data_extraction_prompt
from .processing import process_tasks, process_events, process_notes, process_shopping_lists
from .notifications import send_notifications

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
    
    token_usage = response.usage_metadata
    total_tokens = token_usage.get('total_tokens', 0) if token_usage else 0

    match = re.search(r"\{.*\}", response.content, re.DOTALL)
    if not match:
        raise HTTPException(status_code=500, detail="Could not find JSON array in Gemini response")
    
    json_data = json.loads(match.group(0))
    return json_data, total_tokens

@app.post("/gemini")
def gemini_endpoint(
    token: None = Depends(verify_token),
    body: dict = Body(...)
):
    message = body.get("message")
    if not message:
        raise HTTPException(status_code=400, detail="Missing 'message' in request body")

    data, total_tokens = extract_data_from_message(message)
    
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
        "success": True,
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