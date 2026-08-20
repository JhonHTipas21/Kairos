"""
Skill para obtener las últimas noticias del día utilizando el feed RSS de Google News.
"""

import urllib.request
import xml.etree.ElementTree as ET


def get_latest_news() -> str:
    """
    Obtiene las 5 noticias de actualidad más importantes de hoy en español.

    Returns:
        Un resumen textual con las principales noticias para que el asistente las lea.
    """
    url = "https://news.google.com/rss?hl=es-419&gl=US&ceid=US:es-419"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            xml_data = response.read()

        root = ET.fromstring(xml_data)
        items = root.findall(".//item")

        if not items:
            return "No encontré noticias disponibles en este momento."

        news_list = []
        for idx, item in enumerate(items[:5], 1):
            title = item.find("title").text
            # Limpiar un poco el título quitando la fuente (ej. " - El Tiempo")
            if " - " in title:
                title = title.split(" - ")[0]
            news_list.append(f"{idx}. {title}")

        news_summary = "\n".join(news_list)
        return f"Estas son las noticias más destacadas:\n\n{news_summary}"
    except Exception as e:
        return f"No he podido recuperar las noticias en este momento. Detalle: {str(e)}"
