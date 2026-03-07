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
    - 3pm / 15:00
    """

    tz = ZoneInfo(DEFAULT_TZ)
    now = datetime.now(tz)

    normalized_date = None
    normalized_time = None

    text_lower = text.lower()

    # Detectar fecha relativa
    if "pasado mañana" in text_lower:
        normalized_date = (now + timedelta(days=2)).date()

    elif "mañana" in text_lower:
        normalized_date = (now + timedelta(days=1)).date()

    elif "hoy" in text_lower:
        normalized_date = now.date()

    # Detectar hora tipo 3pm
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

    return text + "\n" + "\n".join(extra)
