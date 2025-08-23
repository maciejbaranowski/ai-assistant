import os
from datetime import datetime
from fastapi import Body, FastAPI, Depends, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from langchain_google_community import CalendarToolkit
import google.generativeai as genai

from .processing import process_text_and_get_response
from .integrations.notionConnector import create_notion_page

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
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.post("/gemini")
def gemini_endpoint(
    token: None = Depends(verify_token),
    body: dict = Body(...)
):
    message = body.get("message")
    if not message:
        raise HTTPException(status_code=400, detail="Missing 'message' in request body")

    try:
        response_data = process_text_and_get_response(message)
        return {"success": True, **response_data}
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/audio-input")
async def audio_input(
    request: Request,
    token: None = Depends(verify_token)
):
    content_type = request.headers.get('content-type')
    if not content_type == "audio/3gpp":
        raise HTTPException(status_code=400, detail=f"Invalid content type: {content_type}. Only audio/3gpp is accepted.")

    audio_bytes = await request.body()

    try:
        # Use the Gemini 1.5 Flash model for fast transcription
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        
        audio_file = {"mime_type": "audio/3gpp", "data": audio_bytes}
        
        response = model.generate_content(
            ["Dokonaj transkrypcji tego pliku audio:", audio_file]
        )
        
        transcription = response.text

        # Save transcription to Notion
        if transcription:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            notion_page_data = {
                "title": f"Transcription - {now}",
                "content": transcription
            }
            create_notion_page(notion_page_data, NOTION_TRANSCRIPTION_PAGE_ID)

            response_data = process_text_and_get_response(transcription)
            return {"transcription": transcription, **response_data}
        else:
            return {"transcription": ""}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {e}")