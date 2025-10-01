from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
import httpx
import traceback
import os
from dotenv import load_dotenv

load_dotenv()

MCP_SERVER_URL = os.getenv("CALENDAR_MCP_SERVER_URL")

TIMEOUT_CONFIG = httpx.Timeout(30.0, connect=5.0)


async def crear_cita_en_calendario(cita: any) -> dict | None:
    """
    Se conecta al servidor MCP remoto y llama a la herramienta 'create-event'.
    """
    try:
        # 1. Establecer la conexión usando el transporte HTTP
        async with streamablehttp_client(MCP_SERVER_URL, client_options={'timeout': TIMEOUT_CONFIG}) as (read_stream, write_stream, _):

            # 2. Iniciar una sesión de cliente MCP sobre esa conexión
            async with ClientSession(read_stream, write_stream) as session:

                await session.initialize()

                argumentos = {
                    "summary": cita.titulo,
                    "start": cita.inicio,
                    "end": cita.fin,
                    "attendees": [str(email) for email in cita.asistentes]
                }

                # 3. Llamar a la herramienta remota
                resultado = await session.call_tool("create-event", arguments=argumentos)

                # 4. Procesar el resultado...
                if resultado.isError:
                    return None

                return resultado.structuredContent

    except httpx.TimeoutException as e:
        # Es buena práctica capturar el error de timeout específicamente
        print(
            f"ERROR: La conexión con el servidor MCP excedió el tiempo de espera (timeout): {e}")
        return None

    except Exception as e:
        # Captura cualquier otro error
        print(f"Error crítico al conectar o llamar al servidor MCP: {e}")
        traceback.print_exc()
        return None

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
        async with streamablehttp_client(MCP_SERVER_URL) as (read_stream, write_stream, _):

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
