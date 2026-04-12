# 🚀 Guía Completa de Configuración - TurnoAI

Esta guía te ayudará a configurar TurnoAI completamente en tu máquina local.

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener:

- **Python 3.10 o superior** - [Descargar](https://www.python.org)
- **Git** - [Descargar](https://git-scm.com)
- **Cuenta de Google** con Google Calendar
- **Cuenta de Twilio** (gratuita) - [Crear en twilio.com](https://www.twilio.com)
- **OpenAI API Key** - [Obtener en platform.openai.com](https://platform.openai.com)
- **MCP Server de Google Calendar** ejecutándose localmente

---

## 1️⃣ Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/JuanPaz98/TurnoAI
cd TurnoAI
```

---

## 2️⃣ Paso 2: Configurar Entorno Python

### Crear Entorno Virtual

**Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Verificar que está activado

Al ejecutar `python --version` debería mostrar Python 3.10+

---

## 3️⃣ Paso 3: Instalar Dependencias

```bash
pip install -r requirements.txt
```

Esto instalará:

- FastAPI & Uvicorn
- LangChain & LangGraph
- Twilio SDK
- Google Auth
- MCP Client
- OpenAI
- Y todas las dependencias auxiliares

---

## 4️⃣ Paso 4: Obtener Credenciales de Twilio

### 4.1 Crear Cuenta en Twilio

1. Ve a [twilio.com](https://www.twilio.com)
2. Haz clic en "Sign Up"
3. Completa el registro (es tención de que el sandbox es gratuito)
4. Verifica tu email
5. Ve a [Twilio Console](https://console.twilio.com)

### 4.2 Obtener Account SID y Auth Token

1. En Twilio Console, vas a la sección de **Account**
2. Copiar:
   - **Account SID** (comienza con `AC`)
   - **Auth Token** (contraseña del account)
3. Guárdalos en un lugar seguro

### 4.3 Configurar WhatsApp Sandbox

1. En Twilio Console, ve a **Messaging > Services > WhatsApp**
2. Crea o selecciona un servicio de WhatsApp
3. En **Sandbox**, verás un número de WhatsApp Twilio (ej: `whatsapp:+14155552671`)
4. Copia este número - será tu `TWILIO_WHATSAPP_NUMBER`

### 4.4 Configurar Webhook (URL de Callback)

Para que Twilio sepa dónde enviar los mensajes:

#### Opción A: Desarrollo Local con Cloudflare Tunnel (Recomendado)

**¿Qué es Cloudflare Tunnel?** Un túnel seguro que expone tu servidor local en internet sin deployment.

1. Descargar Cloudflare CLI desde [developers.cloudflare.com](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/)
2. Instalar en tu sistema (Windows, macOS o Linux)
3. Autenticarse con tu cuenta Cloudflare:
   ```bash
   cloudflare tunnel login
   ```
4. Crear y ejecutar un túnel para el puerto 8000:
   ```bash
   cloudflare tunnel run mi-turnoai
   ```
5. Cloudflare mostrará:
   ```
   Tunnel running on https://mi-turnoai.cfargotunnel.com
   ```
6. Copia la URL `https://mi-turnoai.cfargotunnel.com`

7. En **Twilio Console > WhatsApp Sandbox > Inbound Message URL**, pega:
   ```
   https://mi-turnoai.cfargotunnel.com/webhook
   ```
8. Guarda los cambios

#### Opción B: Deployment en Production

Si tienes un servidor en internet (ej: Heroku, Railway), usa su URL:

```
https://mi-app.herokuapp.com/webhook
```

---

## 5️⃣ Paso 5: Obtener OpenAI API Key

1. Ve a [OpenAI Platform](https://platform.openai.com/account/api-keys)
2. Haz clic en "Create new secret key"
3. Copia la key (no podrás verla de nuevo)
4. Guárdala en el archivo `.env`

---

## 6️⃣ Paso 6: Configurar MCP Server de Google Calendar

El MCP Server es un servicio que actúa de intermediario entre tu aplicación y Google Calendar.

### ¿Qué es MCP?

**Model Context Protocol** - Un protocolo estándar para conectar aplicaciones con recursos externos de forma segura.

### Descargar e Instalar

1. Encuentra el repositorio del MCP Server de Google Calendar
2. Clona el repositorio:

   ```bash
   git clone https://github.com/JuanPaz98/google-calendar-mcp
   cd mcp-google-calendar
   ```

3. Instala dependencias:

   ```bash
   pip install -r requirements.txt
   ```

4. Configura credenciales de Google:
   - Ya debería have un `credentials.json` o instrucciones para obtenerlo
   - Sigue las instrucciones del repositorio del MCP Server

5. Inicia el servidor:
   ```bash
   python main.py
   # o
   uvicorn main:app --reload --port 8000
   ```

El servidor debe responder en `http://localhost:8000`

---

## 7️⃣ Paso 7: Configurar Variables de Entorno

### Crear archivo `.env`

1. En la raíz de TurnoAI, copy `.env-example` a `.env`:

   ```bash
   cp .env-example .env
   ```

2. Edita `.env` con tus valores reales:

```env
# ============================================================
# GOOGLE CALENDAR (MCP)
# ============================================================
CALENDAR_MCP_SERVER_URL=http://localhost:8000

# ============================================================
# TWILIO (WhatsApp)
# ============================================================
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155552671
USE_TWILIO_FAKE=false

# ============================================================
# OPENAI
# ============================================================
OPENAI_API_KEY=sk-your_openai_api_key_here

# ============================================================
# CONFIGURACIÓN
# ============================================================
TIMEZONE=America/Bogota
PORT=8000
DEBUG=true
```

### Valores por Tipo:

**Para Desarrollo (USE_TWILIO_FAKE=true):**

```env
CALENDAR_MCP_SERVER_URL=http://localhost:8000
OPENAI_API_KEY=sk-xxx
USE_TWILIO_FAKE=true
TIMEZONE=America/Bogota
```

**Para Testing Real (USE_TWILIO_FAKE=false):**

```env
CALENDAR_MCP_SERVER_URL=http://localhost:8000
TWILIO_ACCOUNT_SID=ACxxx
TWILIO_AUTH_TOKEN=xxx
TWILIO_WHATSAPP_NUMBER=whatsapp:+1415555xxxx
OPENAI_API_KEY=sk-xxx
USE_TWILIO_FAKE=false
TIMEZONE=America/Bogota
```

---

## 8️⃣ Paso 8: Ejecutar la Aplicación

### Terminal 1: MCP Server de Google Calendar

```bash
cd ~/path/to/mcp-google-calendar
python main.py
# Debería mostrar:
# INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Mantén esta terminal abierta.**

### Terminal 2: Cloudflare Tunnel (si es desarrollo local)

```bash
cloudflare tunnel run mi-turnoai
# Debería mostrar:
# Tunnel running on https://mi-turnoai.cfargotunnel.com
```

**Mantén esta terminal abierta.**

### Terminal 3: TurnoAI FastAPI Server

```bash
cd ~/path/to/TurnoAI
source .venv/Scripts/activate  # o .venv\Scripts\activate en Windows
uvicorn main:app --reload
# Debería mostrar:
# INFO:     Uvicorn running on http://127.0.0.1:8000
```

---

## 9️⃣ Paso 9: Probar la Aplicación

### Modo Fake (Sin Twilio Real)

1. Set `USE_TWILIO_FAKE=true` en `.env`
2. Ejecuta TurnoAI
3. Abre `http://localhost:8000/docs` (Swagger UI)
4. Usa el endpoint `/webhook` para simular:

```bash
curl -X POST "http://localhost:8000/webhook" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=whatsapp:%2B573001234567&Body=agendar%20cita%20mañana%20a%20las%203pm"
```

Deberías ver el mensaje en los logs:

```
Recibido de whatsapp:+573001234567: agendar cita mañana a las 3pm
📱 [FAKE TWILIO] Mensaje a whatsapp:+573001234567:
   ✅ Cita agendada con éxito
```

### Modo Real (Con Twilio)

1. Asegúrate de que ngrok está corriendo y la URL está en Twilio Console
2. Set `USE_TWILIO_FAKE=false` en `.env`
3. Agrega credenciales reales de Twilio
4. Envía un mensaje desde El número de WhatsApp que vinculaste con Twilio Sandbox
5. El mensaje debería llegar a tu app y responder en tiempo real

---

## 🔍 Debugging y Troubleshooting

### Error: "CALENDAR_MCP_SERVER_URL not found"

**Solución:**

```bash
# Verifica que .env existe y tiene la variable
cat .env

# Si no existe, crea uno:
cp .env-example .env

# Edita con tus valores
nano .env  # o vs code .env
```

### Error: "Connection refused" para MCP Server

**Verificar:**

1. ¿El MCP Server está ejecutándose?

   ```bash
   curl http://localhost:8000/health
   # Debería retornar 200 OK
   ```

2. ¿El puerto es correcto?
   - En `.env`: `CALENDAR_MCP_SERVER_URL=http://localhost:8000`
   - En MCP Server terminal: Debe mostrar `Uvicorn running on http://127.0.0.1:8000`

### Error: "TWILIO_ACCOUNT_SID not configured"

**Solución:**

- Si usas `USE_TWILIO_FAKE=true`: No necesitas credenciales de Twilio
- Si usas `USE_TWILIO_FAKE=false`: Añade credenciales reales en `.env`

### Los mensajes no se envían

**Checklist:**

1. ngrok está ejecutándose y la URL está en Twilio Console
2. FastAPI server está ejecutándose sin errores
3. `USE_TWILIO_FAKE=false` en `.env`
4. Credenciales de Twilio son correctas
5. Revisa los logs de FastAPI para errores

### Error: "No module named 'X'"

**Solución:**

```bash
# Asegúrate de que el entorno virtual está activado
source .venv/Scripts/activate

# Reinstala dependencias
pip install -r requirements.txt --force-reinstall
```

---

## 📊 Verificar Setup Completo

```bash
# 1. Verifica Python
python --version  # Debería ser 3.10+

# 2. Verifica que el venv está activado
which python  # Debería mostrar .venv/bin/python

# 3. Verifica dependencias
pip list | grep -E 'fastapi|langchain|twilio'

# 4. Verifica .env existe
ls -la .env

# 5. Verifica que MCP Server funciona
curl http://localhost:8000/health

# 6. Inicia la app
uvicorn main:app --reload
```

---

## 📞 Referencias Rápidas

| Recurso             | URL                                          |
| ------------------- | -------------------------------------------- |
| Twilio Console      | https://console.twilio.com                   |
| OpenAI API Keys     | https://platform.openai.com/account/api-keys |
| ngrok Download      | https://ngrok.com/download                   |
| FastAPI Docs        | http://localhost:8000/docs                   |
| Google Calendar API | https://developers.google.com/calendar       |

---

**¿Problemas?** Revisa los logs, asegúrate de que todos los servicios están corriendo, y verifica las variables de entorno.
