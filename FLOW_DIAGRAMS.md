# 📊 Diagramas de Flujo - TurnoAI

## Flujo General de Procesamiento de Mensajes

```
┌─────────────────────────────────────────────────────────────────┐
│                     USUARIO WHATSAPP                             │
│              "Agendar cita mañana a las 3pm"                     │
└─────────────┬───────────────────────────────────────────────────┘
              │
              ├─→ Twilio recibe el mensaje
              │
              ├─→ POST /webhook en FastAPI
              │   From: whatsapp:+57300...
              │   Body: "agendar cita mañana a las 3pm"
              │
              ├─→ DateTime Normalizer enriquece
              │   [fecha_detectada: 2026-03-24]
              │   [hora_detectada: 15:00]
              │   [timezone: America/Bogota]
              │
              ├─→ Agent Executor (LangGraph/LangChain)
              │   ├─ Analiza intención: CREAR_CITA
              │   ├─ Extrae parámetros:
              │   │  - titulo: "Cita"
              │   │  - fecha: 2026-03-24
              │   │  - hora: 15:00
              │   │
              │   ├─→ Tool: buscar_disponibilidad()
              │   │   ├─ MCP Client HTTP → Google Calendar
              │   │   └─ Respuesta: "Disponible ✅"
              │   │
              │   ├─→ Tool: crear_evento()
              │   │   ├─ MCP Client HTTP → Google Calendar
              │   │   └─ Respuesta: event_id creado ✅
              │   │
              │   └─ Genera respuesta:
              │      "✅ Cita agendada para mañana a las 3pm"
              │
              ├─→ send_whatsapp_message()
              │   Twilio API
              │
              └─→ Usuario recibe respuesta en WhatsApp
```

## Tipos de Solicitudes del Agente

### 1. 📅 Crear Cita - "Agendar corte mañana a las 3pm"

```
                  Mensaje del usuario
                         │
                         ▼
                 Enriquecimiento (DateTime)
                  [fecha: 2026-03-24]
                  [hora: 15:00]
                         │
                         ▼
              Agent analiza: CREAR_CITA
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
    Buscar disponib.  Extraer título  Validar hora
    para ese horario  de la solicitud  (no en pasado)
          │              │              │
          └──────────────┼──────────────┘
                         ▼
                 ¿Disponible?
                    │
         ┌──────────┴──────────┐
         ▼                     ▼
        SÍ                     NO
         │                     │
         ▼                     ▼
    Crear evento        Sugerir otro
    en Calendar         horario
         │              (buscar disponibilidad)
         ▼              │
    ✅ Confirmación     ▼
         │         ¿Aceptar otro?
         └────────→ SÍ/NO
                     │
                     └─→ Responder al usuario
```

### 2. 🔍 Buscar Citas - "¿Qué tengo mañana?"

```
              "¿Qué tengo mañana?"
                     │
                     ▼
          Enrich: [fecha: 2026-03-24]
                     │
                     ▼
         Agent: BUSCAR_CITAS
                     │
                     ▼
         buscar_citas(2026-03-24)
                     │
                     ▼
         Google Calendar (via MCP)
                     │
      ┌─────────────┴─────────────┐
      ▼                           ▼
   ¿Citas encontradas?      Sin citas
      │                           │
      ▼                           ▼
   Formatear lista          "No tienes citas
   - 10:00 Corte             para mañana"
   - 2:00 Manicure
      │
      ▼
   Enviar al usuario
```

### 3. 🗑️ Cancelar Cita - "Cancela mi cita de barbería"

```
         "Cancela mi cita de barbería"
                     │
                     ▼
    Agent: CANCELAR_CITA
                     │
         ┌───────────┼───────────┐
         ▼           ▼           ▼
    Opción 1:  Opción 2:   Opción 3:
    Buscar por Buscar evento Buscar en
    palabra     reciente      última respuesta
    "barbería"  mencionado    del agente
         │           │           │
         └───────────┼───────────┘
                     ▼
         ¿Evento encontrado?
                  │
        ┌─────────┴──────────┐
        ▼                    ▼
       SÍ                    NO
        │                    │
        ▼                    ▼
   Confirmar          Pedir al usuario:
   cancelación         "¿Cuál cita
        │              deseas cancelar?"
        ▼                   │
   ✅ cancelar_evento()     ▼
        │               Esperar respuesta
        ▼
   "✅ Cita cancelada"
```

### 4. ✏️ Actualizar Cita - "Mueve mi cita a las 4pm"

```
         "Mueve mi cita de mañana a las 4pm"
                     │
                     ▼
         Agent: ACTUALIZAR_CITA
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
    Encontrar evento        Validar nueva hora
    con palabra "cita"       - No en pasado
    o fecha "mañana"         - Disponible
         │                       │
         └───────────┬───────────┘
                     ▼
            ¿Evento + hora válida?
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
       SÍ                         NO
        │                         │
        ▼                         ▼
   Validar              Buscar disponibilidad
   disponibilidad       alternativa
   nuevo horario             │
        │                    ▼
        ▼                Sugerir otro horario
    ¿Disponible?
        │
    ┌───┴───┐
    ▼       ▼
   SÍ      NO
    │       │
    ▼       ▼
  Actualizar Rechazar
  evento     solicitud
    │           │
    ▼           ▼
  Confirmación  "No está disponible
        │       ese horario"
        └──────→ Responder
```

## Flujo de Thread Memory (Memoria de Conversación)

```
Usuario 1 (whatsapp:+573001234567)
│
├─ Mensaje 1: "Agendar cita mañana"
│  └─ Thread: whatsapp:+573001234567
│     └─ Memory: user_id, last_event_id, context
│
├─ Mensaje 2: "A qué hora?"
│  └─ Thread: whatsapp:+573001234567
│     └─ Memory: Accede a contexto anterior
│        └─ Puede referirse a: "mi cita de mañana"
│
└─ Mensaje 3: "Cancelala"
   └─ Thread: whatsapp:+573001234567
      └─ Memory: Accede a last_event_id
         └─ Cancela la cita creada en Mensaje 1

Usuario 2 (whatsapp:+573009876543)
│
└─ Mensaje 1: "Muestra mis citas"
   └─ Thread: whatsapp:+573009876543
      └─ Memory: Independiente del Usuario 1
         └─ No tiene historial de mensajes anteriores
```

## Flujo de Errores y Manejo

```
          Mensaje recibido
                │
                ▼
    ¿Mensaje válido?
       │
    ┌──┴──┐
    ▼     ▼
   SÍ    NO
    │     │
    │     ▼
    │   Responder:
    │   "No entiendo.
    │    Por favor intenta
    │    de nuevo"
    │
    ▼
Enriquecer mensaje
    │
    ▼
Agent ejecuta
    │
    ┌──────────────┬──────────────┐
    ▼              ▼              ▼
Éxito         Error MCP      Error OpenAI
    │              │              │
    ▼              ▼              ▼
Respuesta    "No puedo      "El asistente
normal       conectar con   no está
    │        el calendario" disponible"
    │              │              │
    └──────────────┼──────────────┘
                   ▼
            Usuario recibe
            mensaje de error
```

## Arquitectura de Componentes

```
┌────────────────────────────────────────────────────────┐
│                    TURNOAI (FastAPI)                   │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ┌─────────────────────────────────────────────────┐ │
│  │  main.py                                        │ │
│  │  - FastAPI app                                  │ │
│  │  - Lifespan (inicia agente)                     │ │
│  │  - POST /webhook (recibe WhatsApp)              │ │
│  │  - send_whatsapp_message()                      │ │
│  └──────────────────────────┬──────────────────────┘ │
│                             │                         │
│  ┌──────────────────────────▼──────────────────────┐ │
│  │  services/datetime_normalizer.py               │ │
│  │  - normalize_datetime()                         │ │
│  │  - enrich_user_message()                        │ │
│  │  - Detecta: fecha, hora, timezone               │ │
│  └──────────────────────────┬──────────────────────┘ │
│                             │                         │
│  ┌──────────────────────────▼──────────────────────┐ │
│  │  services/agent_service.py                     │ │
│  │  - create_executer_agent()                      │ │
│  │  - Tools:                                        │ │
│  │    ├─ buscar_disponibilidad()                   │ │
│  │    ├─ crear_evento()                            │ │
│  │    ├─ buscar_eventos_por_texto_tool()           │ │
│  │    ├─ actualizar_evento()                       │ │
│  │    └─ cancelar_evento()                         │ │
│  └──────────────────────────┬──────────────────────┘ │
│                             │                         │
│  ┌──────────────────────────▼──────────────────────┐ │
│  │  services/calendar_service.py                  │ │
│  │  - Comunicación con MCP Server                  │ │
│  │  - HTTP Client (streamable_http_client)         │ │
│  │  - JSON-RPC calls a Google Calendar             │ │
│  └──────────────────────────┬──────────────────────┘ │
│                             │                         │
│  ┌──────────────────────────▼──────────────────────┐ │
│  │  prompts/initial_prompt.py                     │ │
│  │  - System prompt del agente                     │ │
│  │  - Instrucciones y reglas                       │ │
│  │  - Fecha/hora actual y timezone                 │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  ┌────────────────────────────────────────────────┐  │
│  │  LangGraph/LangChain Stack                      │  │
│  │  - ReAct Agent (Reasoning + Acting)             │  │
│  │  - Memory Saver (thread-based)                  │  │
│  │  - OpenAI ChatModel                             │  │
│  └────────────────────────────────────────────────┘  │
│                                                        │
└────────────────────────────────────────────────────────┘
```

## Ciclo de Vida de la Aplicación

```
┌──────────────────────────┐
│  Iniciar uvicorn main:app│
└────────┬─────────────────┘
         │
         ▼
    ┌─────────────┐
    │ Lifespan    │ (contextmanager)
    │ (startup)   │
    └─────┬───────┘
          │
          ▼
    ┌─────────────────────────────────────┐
    │ load_dotenv()                       │
    │ - Lee .env                          │
    │ - Carga variables de entorno        │
    └─────├───────────────────────────────┘
          │
          ▼
    ┌─────────────────────────────────────┐
    │ Inicializar Twilio Client           │
    │ - Si USE_TWILIO_FAKE=false:         │
    │   Crear Client(account_sid, token)  │
    │ - Si USE_TWILIO_FAKE=true:          │
    │   twilio_client = None              │
    └─────├───────────────────────────────┘
          │
          ▼
    ┌─────────────────────────────────────┐
    │ create_executer_agent()             │
    │ - Crea LLM (ChatOpenAI)             │
    │ - Registra tools                    │
    │ - Crea ReAct Agent                  │
    │ - Inicializa MemorySaver            │
    └─────├───────────────────────────────┘
          │
          ▼
    ✅ APP LISTA PARA RECIBIR MENSAJES


    ┌─────────────────────────────────────┐
    │ POST /webhook (loop principal)      │
    │ Mientras FastAPI está corriendo ... │
    └─────└───────────────────────────────┘


    ┌──────────────────────────┐
    │ Detener FastAPI server   │
    └────────┬─────────────────┘
             │
             ▼
    ┌─────────────┐
    │ Lifespan    │ (cleanup)
    │ (shutdown)  │
    └─────┬───────┘
          │
          ▼
    ✅ Aplicación cerrada correctamente.
```

---

Estos diagramas te ayudarán a entender cómo se comporta TurnoAI en diferentes escenarios y cuál es el flujo de datos a través del sistema.
