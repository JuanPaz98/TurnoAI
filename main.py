# main.py
from fastapi import FastAPI, Form, Request
from twilio.twiml.messaging_response import MessagingResponse
import os
from twilio.rest import Client
from dotenv import load_dotenv

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

    incoming_msg = Body
    sender = From  # será algo como "whatsapp:+57300..."

    print(f"Recibido de {sender}: {incoming_msg}")

    # Puedes decidir si responder vía TwiML o enviar proactivamente
    resp = MessagingResponse()
    resp.message("Estoy procesando tu mensaje...")

    # Luego, como ejemplo, envía otro mensaje personalizado
    sid = send_whatsapp_message(
        sender, f"Hola de parte de TurnoAI, recibí: {incoming_msg}")

    print("Mensaje enviado con SID:", sid)

    return str(resp)


# Endpoint de prueba
@app.get("/")
def read_root():
    return {"message": "TurnoAI API funcionando"}
