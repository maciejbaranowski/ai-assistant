import os, json, re
from fastapi import Body, FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from langchain_google_community import CalendarToolkit
from datetime import datetime
from .prompts import invoke_data_extraction_prompt
from .googleCalendarConnector import create_calendar_event

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
    match = re.search(r"\[.*\]", response.content, re.DOTALL)
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
    
    calendarResponses = [create_calendar_event(item) for item in data]
    
    return {"gemini":data,"calendar":calendarResponses}