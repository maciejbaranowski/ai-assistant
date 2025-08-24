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

    model = genai.GenerativeModel('gemini-2.5-flash')
    
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

def process_conversation(audio_bytes: bytes):
    logging.debug("Transcribing conversation with Gemini.")
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    audio_file = {"mime_type": "audio/3gpp", "data": audio_bytes}
    
    response = model.generate_content(
        ["Dokonaj transkrypcji tego pliku audio. Zwróć uwagę że jest to konwersacja między dwiema osboami, rozdziel w widoczny sposób kwestie obydwu z nich:", audio_file]
    )
    
    transcription = response.text
    logging.debug("Transcription successful.")

    # Save transcription to Notion
    if transcription:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        notion_page_data = {
            "title": f"Rozmowa - {now}",
            "content": transcription
        }
        create_notion_page(notion_page_data, NOTION_TRANSCRIPTION_PAGE_ID)
        logging.debug("Transcription saved to Notion.")

        return {"transcription": transcription}
    else:
        logging.debug("Empty transcription, nothing to process.")
        return {"transcription": ""}
