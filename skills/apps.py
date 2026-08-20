"""
Skill para abrir aplicaciones nativas de macOS mediante comandos de consola.
"""

import subprocess


def open_application(app_name: str) -> str:
    """
    Abre una aplicación nativa de macOS por su nombre (ej. 'Safari', 'Calculadora', 'Calendario', 'Spotify').

    Args:
        app_name: El nombre de la aplicación a abrir (ej. 'Safari', 'Google Chrome', 'Calculator', 'Notes').

    Returns:
        Mensaje de confirmación del estado de la operación.
    """
    clean_name = app_name.lower().strip()

    # Mapeo de nombres comunes en español a nombres oficiales de macOS
    app_mapping = {
        "safari": "Safari",
        "chrome": "Google Chrome",
        "google chrome": "Google Chrome",
        "spotify": "Spotify",
        "notas": "Notes",
        "notes": "Notes",
        "calendario": "Calendar",
        "calendar": "Calendar",
        "calculadora": "Calculator",
        "calculator": "Calculator",
        "terminal": "Terminal",
        "finder": "Finder",
        "correo": "Mail",
        "mail": "Mail",
        "vs code": "Visual Studio Code",
        "visual studio code": "Visual Studio Code",
        "musica": "Music",
        "music": "Music",
    }

    target_app = app_mapping.get(clean_name, app_name)

    try:
        subprocess.run(["open", "-a", target_app], check=True)
        return f"Abriendo la aplicación '{target_app}', señor."
    except Exception:
        # Fallback usando el nombre literal que proporcionó el usuario
        try:
            subprocess.run(["open", "-a", app_name], check=True)
            return f"Abriendo la aplicación '{app_name}', señor."
        except Exception:
            return f"No he podido abrir la aplicación '{app_name}'. Asegúrese de que el nombre sea correcto y esté instalada en su Mac."
