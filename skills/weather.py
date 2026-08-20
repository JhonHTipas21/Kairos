"""
Skill para consultar el clima actual de cualquier ciudad utilizando el servicio wttr.in (libre de keys).
"""
import urllib.request
import urllib.parse

def get_current_weather(city_name: str = "Cali") -> str:
    """
    Obtiene el reporte del clima actual (temperatura, condiciones, humedad y viento) de una ciudad específica.

    Args:
        city_name: El nombre de la ciudad a consultar (ej. 'Bogota', 'Cali', 'Madrid').

    Returns:
        Reporte del clima detallado de la ciudad.
    """
    # Codificar el nombre de la ciudad para la URL
    safe_city = urllib.parse.quote(city_name.strip())
    url = f"https://wttr.in/{safe_city}?format=%C+%t+Humedad:%h+Viento:%w"
    
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            weather_data = response.read().decode('utf-8').strip()
            # Reemplazar el signo + si wttr.in lo devuelve como espaciador
            clean_weather = weather_data.replace("+", " ")
            return f"Reporte del clima actual en {city_name.capitalize()}: {clean_weather}."
    except Exception as e:
        return f"No he podido recuperar el reporte del clima para {city_name} en este momento. Detalle: {str(e)}"
