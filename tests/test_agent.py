"""
Test para el agente de calendario sin usar Twilio.
Simula requests de Twilio y prueba el agente con MCP real.
"""

from services.datetime_normalizer import enrich_user_message
from services.agent_service import create_executer_agent
import asyncio
import sys
from pathlib import Path

# Agregar la raíz del proyecto al path PRIMERO
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class WhatsAppSimulator:
    """Simula mensajes de WhatsApp para testear el agente"""

    def __init__(self):
        self.agent = None
        self.thread_id = "test-thread-001"

    async def initialize(self):
        """Inicializa el agente una sola vez"""
        print("\n[*] Inicializando agente...")
        self.agent = await create_executer_agent()
        print("[OK] Agente inicializado correctamente\n")

    async def send_message(self, message: str, sender: str = "whatsapp:+573165808886"):
        """
        Simula envío de mensaje de WhatsApp y obtiene respuesta del agente.

        Args:
            message: El mensaje del usuario
            sender: El número de WhatsApp (simulado)
        """
        # Enriquecer el mensaje con fechas detectadas (igual que en main.py)
        enriched_message = enrich_user_message(message.lower())

        print(f"\n{'='*60}")
        print(f"[MSG] Mensaje de {sender}:")
        print(f"   {enriched_message}")
        print(f"{'='*60}")

        try:
            # Ejecutar el agente con el mensaje enriquecido usando ainvoke (async)
            response = await self.agent.ainvoke(
                {"messages": [enriched_message]},
                config={"configurable": {"thread_id": self.thread_id}}
            )

            # Extraer última respuesta del agente
            last_message = response["messages"][-1]

            if hasattr(last_message, 'content'):
                bot_response = last_message.content
            else:
                bot_response = str(last_message)

            print(f"\n[BOT] Respuesta del agente:")
            print(f"   {bot_response}")
            print()

            return bot_response

        except Exception as e:
            print(f"\n[ERROR] Error en el agente: {e}")
            import traceback
            traceback.print_exc()
            return None

            return bot_response

        except Exception as e:
            print(f"\n[ERROR] Error en el agente: {e}")
            import traceback
            traceback.print_exc()
            return None


async def run_interactive_chat():
    """Ejecuta un chat interactivo con el agente tipo WhatsApp"""

    simulator = WhatsAppSimulator()
    await simulator.initialize()

    print("\n" + "=" * 60)
    print("[CHAT INTERACTIVO]")
    print("Escribe 'exit' o 'salir' para terminar")
    print("=" * 60 + "\n")

    while True:
        try:
            # Obtener input del usuario
            user_input = input("[TU]: ").strip()

            # Salir si el usuario lo pide
            if user_input.lower() in ["exit", "salir", "quit"]:
                print("\n[SISTEMA] Cerrando chat...")
                break

            # Ignorar inputs vacíos
            if not user_input:
                continue

            # Enviar mensaje al agente
            await simulator.send_message(user_input)

        except KeyboardInterrupt:
            print("\n\n[SISTEMA] Chat interrumpido por el usuario")
            break
        except Exception as e:
            print(f"\n[ERROR] Error en el chat: {e}")
            continue


async def run_tests():
    """Ejecuta una serie de pruebas del agente"""

    simulator = WhatsAppSimulator()
    await simulator.initialize()

    # Test 1: Crear una cita
    print("\n" + "█" * 60)
    print("TEST 1: Crear una cita para corte de cabello")
    print("█" * 60)
    await simulator.send_message(
        "Agenda una cita para el proximo viernes a las 2pm, corte de cabello"
    )

    # Test 2: Buscar disponibilidad
    print("\n" + "█" * 60)
    print("TEST 2: Buscar disponibilidad")
    print("█" * 60)
    await simulator.send_message(
        "¿Tengo disponibilidad manana entre las 9am y 12pm?"
    )

    # Test 3: Ver citas del día
    print("\n" + "█" * 60)
    print("TEST 3: Ver citas de manana")
    print("█" * 60)
    await simulator.send_message(
        "¿Que tengo agendado para manana?"
    )

    # Test 4: Buscar cita específica
    print("\n" + "█" * 60)
    print("TEST 4: Buscar cita por nombre")
    print("█" * 60)
    await simulator.send_message(
        "Muestrame mis citas de corte de cabello"
    )

    # Test 5: Conversación natural
    print("\n" + "█" * 60)
    print("TEST 5: Conversacion natural sin contexto claro")
    print("█" * 60)
    await simulator.send_message(
        "Necesito agendar algo importante para el lunes"
    )


async def run_single_test(user_message: str):
    """Ejecuta una prueba individual con un mensaje personalizado"""

    simulator = WhatsAppSimulator()
    await simulator.initialize()

    print("\n" + "█" * 60)
    print("TEST PERSONALIZADO")
    print("█" * 60)
    await simulator.send_message(user_message)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Test del agente de calendario")
    parser.add_argument(
        "--message",
        type=str,
        help="Mensaje personalizado para probar (sin --test-suite)",
        default=None
    )
    parser.add_argument(
        "--test-suite",
        action="store_true",
        help="Ejecutar suite completa de pruebas",
        default=False
    )
    parser.add_argument(
        "--chat",
        action="store_true",
        help="Ejecutar modo chat interactivo (tipo WhatsApp)",
        default=False
    )

    args = parser.parse_args()

    if args.chat:
        # Chat interactivo
        asyncio.run(run_interactive_chat())
    elif args.message:
        # Test individualizado
        asyncio.run(run_single_test(args.message))
    elif args.test_suite or (not args.message):
        # Suite completa
        asyncio.run(run_tests())
