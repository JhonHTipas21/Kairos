"""
Skill para integrar el servicio de Gmail y permitir leer y enviar correos.
"""

import base64
from email.mime.text import MIMEText

from googleapiclient.discovery import build

from skills.google_auth import get_google_credentials


def list_unread_emails(max_results: int = 5) -> str:
    """
    Recupera los últimos correos no leídos en la cuenta de Gmail del usuario.

    Args:
        max_results: Cantidad máxima de correos a listar (por defecto 5).

    Returns:
        Un resumen de texto con los correos no leídos (remitente y asunto).
    """
    creds = get_google_credentials()
    if not creds:
        return "Error: No se encontraron credenciales de Google. Asegúrate de colocar el archivo 'credentials.json' en la raíz."

    try:
        service = build("gmail", "v1", credentials=creds)

        # Buscar mensajes no leídos
        results = service.users().messages().list(userId="me", q="is:unread", maxResults=max_results).execute()

        messages = results.get("messages", [])

        if not messages:
            return "No tiene correos no leídos en su bandeja de entrada, señor."

        report_lines = [f"Últimos {len(messages)} correos no leídos:"]

        for msg in messages:
            msg_id = msg["id"]
            # Obtener detalles del mensaje
            message = service.users().messages().get(userId="me", id=msg_id, format="metadata").execute()

            headers = message.get("payload", {}).get("headers", [])

            subject = "Sin asunto"
            sender = "Desconocido"

            for header in headers:
                if header["name"].lower() == "subject":
                    subject = header["value"]
                elif header["name"].lower() == "from":
                    sender = header["value"]

            report_lines.append(f"- De: {sender} | Asunto: {subject}")

        return "\n".join(report_lines)
    except Exception as e:
        return f"Error al recuperar los correos de Gmail: {str(e)}"


def send_gmail_message(to_email: str, subject: str, message_text: str) -> str:
    """
    Envía un correo electrónico a través de la API de Gmail.

    Args:
        to_email: Dirección de correo del destinatario (ej. 'ejemplo@correo.com').
        subject: Asunto del correo.
        message_text: Contenido del mensaje del correo.

    Returns:
        Mensaje confirmando el envío o reportando un fallo.
    """
    creds = get_google_credentials()
    if not creds:
        return "Error: No se encontraron credenciales de Google. Asegúrate de colocar el archivo 'credentials.json' en la raíz."

    try:
        service = build("gmail", "v1", credentials=creds)

        # Crear estructura MIMEText
        mime_message = MIMEText(message_text, "plain", "utf-8")
        mime_message["to"] = to_email
        mime_message["subject"] = subject

        # Codificar en base64url seguro para la API de Gmail
        raw_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode("utf-8")
        body = {"raw": raw_message}

        service.users().messages().send(userId="me", body=body).execute()
        return f"Éxito: Correo enviado correctamente a '{to_email}' con el asunto '{subject}'."
    except Exception as e:
        return f"Error al enviar el correo a través de Gmail: {str(e)}"
