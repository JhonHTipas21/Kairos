"""
Skill para integrar el servicio de Google Drive y respaldar la bóveda local.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from config import KAIROS_VAULT_DIR
from skills.google_auth import get_google_credentials


def backup_vault_to_drive() -> str:
    """
    Comprime la carpeta local de la bóveda de Obsidian ('vault') en un archivo ZIP
    y la sube a Google Drive dentro de una carpeta llamada 'Kairos Backups'.
    Luego, elimina el archivo ZIP temporal local.

    Returns:
        Mensaje confirmando la subida exitosa con el ID de archivo, o reportando el error.
    """
    creds = get_google_credentials()
    if not creds:
        return "Error: No se encontraron credenciales de Google. Asegúrate de colocar el archivo 'credentials.json' en la raíz."

    vault_path = Path(KAIROS_VAULT_DIR)
    if not vault_path.exists():
        return f"Error: La bóveda local '{KAIROS_VAULT_DIR}' no existe, no se pudo realizar el respaldo."

    # Nombre del archivo zip temporal
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"kairos_vault_backup_{timestamp}"
    temp_zip_file = Path(f"{zip_filename}.zip")

    try:
        # 1. Comprimir la carpeta de forma recursiva
        shutil.make_archive(zip_filename, "zip", vault_path)

        # 2. Inicializar cliente de Google Drive API
        service = build("drive", "v3", credentials=creds)

        # 3. Buscar si existe la carpeta 'Kairos Backups' en Drive
        folder_id = None
        query = "name = 'Kairos Backups' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        folders_result = service.files().list(q=query, spaces="drive", fields="files(id)").execute()
        folders = folders_result.get("files", [])

        if folders:
            folder_id = folders[0]["id"]
        else:
            # Crear la carpeta si no existe
            folder_metadata = {"name": "Kairos Backups", "mimeType": "application/vnd.google-apps.folder"}
            folder = service.files().create(body=folder_metadata, fields="id").execute()
            folder_id = folder.get("id")

        # 4. Configurar metadatos del archivo a subir
        file_metadata = {"name": f"{zip_filename}.zip", "parents": [folder_id]}

        media = MediaFileUpload(str(temp_zip_file), mimetype="application/zip", resumable=True)

        # 5. Realizar la subida
        uploaded_file = service.files().create(body=file_metadata, media_body=media, fields="id, name").execute()

        return f"Éxito: Bóveda respaldada correctamente en Google Drive en la carpeta 'Kairos Backups'. Archivo: '{uploaded_file.get('name')}' (ID: {uploaded_file.get('id')})."

    except Exception as e:
        return f"Error al respaldar la bóveda en Google Drive: {str(e)}"

    finally:
        # Asegurar la limpieza del archivo zip local temporal
        if temp_zip_file.exists():
            try:
                os.remove(temp_zip_file)
            except Exception:
                pass
