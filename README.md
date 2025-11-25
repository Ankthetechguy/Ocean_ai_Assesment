# Prompt-Driven Email Productivity Agent (Streamlit + Gemini)

## Overview
Streamlit app that loads a mock inbox, allows editing prompt templates ("Prompt Brain"), runs Gemini to:

## Prerequisites
# Prompt-Driven Email Productivity Agent (Streamlit + Gemini)

## Overview
Streamlit app that loads a mock inbox and a small "prompt brain" to:
- Categorize emails
- Extract action items
- Generate draft replies
- Answer freeform queries per-email

The app can run in two modes:
- Real mode: uses `google-generativeai` and a Gemini API key (set `GEMINI_API_KEY`).
- Mock mode: set `GEMINI_MOCK=true` (or use the provided `.env.example`) to run locally without a key.

## Prerequisites
- Python 3.10+
- Install dependencies:

```powershell
pip install -r .\email-agent\requirements.txt
```

## Run (mock mode, recommended for local development)

1. Enable mock mode for the current terminal session:

```powershell
$env:GEMINI_MOCK = "true"
```

2. Run Streamlit:

```powershell
streamlit run .\email-agent\app.py
```

Open the URL printed by Streamlit (usually http://localhost:8501).

## Run with a real Gemini API key (recommended)

Important security note: do NOT paste API keys into chat, issue trackers, or public places. Keep keys in environment variables or a local `.env` file that is excluded from source control.

1. For the current PowerShell session (temporary):

```powershell
$env:GEMINI_API_KEY = "your_real_gemini_api_key_here"
streamlit run .\email-agent\app.py
```

2. To set the key persistently for your Windows user account (you'll need to open a new terminal after running):

```powershell
setx GEMINI_API_KEY "your_real_gemini_api_key_here"
```

3. Alternatively, create a local `.env` file in `email-agent/` with the following content (DO NOT commit this file):

```
GEMINI_API_KEY=your_real_gemini_api_key_here
GEMINI_MOCK=false
```

Then run Streamlit normally. The app uses `python-dotenv` to load `.env` files automatically.

If you want me to test connectivity from this environment I cannot accept keys via chat — instead set the environment variable yourself in the terminal you use to run Streamlit, then press the "Test Gemini connection" button in the app's sidebar to verify.

## Files of interest
- `app.py` — Streamlit UI
- `gemini_client.py` — Gemini client wrapper; supports mock mode and dotenv
- `data/` — sample inbox and prompt templates; processed outputs are written here

## Notes
- Keep real API keys out of source control. Use environment variables or a local `.env` file (don't commit it).
- If you want, I can add a `.gitignore` entry for `.env` or wire a UI toggle for mock mode.
