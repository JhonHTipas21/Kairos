import os

from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
KAIROS_VAULT_DIR = os.getenv("KAIROS_VAULT_DIR", "vault")
VOICE_NAME = os.getenv("VOICE_NAME", "es-MX-JorgeNeural")

# Asegurar que existan los subdirectorios de la bóveda de Obsidian
vault_subdirs = ["inbox", "planes", "metricas", "memoria"]
for subdir in vault_subdirs:
    os.makedirs(os.path.join(KAIROS_VAULT_DIR, subdir), exist_ok=True)
