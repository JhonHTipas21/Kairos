"""
Skill para abrir páginas web, buscar en Google y reproducir contenido en YouTube.
"""

import urllib.parse
import webbrowser


def open_web_url(url: str) -> str:
    """
    Abre un enlace web o URL específico en el navegador predeterminado del sistema.

    Args:
        url: La URL completa o dominio (ej. 'https://github.com' o 'google.com').

    Returns:
        Mensaje informando la dirección abierta.
    """
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    try:
        webbrowser.open(url)
        return f"Abriendo la dirección web: {url}"
    except Exception as e:
        return f"Error abriendo la página web: {str(e)}"


def search_google(query: str) -> str:
    """
    Realiza una consulta o búsqueda en Google utilizando el navegador predeterminado.

    Args:
        query: La frase o término de búsqueda a consultar.

    Returns:
        Confirmación del término de búsqueda.
    """
    encoded_query = urllib.parse.quote(query)
    search_url = f"https://www.google.com/search?q={encoded_query}"
    try:
        webbrowser.open(search_url)
        return f"Buscando '{query}' en Google."
    except Exception as e:
        return f"Error realizando la búsqueda: {str(e)}"


def play_youtube_video(video_keywords: str) -> str:
    """
    Busca y reproduce un video en YouTube basado en las palabras clave provistas.

    Args:
        video_keywords: El título o palabras clave del video que se desea reproducir.

    Returns:
        Confirmación de la búsqueda del video en YouTube.
    """
    encoded_keywords = urllib.parse.quote(video_keywords)
    youtube_url = f"https://www.youtube.com/results?search_query={encoded_keywords}"
    try:
        webbrowser.open(youtube_url)
        return f"Buscando '{video_keywords}' en YouTube."
    except Exception as e:
        return f"Error abriendo YouTube: {str(e)}"
