# main.py
import asyncio
from fastapi import FastAPI, Form, Request
from twilio.twiml.messaging_response import MessagingResponse
import os
from twilio.rest import Client
from dotenv import load_dotenv
from services.calendar_service import list_calendar_events
from fastapi.responses import PlainTextResponse


load_dotenv()

app = FastAPI()

# inicializar cliente
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_client = Client(account_sid, auth_token)


def send_whatsapp_message(to: str, body: str):
    from_whatsapp = os.getenv("TWILIO_WHATSAPP_NUMBER")
    message = twilio_client.messages.create(
        body=body,
        from_=from_whatsapp,
        to=to
    )
    return message.sid


# Endpoint para recibir mensajes de WhatsApp
@app.post("/webhook")
async def whatsapp_webhook(
    Body: str = Form(...),
    From: str = Form(...)
):

    incoming_msg = Body.lower()
    sender = From  # será algo como "whatsapp:+57300..."

    print(f"Recibido de {sender}: {incoming_msg}")

    # Puedes decidir si responder vía TwiML o enviar proactivamente
    resp = MessagingResponse()

    if "eventos" in incoming_msg:
        events = await list_calendar_events(
            '2025-09-25T00:00:00-05:00',
            '2025-10-10T00:00:00-05:00'
        )

        print("DEBUG - events:", events)

        if events and hasattr(events, "content") and events.content:
            texto_eventos = events.content[0].text
            send_whatsapp_message(
                sender, f"Tus próximos eventos:\n{texto_eventos}")

        else:
            send_whatsapp_message(
                sender, f"No encontré eventos en tu calendario.")

    elif "saludo" in incoming_msg:
        send_whatsapp_message(sender, "¡Hola! Soy TurnoAI 😊")
    else:
        send_whatsapp_message(sender,
                              "No entendí tu mensaje. Escribe 'eventos' para ver tu calendario.")

    # Twilio espera un string XML (TwiML)
    return PlainTextResponse(str(resp), media_type="application/xml")


# Endpoint de prueba
@app.get("/")
def read_root():
    return {"message": "TurnoAI API funcionando"}
