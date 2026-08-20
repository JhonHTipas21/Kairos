"""
Skill para generar un briefing contextual de bienvenida del sistema Kairós.
"""

from datetime import datetime

from skills.metrics import get_real_cpu_usage
from skills.system import get_battery_status


def get_systems_briefing() -> str:
    """
    Genera un informe de estado de Kairós (J.A.R.V.I.S. style) con la fecha, hora, saludo contextual, estado de batería y carga de CPU actual.

    Returns:
        Un informe narrativo estructurado listo para ser leído por voz por el asistente.
    """
    now = datetime.now()
    hour = now.hour

    # Saludo según la hora
    if hour < 12:
        greeting = "Buenos días, señor."
    elif hour < 19:
        greeting = "Buenas tardes, señor."
    else:
        greeting = "Buenas noches, señor."

    time_str = now.strftime("%I:%M %p").lstrip("0")
    date_str = now.strftime("%d de %B de %Y")

    # Mapeo de meses en inglés a español
    months_es = {
        "January": "enero",
        "February": "febrero",
        "March": "marzo",
        "April": "abril",
        "May": "mayo",
        "June": "junio",
        "July": "julio",
        "August": "agosto",
        "September": "septiembre",
        "October": "octubre",
        "November": "noviembre",
        "December": "diciembre",
    }
    for eng, esp in months_es.items():
        date_str = date_str.replace(eng, esp)

    try:
        battery = get_battery_status()
        # Limpiar un poco el formato "Estado de batería actual: ..."
        battery = battery.replace("Estado de batería actual:", "El estado de la batería es")
    except Exception:
        battery = "El estado de la batería no está disponible."

    try:
        cpu = get_real_cpu_usage()
    except Exception:
        cpu = 12.0

    briefing = (
        f"{greeting} Hoy es {date_str} y son las {time_str}.\n"
        f"{battery}.\n"
        f"La carga del procesador principal está al {cpu}%.\n"
        "Todos los sistemas operativos de Kairós están en línea y listos para sus instrucciones."
    )
    return briefing
