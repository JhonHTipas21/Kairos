"""
Skill para gestionar una lista de tareas (To-Do List) interactiva guardada en la bóveda de Obsidian.
"""

from pathlib import Path

from config import KAIROS_VAULT_DIR


def get_todo_file_path() -> Path:
    todo_path = Path(KAIROS_VAULT_DIR) / "todo.md"
    if not todo_path.exists():
        todo_path.parent.mkdir(parents=True, exist_ok=True)
        todo_path.write_text("# Lista de Tareas de Kairós\n\n", encoding="utf-8")
    return todo_path


def add_todo_item(task: str) -> str:
    """
    Añade una nueva tarea a la lista de pendientes (To-Do list).

    Args:
        task: La descripción o título de la tarea a añadir (ej. 'Comprar leche', 'Estudiar para el examen').

    Returns:
        Mensaje confirmando la adición de la tarea.
    """
    todo_path = get_todo_file_path()
    try:
        task_line = f"- [ ] {task.strip()}\n"
        with open(todo_path, "a", encoding="utf-8") as f:
            f.write(task_line)
        return f"Éxito: Se añadió la tarea '{task}' a la lista de pendientes."
    except Exception as e:
        return f"Error al añadir la tarea: {str(e)}"


def list_todo_items() -> str:
    """
    Obtiene la lista actual de tareas (pendientes y completadas).

    Returns:
        Una lista de tareas formateada en texto.
    """
    todo_path = get_todo_file_path()
    try:
        content = todo_path.read_text(encoding="utf-8")
        lines = content.strip().split("\n")

        todos = []
        for line in lines:
            if line.startswith("- [ ]") or line.startswith("- [x]"):
                todos.append(line)

        if not todos:
            return "La lista de tareas está actualmente vacía."

        pending = [t.replace("- [ ] ", "") for t in todos if "- [ ]" in t]
        completed = [t.replace("- [x] ", "") for t in todos if "- [x]" in t]

        report = []
        if pending:
            report.append("### Tareas Pendientes:")
            for idx, task in enumerate(pending, 1):
                report.append(f"{idx}. {task}")
        else:
            report.append("No tiene tareas pendientes en este momento.")

        if completed:
            report.append("\n### Tareas Completadas:")
            for idx, task in enumerate(completed, 1):
                report.append(f"{idx}. {task}")

        return "\n".join(report)
    except Exception as e:
        return f"Error al leer la lista de tareas: {str(e)}"


def complete_todo_item(task_keyword: str) -> str:
    """
    Marca una tarea de la lista como completada buscando por una palabra clave.

    Args:
        task_keyword: Palabra clave que identifica la tarea a completar (ej. 'leche', 'examen').

    Returns:
        Mensaje de confirmación informando si se encontró y completó la tarea.
    """
    todo_path = get_todo_file_path()
    try:
        content = todo_path.read_text(encoding="utf-8")
        lines = content.split("\n")

        found = False
        updated_lines = []
        target_task = ""

        keyword = task_keyword.lower().strip()
        for line in lines:
            if line.startswith("- [ ]") and keyword in line.lower():
                # Cambiar de [ ] a [x]
                updated_lines.append(line.replace("- [ ]", "- [x]", 1))
                target_task = line.replace("- [ ] ", "").strip()
                found = True
            else:
                updated_lines.append(line)

        if found:
            todo_path.write_text("\n".join(updated_lines), encoding="utf-8")
            return f"Éxito: Se marcó como completada la tarea '{target_task}'."
        return f"No encontré ninguna tarea pendiente que coincida con '{task_keyword}'."
    except Exception as e:
        return f"Error al completar la tarea: {str(e)}"


def clear_completed_todos() -> str:
    """
    Elimina todas las tareas que ya han sido completadas de la lista.

    Returns:
        Mensaje confirmando la limpieza.
    """
    todo_path = get_todo_file_path()
    try:
        content = todo_path.read_text(encoding="utf-8")
        lines = content.split("\n")

        updated_lines = []
        cleared_count = 0
        for line in lines:
            if line.startswith("- [x]"):
                cleared_count += 1
            else:
                updated_lines.append(line)

        if cleared_count > 0:
            todo_path.write_text("\n".join(updated_lines), encoding="utf-8")
            return f"Éxito: Se eliminaron {cleared_count} tareas completadas de la lista."
        return "No había ninguna tarea completada para limpiar."
    except Exception as e:
        return f"Error al limpiar la lista de tareas: {str(e)}"
