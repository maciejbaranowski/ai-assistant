import os, json, re
import logging
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI

gemini = ChatGoogleGenerativeAI(
    model=os.getenv("LANGCHAIN_MODEL", "gemini-2.5-flash"),
    google_api_key=os.getenv("GOOGLE_AI_API_KEY")
)

def invoke_data_extraction_prompt(message: str):
    logging.debug("Invoking data extraction prompt.")
    return gemini.invoke(
        f"""
Przeanalizuj wiadomość i zwróć informacje zawarte w treści w ustrukturyzowany sposób wyłącznie w formacie JSON, w formie rekordu z polami: tasks, events, notes, shopping_lists.
Każdy z tych rekordów powinien być listą obiektów, gdzie każdy obiekt zawiera następujące pola:
Dla tasks:
- title: tytuł zadania
- description: opis zadania
- due_date: data wykonania zadania, jeśli nie da się określić, załóż że zadanie jest do wykonania na jutro.
Dla notes:
- title: tytuł notatki
- content: treść notatki. Jeśli notatka jest długa, podziel ją na akapity. Jeśli notatka zawiera listy, zachowaj ich strukturę, używając myślników do oznaczenia punktów listy.
  Jeśli notatka zawiera prośbę skierowaną do asystenta, spełnij ją, wypisz swoje wnioski w treści notatki w nawiasie kwadratowym [].
Dla shopping_lists:
- content: lista przedmiotów do kupienia, w formie nienumerowanej listy podzielonej na kategorie, zgodnie z tym jak podzielone są produkty w supermarketach.
  Zwróć uwagę żeby uwzględnić wszystkie wspomniane w komunikacie pozycje. Jeśli pojawiają się dodatkowe informacje, takie jak ilość, marka, rodzaj czy warunki kiedy należy kupić
  (na przykład, "jeśli będzie długi termin ważności"), uwzględnij je w opisie pozycji.s
Dla events:
- title: tytuł wydarzenia
- description: opis wydarzenia
- start_datetime: data i czas rozpoczęcia
- end_datetime: data i czas zakończenia. Jeśli nie da się określić, załóż że wydarzenie trwa 1 godzinę.

Bierz pod uwagę że dziś jest {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, wszystkie wydarzenia powinny być w przyszłości, nie mogą być w przeszłości.
Przykład odpowiedzi:
{{
    tasks: [
        {{
            "title": "Zadanie 1",
            "description": "Opis zadania 1",
            "due_date": "2025-09-10"
        }}
    ],
    notes: [
        {{
            "title": "Notatka 1",
            "content": "Treść notatki 1"
        }}
    ],
    shopping_lists: [
        {{
            "content": "Nabiał\n - Mleko (jeśli będzie długi termin ważności)\n - Jogurt naturalny marki Pilos\n - Jajka Ligol\nOwoce\n - Jabłka\n - Banany\n - Pomarańcze"
        }}
    ],
    events: [
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
}}
Zwróć uwagę, żeby odpowiedź była poprawnym JSON-em

Treść wiadomości: {message}""")

def extract_data_from_message(message: str):
    logging.debug("Extracting data from message.")
    response = invoke_data_extraction_prompt(message) 
    if not response or not response.content:
        logging.error("No response from Gemini")
        raise ValueError("No response from Gemini")
    
    token_usage = response.usage_metadata
    total_tokens = token_usage.get('total_tokens', 0) if token_usage else 0
    logging.debug(f"Gemini response: {response.content}")
    match = re.search(r"\{.*\}", response.content, re.DOTALL)
    if not match:
        logging.error("Could not find JSON array in Gemini response")
        raise ValueError("Could not find JSON array in Gemini response")
    
    try:
        json_data = json.loads(match.group(0))
        logging.debug("Successfully extracted JSON data.")
    except json.JSONDecodeError as e:
        logging.error(f"Could not decode JSON from Gemini response: {e}")
        raise ValueError("Could not decode JSON from Gemini response")
        
    return json_data, total_tokens
