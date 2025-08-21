import os
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI

from dotenv import load_dotenv
load_dotenv()

gemini = ChatGoogleGenerativeAI(
    model=os.getenv("LANGCHAIN_MODEL", "gemini-2.5-flash"),
    google_api_key=os.getenv("GOOGLE_AI_API_KEY")
)

def invoke_data_extraction_prompt(message: str):
    return gemini.invoke(
        f"""
Przeanalizuj wiadomość i zwróć informacje o spotkaniach, wydarzeniach, zadaniach. Odpowiadaj wyłącznie w formacie JSON, w formie tablicy rekordów z polami:
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

Treść wiadomości: {message}""")