# main.py
from fastapi import FastAPI, Form
from twilio.twiml.messaging_response import MessagingResponse
import os
from twilio.rest import Client
from dotenv import load_dotenv
from fastapi.responses import PlainTextResponse
from contextlib import asynccontextmanager
from pydantic import BaseModel
from services.agent_service import create_executer_agent
from services.datetime_normalizer import enrich_user_message

load_dotenv()

# Variable global para mantener el ejecutor del agente
agent_executor = None

# Detectar si usar Twilio fake o real
USE_TWILIO_FAKE = os.getenv("USE_TWILIO_FAKE", "False").lower() == "true"

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

# Inicializar Twilio solo si no es fake
if not USE_TWILIO_FAKE:
    twilio_client = Client(account_sid, auth_token)
else:
    twilio_client = None
    print("⚠️  Modo TWILIO FAKE habilitado - No se enviarán mensajes reales")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Al iniciar la aplicación, crea una única instancia del agente
    print("Iniciando la aplicación y creando el agente de IA...")
    global agent_executor
    agent_executor = await create_executer_agent()
    yield
    # Limpieza al cerrar la aplicación (si es necesario)
    print("Cerrando la aplicación.")

app = FastAPI(lifespan=lifespan)


class AgentQuery(BaseModel):
    query: str
    thread_id: str  # Para mantener la memoria de la conversación


def send_whatsapp_message_fake(to: str, body: str):
    """Simula envío de WhatsApp sin usar Twilio (para testing)"""
    print(f"\n📱 [FAKE TWILIO] Mensaje a {to}:")
    print(f"   {body}")
    print()
    return "fake-message-id-123"


def send_whatsapp_message_real(to: str, body: str):
    """Envía mensaje real por Twilio"""
    from_whatsapp = os.getenv("TWILIO_WHATSAPP_NUMBER")
    message = twilio_client.messages.create(
        body=body,
        from_=from_whatsapp,
        to=to
    )
    return message.sid


def send_whatsapp_message(to: str, body: str):
    """Envía mensaje por WhatsApp (real o fake según configuración)"""
    if USE_TWILIO_FAKE:
        return send_whatsapp_message_fake(to, body)
    else:
        return send_whatsapp_message_real(to, body)


# Endpoint para recibir mensajes de WhatsApp
@app.post("/webhook")
async def whatsapp_webhook(
    Body: str = Form(...),
    From: str = Form(...)
):

    incoming_msg = enrich_user_message(Body.lower())
    sender = From  # será algo como "whatsapp:+57300..."

    print(f"Recibido de {sender}: {incoming_msg}")

    if not agent_executor:
        send_whatsapp_message(
            sender, "Lo siento, el asistente de IA no está disponible en este momento. Inténtalo de nuevo más tarde.")
        return PlainTextResponse(str(MessagingResponse()), media_type="application/xml")

    # Pasamos el input directamente al agente
    try:
        response = await agent_executor.ainvoke(
            {"messages": [incoming_msg]},
            {"configurable": {"thread_id": sender}}
        )

        print("DEBUG - Respuesta del agente:", response)

        send_whatsapp_message(sender, response["messages"][-1].content)

    except Exception as e:
        print(f"Error en el agente: {e}")
        send_whatsapp_message(
            sender, "Ocurrió un error al procesar tu mensaje.")

    # Twilio espera un string XML (aunque ya respondimos proactivamente)
    return PlainTextResponse(str(MessagingResponse()), media_type="application/xml")


# Endpoint de prueba
@app.get("/")
def read_root():
    return {"message": "TurnoAI API funcionando"}
