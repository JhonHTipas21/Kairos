"""
Skill para integrar el servicio de Google Calendar.
"""

from datetime import datetime, timezone

from googleapiclient.discovery import build

from skills.google_auth import get_google_credentials


def list_upcoming_events(max_results: int = 5) -> str:
    """
    Obtiene los próximos eventos programados en el calendario de Google del usuario.

    Args:
        max_results: Número máximo de eventos a recuperar (por defecto 5).

    Returns:
        Un informe de texto con los eventos encontrados o un mensaje explicativo si no hay eventos.
    """
    creds = get_google_credentials()
    if not creds:
        return "Error: No se encontraron credenciales de Google. Asegúrate de colocar el archivo 'credentials.json' en la raíz."

    try:
        service = build("calendar", "v3", credentials=creds)
        # Obtener el tiempo actual en formato ISO y UTC
        now = datetime.now(timezone.utc).isoformat()

        events_result = (
            service.events()
            .list(calendarId="primary", timeMin=now, maxResults=max_results, singleEvents=True, orderBy="startTime")
            .execute()
        )

        events = events_result.get("items", [])

        if not events:
            return "No tiene eventos programados próximamente en su Google Calendar, señor."

        report_lines = ["Próximos eventos en su Google Calendar:"]
        for idx, event in enumerate(events, 1):
            start = event["start"].get("dateTime", event["start"].get("date"))
            # Limpiar un poco la fecha ISO para mejor lectura
            try:
                dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
                formatted_time = dt.strftime("%d de %B, %I:%M %p")
            except Exception:
                formatted_time = start

            summary = event.get("summary", "Sin título")
            report_lines.append(f"{idx}. '{summary}' programado para el {formatted_time}.")

        return "\n".join(report_lines)
    except Exception as e:
        return f"Error al recuperar los eventos de Google Calendar: {str(e)}"


def create_calendar_event(summary: str, start_time_str: str, end_time_str: str, description: str = "") -> str:
    """
    Crea un nuevo evento en el calendario de Google.

    Args:
        summary: El título o asunto del evento (ej. 'Reunión de desarrollo').
        start_time_str: Fecha y hora de inicio en formato ISO (ej. '2026-08-21T10:00:00-05:00').
        end_time_str: Fecha y hora de finalización en formato ISO (ej. '2026-08-21T11:00:00-05:00').
        description: Detalles o notas adicionales del evento.

    Returns:
        Mensaje confirmando la creación exitosa del evento o describiendo el error.
    """
    creds = get_google_credentials()
    if not creds:
        return "Error: No se encontraron credenciales de Google. Asegúrate de colocar el archivo 'credentials.json' en la raíz."

    try:
        service = build("calendar", "v3", credentials=creds)

        event_body = {
            "summary": summary,
            "description": description,
            "start": {
                "dateTime": start_time_str,
                "timeZone": "America/Bogota",
            },
            "end": {
                "dateTime": end_time_str,
                "timeZone": "America/Bogota",
            },
        }

        event = service.events().insert(calendarId="primary", body=event_body).execute()
        return (
            f"Éxito: Se programó el evento '{summary}' correctamente en Google Calendar. Link: {event.get('htmlLink')}"
        )
    except Exception as e:
        return f"Error al crear el evento en Google Calendar: {str(e)}"
