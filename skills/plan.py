"""
Skill para actualizar el plan diario con las prioridades principales.
"""

from datetime import datetime
from pathlib import Path

from config import KAIROS_VAULT_DIR


def update_daily_plan(priorities: list[str]) -> str:
    """
    Actualiza el archivo de planificación diaria ('planes/plan_diario.md') en la bóveda con el Top 3 de prioridades para el día de hoy.

    Args:
        priorities: Una lista de cadenas con las prioridades principales del día (debe contener idealmente hasta 3).

    Returns:
        Mensaje de confirmación del éxito de la operación.
    """
    plan_path = Path(KAIROS_VAULT_DIR) / "planes" / "plan_diario.md"

    try:
        plan_path.parent.mkdir(parents=True, exist_ok=True)

        date_str = datetime.now().strftime("%Y-%m-%d")

        lines = [f"# Plan Diario - {date_str}", "", "## Top 3 Prioridades del Día", ""]

        # Tomar como máximo las primeras 3 prioridades
        for idx, priority in enumerate(priorities[:3], 1):
            lines.append(f"{idx}. [ ] {priority}")

        content = "\n".join(lines) + "\n"
        plan_path.write_text(content, encoding="utf-8")

        return f"Éxito: Se actualizó el plan diario en 'planes/plan_diario.md' con {len(priorities[:3])} prioridades."
    except Exception as e:
        return f"Error al actualizar el plan diario: {str(e)}"
