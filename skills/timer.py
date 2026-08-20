"""
Skill para programar alarmas y recordatorios en el sistema Kairos.
"""

import threading
import time


def set_alarm_timer(minutes: float, label: str = "Recordatorio General") -> str:
    """
    Programa una alarma o recordatorio que emitirá una alerta visual en el HUD y un mensaje de voz en el sistema
    cuando transcurra el tiempo indicado en minutos.

    Args:
        minutes: Cantidad de minutos a esperar antes de sonar la alarma (puede ser decimal, ej. 0.5 para 30 segundos).
        label: Nombre o descripción del recordatorio (ej. 'tomar agua', 'ir a almorzar').

    Returns:
        Mensaje confirmando la programación de la alarma.
    """
    if minutes <= 0:
        return "Error: Los minutos deben ser mayores a cero."

    seconds = int(minutes * 60)

    def trigger_reminder():
        time.sleep(seconds)

        try:
            import asyncio

            from main import broadcast, speak_response

            # Crear un bucle de eventos para ejecutar tareas asíncronas en este hilo secundario
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            alert_text = f"¡Alarma de recordatorio completada! Objetivo: {label}."
            print(f"[TIMER] Alerta disparada: {alert_text}")

            # Enviar alerta visual al HUD
            loop.run_until_complete(
                broadcast({"type": "log", "sender": "SYSTEM", "message": f"⏰ ALARMA DISPARADA: {label}"})
            )
            loop.run_until_complete(
                broadcast({"type": "status", "state": "speaking", "description": f"Recordatorio: {label}"})
            )

            # Anunciar por voz
            loop.run_until_complete(speak_response(f"Señor, recordatorio completado. {label}."))

            loop.run_until_complete(broadcast({"type": "status", "state": "idle", "description": "En espera."}))
            loop.close()
        except Exception as e:
            print(f"[TIMER] Error disparando el hilo de alarma: {str(e)}")

    # Iniciar el hilo en segundo plano para no bloquear a FastAPI
    thread = threading.Thread(target=trigger_reminder, daemon=True)
    thread.start()

    # Formatear el mensaje de confirmación
    if minutes < 1:
        time_display = f"{int(minutes * 60)} segundos"
    else:
        time_display = f"{minutes} minutos"

    return f"Éxito: He programado un recordatorio para '{label}' en {time_display}."
