"""
Skill para cambiar dinámicamente la voz y personalidad del asistente.
"""

import main


def change_voice_persona(persona_name: str) -> str:
    """
    Cambia el perfil de voz (personalidad) del asistente Kairos en tiempo de ejecución.

    Args:
        persona_name: El nombre de la personalidad deseada: 'jarvis' (voz masculina) o 'friday' (voz femenina).

    Returns:
        Mensaje confirmando el cambio de personalidad.
    """
    clean_name = persona_name.lower().strip()

    # Perfiles de voz neural de alta calidad en español (edge-tts)
    if "friday" in clean_name or "femenina" in clean_name or "mujer" in clean_name:
        main.current_voice = "es-MX-DaliaNeural"
        return "Cambio de personalidad completado. A partir de ahora responderé bajo el perfil de F.R.I.D.A.Y., señor."

    elif "jarvis" in clean_name or "masculino" in clean_name or "hombre" in clean_name:
        main.current_voice = "es-MX-JorgeNeural"
        return "Sistemas reestablecidos. He vuelto al perfil predeterminado de J.A.R.V.I.S., señor."

    else:
        return f"Perfil '{persona_name}' no reconocido. Los perfiles disponibles son 'J.A.R.V.I.S.' (masculino) y 'F.R.I.D.A.Y.' (femenino)."
