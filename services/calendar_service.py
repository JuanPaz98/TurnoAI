from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
import httpx
import traceback
import os
from dotenv import load_dotenv

load_dotenv()

MCP_SERVER_URL = os.getenv("CALENDAR_MCP_SERVER_URL")

TIMEOUT_CONFIG = httpx.Timeout(30.0, connect=5.0)


async def crear_cita_en_calendario(cita: any):
    try:
        async with streamable_http_client(MCP_SERVER_URL) as (read_stream, write_stream, _):

            async with ClientSession(read_stream, write_stream) as session:

                await session.initialize()

                # Detectar formato de fechas - manejo flexible
                if "fecha_inicio" in cita and "fecha_fin" in cita:
                    # Formato: ISO datetime strings (2026-03-08T15:00:00)
                    start = cita["fecha_inicio"]
                    end = cita["fecha_fin"]
                elif "fecha" in cita and "hora_inicio" in cita:
                    # Formato: fecha separada + horas
                    start = f'{cita["fecha"]}T{cita["hora_inicio"]}:00'
                    end = f'{cita["fecha"]}T{cita["hora_fin"]}:00'
                else:
                    raise ValueError(
                        "Formato de fechas no reconocido. Debe incluir fecha_inicio/fecha_fin o fecha/hora_inicio/hora_fin")

                attendees = []
                if "invitados" in cita:
                    attendees = [{"email": email}
                                 for email in cita["invitados"]]

                # Agregar calendarId (requerido por MCP)
                argumentos = {
                    "calendarId": "primary",  # ← IMPORTANTE: Agregado
                    "summary": cita["titulo"],
                    "start": start,
                    "end": end,
                    "attendees": attendees
                }

                print("DEBUG - argumentos enviados al MCP:", argumentos)

                resultado = await session.call_tool(
                    "create-event",
                    arguments=argumentos
                )

                if resultado.isError:
                    raise Exception("Error creando evento")

                return {
                    "status": "✅ *Cita agendada con éxito*",
                    "mensaje": f" 📅 '{cita['titulo']}' creado exitosamente para {start}",
                    "detalles": {
                        "titulo": cita["titulo"],
                        "inicio": start,
                        "fin": end
                    }
                }

    except Exception as e:
        print("ERROR calendario:", e)
        raise e

# --- Función para listar eventos del calendario a través de MCP ---


async def list_calendar_events(fecha_inicio: str, fecha_fin: str) -> list | None:
    """
    Se conecta al servidor MCP y llama a la herramienta 'list-events' 
    para obtener los eventos en un rango de fechas.
    Retorna una lista con el contenido estructurado de los eventos o None si hay error.

    Args:
        fecha_inicio (str): Fecha y hora de inicio en formato ISO (ej: "2024-08-01T00:00:00-05:00")
        fecha_fin (str): Fecha y hora de fin en formato ISO (ej: "2024-08-31T23:59:59-05:00")
    """
    try:
        # 1. Conexión con el servidor usando el transporte HTTP
        async with streamable_http_client(MCP_SERVER_URL) as (read_stream, write_stream, _):

            # 2. Iniciar sesión de cliente MCP
            async with ClientSession(read_stream, write_stream) as session:

                await session.initialize()

                # 3. Preparar los argumentos para la herramienta 'list-events'
                # Los nombres de los argumentos (ej. "start", "end") deben coincidir
                # con los que espera tu servidor MCP de Google Calendar.
                arguments = {
                    "calendarId": "primary",
                    "start": fecha_inicio,
                    "end": fecha_fin
                }

                print(
                    f"Llamando a la herramienta 'list-events' con: {arguments}")
                result = await session.call_tool("list-events", arguments=arguments)

                # 4. Procesar el result
                if result.isError:
                    error_msg = getattr(
                        result.content, 'text', 'Error desconocido') if result.content else 'Error desconocido'
                    print(
                        f"La herramienta 'list-events' retornó un error: {error_msg}")
                    return None

                return result

    except Exception as e:
        print(f"Error crítico al conectar o llamar al servidor MCP: {e}")
        traceback.print_exc()
        return None
