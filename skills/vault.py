"""
Skill para operaciones generales de lectura y escritura de archivos Markdown en la bóveda de Obsidian.
"""
import os
from pathlib import Path
from config import KAIROS_VAULT_DIR

def read_vault_file(relative_path: str) -> str:
    """
    Lee el contenido de un archivo específico dentro de la bóveda de Obsidian.

    Args:
        relative_path: Ruta relativa del archivo dentro de la bóveda (ej. 'memoria/preferencias.md').

    Returns:
        El contenido de texto del archivo, o un mensaje de error si no existe.
    """
    # Limpiar la ruta para evitar directory traversal
    clean_path = relative_path.lstrip("/")
    file_path = Path(KAIROS_VAULT_DIR) / clean_path
    
    if not file_path.exists():
        return f"Error: El archivo '{clean_path}' no existe en la bóveda."
        
    try:
        content = file_path.read_text(encoding="utf-8")
        return content
    except Exception as e:
        return f"Error al leer el archivo: {str(e)}"

def write_vault_file(relative_path: str, content: str) -> str:
    """
    Escribe o sobrescribe un archivo en la bóveda de Obsidian con el contenido provisto.

    Args:
        relative_path: Ruta relativa del archivo dentro de la bóveda (ej. 'memoria/preferencias.md').
        content: El texto que se va a escribir en el archivo.

    Returns:
        Un mensaje confirmando el éxito o reportando el error de escritura.
    """
    clean_path = relative_path.lstrip("/")
    file_path = Path(KAIROS_VAULT_DIR) / clean_path
    
    try:
        # Asegurar que los directorios padres existan
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        return f"Éxito: Se escribió correctamente en '{clean_path}'."
    except Exception as e:
        return f"Error al escribir el archivo: {str(e)}"
