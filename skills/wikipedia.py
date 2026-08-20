"""
Skill para realizar consultas rápidas en Wikipedia en español.
"""
import json
import urllib.request
import urllib.parse

def search_wikipedia(query: str) -> str:
    """
    Busca un tema, personaje, evento o concepto en Wikipedia en español y devuelve un resumen preciso.

    Args:
        query: El término o concepto que se desea buscar (ej. 'Inteligencia Artificial', 'Albert Einstein', 'Marte').

    Returns:
        Un extracto o resumen del artículo de Wikipedia, o un mensaje de error si no se encuentra.
    """
    # Codificar el término de búsqueda para la URL (los espacios se reemplazan por guiones bajos)
    safe_query = urllib.parse.quote(query.strip().replace(" ", "_"))
    url = f"https://es.wikipedia.org/api/rest_v1/page/summary/{safe_query}"
    
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            
        title = data.get("title", query)
        extract = data.get("extract", "")
        
        if not extract:
            return f"No encontré un extracto o definición clara sobre '{query}'."
            
        return f"Según Wikipedia, {title}: {extract}"
    except Exception as e:
        return f"No he encontrado información para '{query}' en Wikipedia en este momento."
