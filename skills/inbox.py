"""
Skill para leer y resumir la bandeja de entrada (inbox) de la bóveda.
"""

from pathlib import Path

from config import KAIROS_VAULT_DIR


def summarize_inbox() -> str:
    """
    Lee las notas rápidas y transcripciones en la carpeta 'inbox' de la bóveda de Obsidian y devuelve un resumen del contenido actual.

    Returns:
        Un resumen detallado de las notas del inbox o un aviso de que está vacío.
    """
    inbox_dir = Path(KAIROS_VAULT_DIR) / "inbox"

    if not inbox_dir.exists():
        return "El directorio de inbox no existe."

    files = list(inbox_dir.glob("*.md"))
    if not files:
        # Fallback a un archivo general inbox.md si existe
        inbox_file = Path(KAIROS_VAULT_DIR) / "inbox.md"
        if inbox_file.exists():
            try:
                content = inbox_file.read_text(encoding="utf-8")
                return f"Contenido del archivo inbox.md:\n\n{content}"
            except Exception as e:
                return f"Error al leer inbox.md: {str(e)}"
        return "La bandeja de entrada (inbox) está vacía en este momento."

    summary_parts = []
    for f in files:
        try:
            content = f.read_text(encoding="utf-8")
            summary_parts.append(f"### Nota: {f.name}\n{content}")
        except Exception as e:
            summary_parts.append(f"### Nota: {f.name}\nError de lectura: {str(e)}")

    return "\n\n".join(summary_parts)
