# services/datetime_normalizer.py
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import re

DEFAULT_TZ = "America/Bogota"


def normalize_datetime(text: str):
    """
    Detecta expresiones simples como:
    - mañana
    - hoy
    - pasado mañana
    - 3pm / 15:00 / 630pm

    IMPORTANTE: Si se detecta hora pero NO se detecta fecha explícita,
    asume que es para "hoy"
    """

    tz = ZoneInfo(DEFAULT_TZ)
    now = datetime.now(tz)

    normalized_date = None
    normalized_time = None
    has_explicit_date = False

    text_lower = text.lower()

    # Detectar fecha relativa
    if "pasado mañana" in text_lower:
        normalized_date = (now + timedelta(days=2)).date()
        has_explicit_date = True

    elif "mañana" in text_lower:
        normalized_date = (now + timedelta(days=1)).date()
        has_explicit_date = True

    elif "hoy" in text_lower:
        normalized_date = now.date()
        has_explicit_date = True

    # Detectar hora tipo 3pm, 3:30pm, 630pm, etc.
    time_match = re.search(r"(\d{1,2})(?::(\d{2}))?\s?(am|pm)", text_lower)

    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2) or 0)
        period = time_match.group(3)

        if period == "pm" and hour != 12:
            hour += 12
        if period == "am" and hour == 12:
            hour = 0

        normalized_time = f"{hour:02d}:{minute:02d}"

        # SI SE DETECTÓ HORA PERO NO HAY FECHA EXPLÍCITA, ASUMIR "HOY"
        if normalized_time and not has_explicit_date:
            normalized_date = now.date()

    return {
        "original": text,
        "normalized_date": str(normalized_date) if normalized_date else None,
        "normalized_time": normalized_time,
        "timezone": DEFAULT_TZ
    }


def enrich_user_message(text: str):
    data = normalize_datetime(text)

    extra = []

    if data["normalized_date"]:
        extra.append(f"[fecha_detectada: {data['normalized_date']}]")

    if data["normalized_time"]:
        extra.append(f"[hora_detectada: {data['normalized_time']}]")

    extra.append(f"[timezone: {data['timezone']}]")

    # Detectar palabras clave que puedan referenciarse al último evento
    # Esto ayuda al agente a buscar en el historial
    keywords = []
    text_lower = text.lower()

    # Detectar referencias PRONOMINALES (verbo + pronombre enclítico)
    # Ejemplos: "reagendala", "eliminala", "muévela", "cambiala", "actualizala"
    pronominal_patterns = [
        # reagendala, reagendalo
        r"(reagenda|reagendar|reschedule)(?:la|lo|me)\b",
        r"(elimina|cancel|cancela|borra|quita)(?:la|lo)\b",  # eliminala, cancelalo
        r"(mueve|move)(?:la|lo)\b",  # muévela
        r"(cambia|modify|edita|modifica)(?:la|lo)\b",  # cambiala
        r"(actualiza)(?:la|lo)\b",  # actualizala
        # verbo + pronombre
        r"(reagendar|reschedule|move|cambiar|update|actualizar)(?:la|lo)(?:\s|$)",
    ]

    is_pronominal_reference = False
    for pattern in pronominal_patterns:
        if re.search(pattern, text_lower):
            is_pronominal_reference = True
            keywords = ["PRONOUN_REFERENCE"]  # Marcador especial
            break

    # Si NO es referencia pronominal, busca palabras clave específicas
    if not is_pronominal_reference:
        # Palabras que típicamente referencian a un evento anterior
        reference_patterns = [
            # elimina [la] cita/evento/profe
            r"(?:elimina|cancela|borra|quita|remove)\s+(?:la|el|lo)?\s*(\w+)",
            # actualiza [la] cita
            r"(?:actualiza|modifica|cambia|edita|mueve)\s+(?:la|el|lo)?\s*(\w+)",
            # qué tengo en [la profe]
            r"(?:cuéntame|dime|cuál|qué)\s+(?:tengo|hay)\s+(?:en|de)\s+(\w+)",
        ]

        for pattern in reference_patterns:
            match = re.search(pattern, text_lower)
            if match:
                keyword = match.group(1)
                # Filtrar palabras muy cortas o genéricas
                if len(keyword) > 2 and keyword not in ["la", "el", "lo", "que"]:
                    keywords.append(keyword)

    # Si hay palabras clave detectadas, ayuda al agente a buscar
    if keywords:
        if keywords == ["PRONOUN_REFERENCE"]:
            # Marcador para que el agente sepa que se refiere al último evento
            extra.append("[referencia_pronominal: true]")
        else:
            extra.append(f"[buscar_en_contexto: {', '.join(keywords)}]")

    return text + "\n" + "\n".join(extra)
