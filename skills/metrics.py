"""
Skill para simular la recolección y guardado de métricas analíticas del sistema.
"""
import os
import random
from pathlib import Path
from datetime import datetime
from config import KAIROS_VAULT_DIR

def log_system_metrics() -> str:
    """
    Simula la obtención de métricas de rendimiento del sistema (CPU, RAM y latencia de red) y las registra en 'metricas/rendimiento.md'.

    Returns:
        Un reporte de texto con las métricas registradas.
    """
    metrics_path = Path(KAIROS_VAULT_DIR) / "metricas" / "rendimiento.md"
    
    try:
        metrics_path.parent.mkdir(parents=True, exist_ok=True)
        
        cpu_usage = random.randint(10, 85)
        memory_usage = random.randint(30, 90)
        network_latency = random.randint(15, 120)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_entry = f"| {timestamp} | {cpu_usage}% | {memory_usage}% | {network_latency}ms |\n"
        
        if not metrics_path.exists():
            header = (
                "# Logs de Rendimiento Analítico\n\n"
                "| Timestamp | Uso de CPU | Uso de RAM | Latencia de Red |\n"
                "| --- | --- | --- | --- |\n"
            )
            metrics_path.write_text(header + log_entry, encoding="utf-8")
        else:
            with open(metrics_path, "a", encoding="utf-8") as f:
                f.write(log_entry)
                
        return f"Métricas registradas con éxito: CPU {cpu_usage}%, RAM {memory_usage}%, Latencia {network_latency}ms."
    except Exception as e:
        return f"Error al registrar las métricas: {str(e)}"
