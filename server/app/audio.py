import os
import logging
from datetime import datetime
import google.generativeai as genai
from .processing import process_text_and_get_response
from .integrations.notionConnector import create_notion_page

genai.configure(api_key=os.getenv("GOOGLE_AI_API_KEY"))

NOTION_TRANSCRIPTION_PAGE_ID = os.getenv("NOTION_TRANSCRIPTION_PAGE_ID")

def process_audio(audio_bytes: bytes):
    logging.debug("Transcribing audio with Gemini.")
    # Use the Gemini 1.5 Flash model for fast transcription
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    
    audio_file = {"mime_type": "audio/3gpp", "data": audio_bytes}
    
    response = model.generate_content(
        ["Dokonaj transkrypcji tego pliku audio:", audio_file]
    )
    
    transcription = response.text
    logging.debug("Transcription successful.")

    # Save transcription to Notion
    if transcription:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        notion_page_data = {
            "title": f"Transcription - {now}",
            "content": transcription
        }
        create_notion_page(notion_page_data, NOTION_TRANSCRIPTION_PAGE_ID)
        logging.debug("Transcription saved to Notion.")

        logging.debug("Processing transcription.")
        response_data = process_text_and_get_response(transcription)
        logging.debug("Finished processing transcription.")
        return {"transcription": transcription, **response_data}
    else:
        logging.debug("Empty transcription, nothing to process.")
        return {"transcription": ""}
