import os
import sys
import json
import asyncio
import inspect
import importlib.util
import tempfile
import subprocess
import functools
import webbrowser
from pathlib import Path

# Dependencias externas
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, HTMLResponse
from google import genai
from google.genai import types
import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel
import edge_tts

# Módulos del proyecto
from config import KAIROS_VAULT_DIR, GEMINI_API_KEY, VOICE_NAME

app = FastAPI(title="KAIROS OS API")

# Servir archivos estáticos del HUD
app.mount("/hud", StaticFiles(directory="hud"), name="hud")

# Variables globales
active_connections: list[WebSocket] = []
whisper_model = None
chat_session = None
gemini_client = None
audio_stream = None
recording = False
audio_buffer = []
skill_map = {}

# Redirigir la raíz al HUD
@app.get("/")
async def root():
    return RedirectResponse(url="/hud/index.html")

# 1. Difusión de mensajes a través de WebSockets
async def broadcast(message: dict):
    for connection in list(active_connections):
        try:
            await connection.send_json(message)
        except Exception:
            if connection in active_connections:
                active_connections.remove(connection)

# 2. Carga dinámica y envoltura de Skills (Neuronas)
def make_tool_wrapper(func):
    """
    Envuelve una función de skill para registrar sus inicios y retornos
    enviando logs y actualizaciones en tiempo real a la interfaz del HUD.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        arg_str = ", ".join(f"{k}={v}" for k, v in kwargs.items())
        msg = f"Ejecutando skill '{func.__name__}' con ({arg_str})..."
        print(f"[TOOL] {msg}")
        
        # Enviar logs al HUD sin bloquear el hilo síncrono
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(broadcast({
                "type": "log",
                "sender": "SKILL-EXEC",
                "message": msg
            }))
        except RuntimeError:
            pass
            
        # Ejecutar la función original
        result = func(*args, **kwargs)
        
        # Enviar el resultado al HUD
        res_msg = f"Skill '{func.__name__}' finalizó con respuesta: {result}"
        print(f"[TOOL] {res_msg}")
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(broadcast({
                "type": "log",
                "sender": "SKILL-EXEC",
                "message": res_msg
            }))
            
            # Recargas dinámicas automáticas según la skill ejecutada
            if func.__name__ in ["update_daily_plan", "write_vault_file"]:
                loop.create_task(load_and_broadcast_plan())
            if func.__name__ == "log_system_metrics":
                loop.create_task(load_and_broadcast_metrics())
            if func.__name__ == "summarize_inbox":
                loop.create_task(load_and_broadcast_inbox())
        except RuntimeError:
            pass
            
        return result
    return wrapper

def load_skills(skills_dir: str = "skills") -> list:
    global skill_map
    wrapped_skills = []
    skills_path = Path(skills_dir)
    if not skills_path.exists():
        print(f"[SYSTEM] Advertencia: Directorio '{skills_dir}' no encontrado.")
        return wrapped_skills
        
    for py_file in skills_path.glob("*.py"):
        if py_file.name == "__init__.py":
            continue
            
        module_name = f"skills.{py_file.stem}"
        spec = importlib.util.spec_from_file_location(module_name, py_file)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Inspeccionar funciones definidas en el módulo
            for name, obj in inspect.getmembers(module, inspect.isfunction):
                if obj.__module__ == module_name:
                    wrapped = make_tool_wrapper(obj)
                    wrapped_skills.append(wrapped)
                    skill_map[name] = wrapped
                    print(f"[SYSTEM] Skill registrada: {name} (de {py_file.name})")
                    
    return wrapped_skills

# 3. Helpers para cargar datos de la bóveda de Obsidian y difundir al HUD
async def load_and_broadcast_plan():
    plan_file = Path(KAIROS_VAULT_DIR) / "planes" / "plan_diario.md"
    if plan_file.exists():
        try:
            content = plan_file.read_text(encoding="utf-8")
            await broadcast({"type": "plan", "content": content})
        except Exception as e:
            await broadcast({"type": "plan", "content": f"Error leyendo plan diario: {str(e)}"})
    else:
        await broadcast({"type": "plan", "content": "El plan diario no ha sido creado hoy en la bóveda."})

async def load_and_broadcast_inbox():
    inbox_dir = Path(KAIROS_VAULT_DIR) / "inbox"
    summary_parts = []
    
    inbox_file = Path(KAIROS_VAULT_DIR) / "inbox.md"
    if inbox_file.exists():
        try:
            summary_parts.append(f"**inbox.md**:<br>{inbox_file.read_text(encoding='utf-8')}")
        except Exception:
            pass
            
    if inbox_dir.exists():
        for f in inbox_dir.glob("*.md"):
            try:
                summary_parts.append(f"**{f.name}**:<br>{f.read_text(encoding='utf-8')}")
            except Exception:
                pass
                
    content = "<br><br>".join(summary_parts) if summary_parts else "La bandeja de entrada (inbox) está vacía."
    await broadcast({"type": "inbox", "content": content})

async def load_and_broadcast_metrics():
    import random
    cpu = random.randint(15, 60)
    ram = random.randint(40, 75)
    latency = random.randint(20, 95)
    await broadcast({"type": "metrics", "cpu": cpu, "ram": ram, "latency": latency})

# 4. Envío de datos iniciales en la conexión del socket
async def send_initial_data(ws: WebSocket):
    plan_file = Path(KAIROS_VAULT_DIR) / "planes" / "plan_diario.md"
    plan_content = "El plan diario no ha sido creado hoy en la bóveda."
    if plan_file.exists():
        try:
            plan_content = plan_file.read_text(encoding="utf-8")
        except Exception as e:
            plan_content = f"Error leyendo plan: {str(e)}"
    await ws.send_json({"type": "plan", "content": plan_content})

    inbox_dir = Path(KAIROS_VAULT_DIR) / "inbox"
    summary_parts = []
    inbox_file = Path(KAIROS_VAULT_DIR) / "inbox.md"
    if inbox_file.exists():
        try:
            summary_parts.append(f"**inbox.md**:<br>{inbox_file.read_text(encoding='utf-8')}")
        except Exception:
            pass
    if inbox_dir.exists():
        for f in inbox_dir.glob("*.md"):
            try:
                summary_parts.append(f"**{f.name}**:<br>{f.read_text(encoding='utf-8')}")
            except Exception:
                pass
    inbox_content = "<br><br>".join(summary_parts) if summary_parts else "La bandeja de entrada (inbox) está vacía."
    await ws.send_json({"type": "inbox", "content": inbox_content})

    import random
    await ws.send_json({
        "type": "metrics",
        "cpu": random.randint(15, 60),
        "ram": random.randint(40, 75),
        "latency": random.randint(20, 95)
    })

# 5. Captura y Callback de Audio
def audio_callback(indata, frames, time, status):
    if recording:
        audio_buffer.append(indata.copy())

async def start_audio_recording():
    global recording, audio_buffer
    if recording:
        return
    recording = True
    audio_buffer = []
    await broadcast({"type": "status", "state": "listening", "description": "Escuchando..."})
    print("[AUDIO] Grabación de voz iniciada.")

async def stop_audio_recording():
    global recording
    if not recording:
        return
    recording = False
    await broadcast({"type": "status", "state": "thinking", "description": "Transcribiendo audio..."})
    print("[AUDIO] Grabación de voz detenida.")
    
    # Procesar el buffer de audio de forma asíncrona
    asyncio.create_task(process_recorded_audio())

# 6. Transcripción Local (Faster-Whisper) y flujo de orquestación
async def process_recorded_audio():
    global audio_buffer, whisper_model
    if not audio_buffer:
        await broadcast({"type": "status", "state": "idle", "description": "No se detectó audio."})
        return
        
    try:
        # Concatenar todos los buffers numpy float32
        audio_data = np.concatenate(audio_buffer, axis=0).flatten()
        
        # Ejecutar transcripción local en un hilo separado
        def transcribe():
            segments, info = whisper_model.transcribe(
                audio_data, 
                beam_size=5, 
                language="es",
                initial_prompt="Kairós, Spotify, YouTube, Obsidian, reproducción, música, plan diario, volumen, reproducir."
            )
            text = "".join(segment.text for segment in segments).strip()
            return text
            
        transcription = await asyncio.to_thread(transcribe)
        print(f"[STT] Transcripción lograda: {transcription}")
        
        if not transcription:
            await broadcast({"type": "log", "sender": "SYSTEM", "message": "No se reconoció voz o el texto está vacío."})
            await broadcast({"type": "status", "state": "idle", "description": "Esperando..."})
            return
            
        await broadcast({"type": "log", "sender": "USER-TRANSCRIPT", "message": transcription})
        await process_user_query(transcription)
        
    except Exception as e:
        err_msg = f"Error transcribiendo audio: {str(e)}"
        print(err_msg)
        await broadcast({"type": "log", "sender": "ERROR", "message": err_msg})
        await broadcast({"type": "status", "state": "idle"})

# 7. Orquestación del Cerebro de Gemini
async def process_user_query(text: str):
    global chat_session
    if not chat_session:
        err_msg = "Error: El cerebro (API de Gemini) no está configurado. Registra tu GEMINI_API_KEY en el archivo .env."
        await broadcast({"type": "log", "sender": "ERROR", "message": err_msg})
        await broadcast({"type": "status", "state": "idle"})
        return
        
    await broadcast({"type": "status", "state": "thinking", "description": "Kairós está pensando..."})
    
    try:
        # Ejecutar la llamada a la API de Gemini (bloqueante) en un hilo secundario con reintentos para evitar errores 503
        max_retries = 3
        retry_delay = 1.0  # segundos
        response = None
        
        for attempt in range(max_retries):
            try:
                response = await asyncio.to_thread(chat_session.send_message, text)
                break
            except Exception as e:
                err_str = str(e)
                # Si el error es por saturación del servidor (503), límite de tasa (429) o desconexión
                if any(x in err_str for x in ["503", "UNAVAILABLE", "ResourceExhausted", "429", "rate limit"]):
                    if attempt < max_retries - 1:
                        print(f"[GEMINI] Servidor ocupado/saturado. Reintentando en {retry_delay}s (intento {attempt + 1}/{max_retries})...")
                        await broadcast({
                            "type": "status",
                            "state": "thinking",
                            "description": f"Servidor saturado. Reintentando ({attempt + 1}/{max_retries})..."
                        })
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue
                raise e
                
        response_text = response.text
        
        print(f"[GEMINI] Respuesta: {response_text}")
        await broadcast({"type": "log", "sender": "KAIROS-LOG", "message": response_text})
        
        # Reproducir voz
        await broadcast({"type": "status", "state": "speaking", "description": "Kairós respondiendo..."})
        await speak_response(response_text)
        
    except Exception as e:
        err_msg = f"Error consultando a Gemini: {str(e)}"
        print(err_msg)
        await broadcast({"type": "log", "sender": "ERROR", "message": err_msg})
        await broadcast({"type": "status", "state": "speaking"})
        await speak_response("Disculpa, encontré un obstáculo al procesar la instrucción.")
        
    finally:
        await broadcast({"type": "status", "state": "idle", "description": "En espera de comandos."})

# 8. Síntesis y Reproducción Local de Voz (edge-tts + afplay)
async def speak_response(text: str):
    # Limpiar un poco el markdown para que no sea deletreado por el TTS
    clean_text = text.replace("*", "").replace("#", "").replace("[ ]", "").replace("[x]", "").strip()
    
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        temp_mp3_path = f.name
        
    try:
        communicate = edge_tts.Communicate(clean_text, VOICE_NAME)
        await communicate.save(temp_mp3_path)
        
        # Ejecutar afplay (macOS native player) en un hilo secundario para evitar bloquear el bucle de eventos
        def play():
            try:
                subprocess.run(["afplay", temp_mp3_path], check=True)
            except Exception as e:
                print(f"[AUDIO] Error reproduciendo con afplay: {str(e)}")
                
        await asyncio.to_thread(play)
        
    except Exception as e:
        print(f"[TTS] Error en síntesis o reproducción: {str(e)}")
    finally:
        try:
            os.remove(temp_mp3_path)
        except Exception:
            pass

# 9. Conectores de Red y WebSocket
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    print(f"[WS] HUD Conectado. Total clientes: {len(active_connections)}")
    
    await websocket.send_json({"type": "status", "state": "idle", "description": "Sistemas en línea. Kairós listo."})
    await send_initial_data(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            action = message.get("action")
            
            if action == "start_recording":
                await start_audio_recording()
            elif action == "stop_recording":
                await stop_audio_recording()
            elif action == "text_input":
                text = message.get("text", "")
                asyncio.create_task(process_user_query(text))
    except WebSocketDisconnect:
        if websocket in active_connections:
            active_connections.remove(websocket)
        print(f"[WS] HUD Desconectado. Total clientes: {len(active_connections)}")

# 10. Scheduler en segundo plano para actualizar métricas
async def metrics_scheduler():
    while True:
        try:
            await load_and_broadcast_metrics()
        except Exception:
            pass
        await asyncio.sleep(10)

# 11. Eventos de Inicialización y Cierre de FastAPI
@app.on_event("startup")
def startup_event():
    global whisper_model, chat_session, audio_stream, gemini_client
    
    # Iniciar la actualización de métricas en segundo plano
    asyncio.create_task(metrics_scheduler())
    
    # 1. Cargar Faster-Whisper
    print("[STT] Inicializando modelo Whisper (base) en CPU (tipo int8)...")
    try:
        whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
        print("[STT] Modelo Whisper inicializado correctamente.")
    except Exception as e:
        print(f"[STT] Error crítico cargando Whisper: {str(e)}")
        sys.exit(1)
        
    # 2. Inicializar Gemini
    print("[GEMINI] Configurando cliente de Google Generative AI...")
    
    # Cargar y mapear skills en el arranque siempre
    tools = load_skills()
    
    if not GEMINI_API_KEY:
        print("[WARNING] GEMINI_API_KEY no se encontró en las variables de entorno. Las peticiones a Gemini fallarán.")
    else:
        try:
            gemini_client = genai.Client(api_key=GEMINI_API_KEY)
            chat_session = gemini_client.chats.create(
                model="gemini-3.7-flash",
                config=types.GenerateContentConfig(
                    tools=tools,
                    system_instruction=(
                        "Eres KAIRÓS, un asistente virtual inteligente similar a J.A.R.V.I.S. de Iron Man. "
                        "Eres sofisticado, servicial, conciso y eficiente. Tu objetivo es ayudar al usuario a "
                        "gestionar su día, agenda y sistemas locales mediante las herramientas disponibles. "
                        "Debes responder siempre en español y mantener tus respuestas cortas y al grano "
                        "(máximo 2-3 oraciones a menos que sea un resumen detallado solicitado), ya que tus "
                        "respuestas serán leídas en voz alta por un sintetizador de voz (TTS). "
                        "Utiliza las herramientas (skills) correspondientes cuando el usuario te pida ver el inbox, "
                        "registrar métricas, cambiar su plan del día o interactuar con la bóveda de Obsidian."
                    )
                )
            )
            print("[GEMINI] Cerebro cargado y listo con el nuevo SDK de Google GenAI.")
        except Exception as e:
            print(f"[GEMINI] Error crítico configurando Gemini con el nuevo SDK: {str(e)}")
            
    # 3. Inicializar captura de micrófono en segundo plano
    print("[AUDIO] Iniciando stream de captura del micrófono local...")
    try:
        audio_stream = sd.InputStream(
            samplerate=16000,
            channels=1,
            dtype='float32',
            callback=audio_callback
        )
        audio_stream.start()
        print("[AUDIO] Micrófono operativo y en escucha pasiva (16000Hz, float32, mono).")
    except Exception as e:
        print(f"[AUDIO] Error inicializando el micrófono local: {str(e)}")
        print("[AUDIO] Asegúrate de otorgar permisos de micrófono a la terminal y tener un dispositivo conectado.")

    # 4. Programar apertura automática del navegador tras 1.5s
    loop = asyncio.get_event_loop()
    loop.call_later(1.5, lambda: webbrowser.open("http://localhost:8000"))

@app.on_event("shutdown")
def shutdown_event():
    global audio_stream
    print("[SYSTEM] Apagando sistemas...")
    if audio_stream:
        try:
            audio_stream.stop()
            audio_stream.close()
            print("[AUDIO] Stream del micrófono cerrado.")
        except Exception:
            pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info")
