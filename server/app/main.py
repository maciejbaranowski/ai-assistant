import os
import logging
from datetime import datetime
from fastapi import Body, FastAPI, Depends, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from langchain_google_community import CalendarToolkit
import google.generativeai as genai

from .processing import process_text_and_get_response
from .integrations.notionConnector import create_notion_page
from .audio import process_audio

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_AI_API_KEY"))
AUTH_TOKEN_SECRET = os.getenv("AUTH_TOKEN_SECRET")
NOTION_TRANSCRIPTION_PAGE_ID = os.getenv("NOTION_TRANSCRIPTION_PAGE_ID")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

calendarToolkit = CalendarToolkit(token_path="token.json")

def verify_token(x_auth: str = Header(..., alias="x-auth")):
    if x_auth != f"{AUTH_TOKEN_SECRET}":
        logging.error("Unauthorized access attempt")
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.post("/gemini")
def gemini_endpoint(
    token: None = Depends(verify_token),
    body: dict = Body(...)
):
    logging.debug("Received new message for processing.")
    message = body.get("message")
    if not message:
        logging.error("Missing 'message' in request body")
        raise HTTPException(status_code=400, detail="Missing 'message' in request body")

    try:
        response_data = process_text_and_get_response(message)
        logging.debug("Finished processing message.")
        return {"success": True, **response_data}
    except ValueError as e:
        logging.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/audio-input")
async def audio_input(
    request: Request,
    token: None = Depends(verify_token)
):
    logging.debug("Received new audio file for processing.")
    content_type = request.headers.get('content-type')
    if not content_type == "audio/3gpp":
        logging.error(f"Invalid content type: {content_type}")
        raise HTTPException(status_code=400, detail=f"Invalid content type: {content_type}. Only audio/3gpp is accepted.")

    audio_bytes = await request.body()

    if len(audio_bytes) > 500 * 1024:
        logging.error("Audio file is too large")
        raise HTTPException(status_code=413, detail="Audio file is too large. Maximum size is 500KB (~5 minutes).")

    try:
        response_data = process_audio(audio_bytes)
        return response_data
    except Exception as e:
        logging.error(f"Error processing audio: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing audio: {e}")