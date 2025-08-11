import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
HEADERS = {
    "Content-Type": "application/json",
    "X-goog-api-key": API_KEY,
}

def ask_gemini_api(message: str) -> str:
    body = {
        "contents": [
            {
                "parts": [
                    {
                        "text": message
                    }
                ]
            }
        ]
    }

    response = requests.post(GEMINI_URL, headers=HEADERS, json=body)

    if response.status_code != 200:
        raise Exception(f"Gagal terhubung ke Gemini: {response.text}")

    try:
        result = response.json()
        reply = result['candidates'][0]['content']['parts'][0]['text']
        return reply
    except Exception:
        return "Tidak ada jawaban dari Gemini."
