# app/api/routes/whatsapp.py

from fastapi import APIRouter, Request, Response
from twilio.twiml.messaging_response import MessagingResponse
from app.api.v1.chatbot_api import ask_gemini, PromptRequest  # import class & fungsi

router = APIRouter()

@router.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    form = await request.form()
    user_message = form.get("Body")
    sender = form.get("From")

    # Konversi pesan ke format PromptRequest
    prompt_request = PromptRequest(prompt=user_message)

    # Dapatkan respons dari AI chatbot
    result = ask_gemini(prompt_request)
    reply = result.get("response", "Maaf, tidak bisa merespons saat ini.")

    response = MessagingResponse()
    response.message(reply)

    return Response(content=str(response), media_type="application/xml")
