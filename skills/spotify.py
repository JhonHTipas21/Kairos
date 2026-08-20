"""
Skill para controlar la aplicación de Spotify local en macOS utilizando AppleScript (completamente gratuito).
"""
import subprocess

def open_spotify() -> str:
    """
    Abre la aplicación de Spotify Desktop en macOS.

    Returns:
        Mensaje de confirmación del estado de la operación.
    """
    try:
        subprocess.run(["open", "-a", "Spotify"], check=True)
        return "Spotify se ha abierto en su sistema, señor."
    except Exception as e:
        return f"Error al abrir Spotify: {str(e)}"

def control_spotify(action: str) -> str:
    """
    Controla la reproducción de música en la aplicación local de Spotify Desktop en macOS.

    Args:
        action: Acción a ejecutar: 'play' (reproducir), 'pause' (pausar), 'next' (siguiente canción), 'previous' (canción anterior).

    Returns:
        Mensaje de confirmación del estado de la reproducción.
    """
    clean_action = action.lower().strip()
    
    script_map = {
        "play": 'tell application "Spotify" to play',
        "pause": 'tell application "Spotify" to pause',
        "next": 'tell application "Spotify" to next track',
        "previous": 'tell application "Spotify" to previous track'
    }
    
    if clean_action not in script_map:
        return f"Acción '{action}' no válida. Use: 'play', 'pause', 'next' o 'previous'."
        
    try:
        subprocess.run(["osascript", "-e", script_map[clean_action]], check=True)
        resp_map = {
            "play": "Reproduciendo música en Spotify.",
            "pause": "Reproducción pausada en Spotify.",
            "next": "Saltando a la siguiente pista en Spotify.",
            "previous": "Reproduciendo la pista anterior en Spotify."
        }
        return resp_map[clean_action]
    except Exception as e:
        # Si falla porque Spotify no está abierto, intentar abrirlo y reproducir
        if clean_action == "play":
            try:
                subprocess.run(["open", "-a", "Spotify"], check=True)
                import time
                time.sleep(2.0)
                subprocess.run(["osascript", "-e", 'tell application "Spotify" to play'], check=True)
                return "Abriendo Spotify y reproduciendo música."
            except Exception as ex:
                return f"Error al controlar Spotify: {str(ex)}"
        return f"Error al controlar Spotify (asegúrese de que la aplicación esté abierta): {str(e)}"

def play_spotify_playlist_or_song(search_query: str) -> str:
    """
    Busca y reproduce una canción, artista, álbum o lista de reproducción (playlist) en la aplicación local de Spotify Desktop de macOS.

    Args:
        search_query: El término de búsqueda o nombre de la lista de reproducción (ej. 'reggaeton', 'lofi coding').

    Returns:
        Mensaje confirmando la búsqueda y reproducción en Spotify.
    """
    try:
        # Abrir Spotify primero para asegurar que reciba el comando
        subprocess.run(["open", "-a", "Spotify"], check=True)
        import time
        time.sleep(1.5)
        
        # Ejecutar AppleScript para reproducir la búsqueda
        script = f'tell application "Spotify" to play track "spotify:search:{search_query}"'
        subprocess.run(["osascript", "-e", script], check=True)
        return f"Buscando y reproduciendo '{search_query}' en Spotify, señor."
    except Exception as e:
        return f"Error al intentar buscar y reproducir en Spotify: {str(e)}"
