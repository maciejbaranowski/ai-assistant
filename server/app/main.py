import os, json, re
from fastapi import Body, FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_community import CalendarToolkit
from langchain_google_community.calendar.create_event import CalendarCreateEvent
from datetime import datetime

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

gemini = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GOOGLE_AI_API_KEY"))

calendarToolkit = CalendarToolkit(token_path="token.json")
createCalendarEventTool = CalendarCreateEvent()
CALENDAR_ID = os.getenv("CALENDAR_ID", "primary")

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
    response = gemini.invoke(
        f"""Przeanalizuj wiadomość i zwróć informacje o spotkaniach, wydarzeniach, zadaniach. Odpowiadaj wyłącznie w formacie JSON, w formie tablicy rekordów z polami:
            - title: tytuł wydarzenia
            - description: opis wydarzenia
            - start_datetime: data i czas rozpoczęcia
            - end_datetime: data i czas zakończenia. Jeśli nie da się określić, załóż że wydarzenie trwa 1 godzinę.
            Bierz pod uwagę że dziś jest {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, wszystkie wydarzenia powinny być w przyszłości, nie mogą być w przeszłości.
            Przykład odpowiedzi:
            [
                {{
                    "title": "Spotkanie z klientem",
                    "description": "Omówienie projektu",
                    "start_datetime": "2025-09-11 12:00:00",
                    "end_datetime": "2025-09-11 13:00:00"
                }},
                {{
                    "title": "Zadanie do wykonania",
                    "description": "Przygotowanie raportu",
                    "start_datetime": "2025-09-11 15:00:00",
                    "end_datetime": "2025-09-11 16:00:00"
                }}
            ]

            Treść wiadomości: {message}"""
    )
    
    if not response or not response.content:
        raise HTTPException(status_code=500, detail="No response from Gemini")
    
    match = re.search(r"\[.*\]", response.content, re.DOTALL)
    if not match:
        raise HTTPException(status_code=500, detail="Could not find JSON array in Gemini response")
    
    parsedResponse = json.loads(match.group(0))   
    
    calendarResponses = []
    for item in parsedResponse:
        calendarResponses.append(createCalendarEventTool.invoke(
            {
            "calendar_id": CALENDAR_ID,
            "summary": item.get("title", "No Title"),
            "start_datetime": item.get("start_datetime"),
            "end_datetime": item.get("end_datetime"),
            "timezone": "Europe/Warsaw",
            "description": item.get("description", "No Description")
            }
        ))

    return {"gemini":parsedResponse,"calendar":calendarResponses}