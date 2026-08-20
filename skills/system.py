"""
Skill para consultar y controlar configuraciones locales del sistema macOS.
"""
import subprocess

def adjust_system_volume(volume_percent: int) -> str:
    """
    Ajusta el volumen de salida de audio del sistema macOS.

    Args:
        volume_percent: Un entero entre 0 y 100 que indica el nivel de volumen deseado.

    Returns:
        Mensaje confirmando el nuevo nivel del volumen.
    """
    # Limitar el volumen entre 0 y 100
    volume = max(0, min(100, volume_percent))
    try:
        subprocess.run(["osascript", "-e", f"set volume output volume {volume}"], check=True)
        return f"Volumen de salida ajustado al {volume}%."
    except Exception as e:
        return f"Error al ajustar el volumen del sistema: {str(e)}"

def get_battery_status() -> str:
    """
    Obtiene información actual de la batería del sistema macOS (porcentaje, estado de carga y tiempo restante).

    Returns:
        Un reporte del estado de la batería del sistema.
    """
    try:
        output = subprocess.check_output(["pmset", "-g", "batt"]).decode("utf-8")
        lines = output.strip().split('\n')
        if len(lines) > 1:
            info = lines[1].split('\t')[-1]
            return f"Estado de batería actual: {info}"
        return f"Lectura de la batería: {output}"
    except Exception as e:
        return f"Error al leer el estado de la batería: {str(e)}"

def lock_macos_screen() -> str:
    """
    Bloquea la pantalla del equipo macOS inmediatamente para proteger la sesión del usuario.

    Returns:
        Mensaje informando que se bloqueó la pantalla.
    """
    try:
        # Envía la pulsación de teclas estándar de macOS (Ctrl + Cmd + Q) para bloquear la pantalla
        script = 'tell application "System Events" to keystroke "q" using {control down, command down}'
        subprocess.run(["osascript", "-e", script], check=True)
        return "Pantalla bloqueada con éxito."
    except Exception as e:
        return f"Error al bloquear la pantalla: {str(e)}"

def take_screenshot() -> str:
    """
    Toma una captura de pantalla completa del sistema macOS y la guarda en la carpeta de Descargas (Downloads) del usuario.

    Returns:
        Un mensaje con la ruta del archivo de captura guardado.
    """
    import os
    from datetime import datetime
    
    downloads_dir = os.path.expanduser("~/Downloads")
    os.makedirs(downloads_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filepath = os.path.join(downloads_dir, f"captura_{timestamp}.png")
    
    try:
        subprocess.run(["screencapture", "-x", filepath], check=True)
        return f"Captura de pantalla guardada con éxito en la carpeta de Descargas como: captura_{timestamp}.png."
    except Exception as e:
        return f"Error al tomar captura de pantalla: {str(e)}"
