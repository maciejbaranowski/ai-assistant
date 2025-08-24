import logging
from fastapi import Body, FastAPI, Depends, HTTPException, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from .processing import process_text_and_get_response
from .audio import process_audio
from .auth import verify_token

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

assistant_router = APIRouter(
    prefix="/assistant",
    dependencies=[Depends(verify_token)]
)

@assistant_router.post("/text-command")
def assistant_text_command_endpoint(
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

@assistant_router.post("/audio-command")
async def assistant_audio_command_endpoint(
    request: Request
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

@assistant_router.post("/audio-conversation")
async def assistant_audio_conversation_endpoint(
    request: Request
):
    logging.debug("Received new audio file for processing.")
    content_type = request.headers.get('content-type')
    if not content_type == "audio/3gpp":
        logging.error(f"Invalid content type: {content_type}")
        raise HTTPException(status_code=400, detail=f"Invalid content type: {content_type}. Only audio/3gpp is accepted.")

    audio_bytes = await request.body()

    if len(audio_bytes) > 3 * 1024 * 1024:
        logging.error("Audio file is too large")
        raise HTTPException(status_code=413, detail="Audio file is too large. Maximum size is 3MB (~30 minutes).")

    try:
        response_data = process_audio(audio_bytes)
        return response_data
    except Exception as e:
        logging.error(f"Error processing audio: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing audio: {e}")

app.include_router(assistant_router)