"""
Módulo de autenticación centralizado para los servicios de Google Workspace.
"""

import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Definir los alcances (scopes) necesarios para Calendario, Gmail y Drive
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/drive.file",
]


def get_google_credentials():
    """
    Recupera las credenciales autenticadas para Google Workspace.
    Si no existen credenciales guardadas en token.json, inicia el flujo de login local.

    Returns:
        google.oauth2.credentials.Credentials: Las credenciales del usuario autorizado.
    """
    creds = None
    token_path = "token.json"

    # Cargar token existente si existe
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        except Exception:
            creds = None

    # Si las credenciales no son válidas o expiraron, realizar el inicio de sesión
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None

        if not creds:
            credentials_path = "credentials.json"
            if not os.path.exists(credentials_path):
                # Retorna None si no hay archivo de configuración de cliente; el módulo llamador manejará el error
                return None

            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            # Abrir el navegador local para completar la autenticación
            creds = flow.run_local_server(port=0)

        # Guardar el token para ejecuciones futuras
        with open(token_path, "w") as token_file:
            token_file.write(creds.to_json())

    return creds
