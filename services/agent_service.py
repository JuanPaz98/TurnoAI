from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain.tools import tool

import os
from dotenv import load_dotenv

from services.calendar_service import crear_cita_en_calendario, list_calendar_events

load_dotenv()

# System Prompt del agente desde variables de entorno
SYSTEM_PROMPT = os.getenv("AGENT_SYSTEM_PROMPT")


@tool
async def buscar_disponibilidad(start: str, end: str):
    """
    Verifica si hay eventos en Google Calendar en un rango de fechas/horas.

    Args:
        start: Fecha y hora de inicio en formato ISO (ej: 2026-03-08T06:00:00)
        end: Fecha y hora de fin en formato ISO (ej: 2026-03-08T12:00:00)

    Returns:
        Dict con 'disponible' (bool) y lista de 'eventos' si están ocupados
    """
    return await list_calendar_events(start, end)


@tool
async def crear_evento(titulo: str, fecha_inicio: str, fecha_fin: str):
    """
    Crea un evento en Google Calendar.

    Args:
        titulo: Nombre o título del evento
        fecha_inicio: Fecha y hora de inicio en formato ISO (ej: 2026-03-08T15:00:00)
        fecha_fin: Fecha y hora de fin en formato ISO (ej: 2026-03-08T16:00:00)
    """
    cita = {
        "titulo": titulo,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin
    }

    return await crear_cita_en_calendario(cita)


async def load_mcp_tools():
    """Retorna las herramientas disponibles para el agente"""
    return [buscar_disponibilidad, crear_evento]


async def create_executer_agent():

    print("Cargando herramientas...")

    calendar_tools = await load_mcp_tools()

    print(f"Herramientas cargadas: {[tool.name for tool in calendar_tools]}")

    model = ChatOpenAI(
        model="gpt-4.1-mini",
        temperature=0
    )

    # Vincular el system prompt al modelo
    model_with_prompt = model.bind(system=SYSTEM_PROMPT)

    agente_executor = create_react_agent(
        model_with_prompt,
        tools=calendar_tools,
        checkpointer=MemorySaver()
    )

    return agente_executor
