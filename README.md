# Gemini Powered Personal Assistant Backend

## Disclaimer

This project is my personal playground with AI. Content of this repository were created with a lot of assistance from LLM models - mostly Gemini-2.5-flash and Gemini-2.5-pro. It works best with Polish as an input language, prompts will need to be translated to use it for different languages efficiently

## Project Overview

This project is a backend server that acts as a personal assistant. It can process natural language input, either from a text message or an audio file, and turn it into structured actions. It uses Google's Gemini AI to understand the input and extract tasks, calendar events, notes, and shopping lists. These items are then automatically created in various third-party services.

## Technologies Used

- **Backend:** Python, FastAPI
- **AI / Machine Learning:** Google Gemini (via `google-generativeai` and `langchain-google-genai`)
- **Integrations:**
    - Google Tasks API
    - Google Calendar API
    - Notion API
    - ntfy (for notifications)
- **Containerization:** Docker, Docker Compose

## Setup and Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Set up Environment Variables

Create a file named `.env` in the `server/` directory. This file will hold all the necessary secrets and configuration values. Add the following variables to it:

```
# A secret token for authenticating requests to the server
AUTH_TOKEN_SECRET="your-secret-token"

# Google AI API Key for Gemini
GOOGLE_AI_API_KEY="your-google-ai-api-key"

# Notion API Key and Page IDs
NOTION_API_KEY="your-notion-api-key"
NOTION_TRANSCRIPTION_PAGE_ID="your-notion-page-id-for-transcriptions"
NOTION_NOTES_PAGE_ID="your-notion-page-id-for-notes"
NOTION_SHOPPING_LIST_PAGE_ID="your-notion-page-id-for-shopping-lists"

# ntfy topic for notifications
NTFY_TOPIC="your-ntfy-topic"
```

### 3. Set up Google Credentials

This application uses Google services for Calendar and Tasks, which require user-based OAuth authentication.

1.  **Enable the Google Calendar API and Google Tasks API** in your Google Cloud project.
2.  **Create OAuth 2.0 Client IDs** for a desktop application and download the `credentials.json` file.
3.  **Place the `credentials.json` file** in the `server/` directory.
4.  **Run the authentication flow:** The first time you run the application, you will need to authenticate with Google. The application will print a URL to the console. Open this URL in your browser, authorize the application, and the application will create a `token.json` file in the `server/` directory. This file will be used for subsequent requests.

**Note:** The `token.json` file contains sensitive information and should not be committed to version control.

### 4. Run the Application

With Docker and Docker Compose installed, you can build and run the application with a single command:

```bash
docker-compose up --build -d
```

The server will be available at `http://localhost:8000`.

## API Endpoints

### `POST /gemini`

Accepts a JSON body with a `message` field containing natural language text. The server processes this text to extract and create tasks, events, notes, and shopping lists.

**Headers:**
- `x-auth`: Your secret auth token.

**Body:**
```json
{
    "message": "Remind me to buy milk tomorrow and schedule a meeting with John for Friday at 2pm."
}
```

### `POST /audio-input`

Accepts a `3gpp` audio file as the raw request body. The server transcribes the audio using Gemini, saves the transcription to Notion, and then processes the transcription text in the same way as the `/gemini` endpoint.

**Headers:**
- `x-auth`: Your secret auth token.
- `Content-Type`: `audio/3gpp`
