# Kairos OS

Kairos OS is an intelligent voice and text orchestrator assistant inspired by the J.A.R.V.I.S. system. It functions as a local desktop companion that connects four main modules: a reasoning engine (Gemini), a local markdown-based memory vault (Obsidian), high-performance local speech recognition (Whisper), and a web-based head-up display (HUD).

## Core Architecture

- **Reasoning Engine:** Configured with the Google GenAI SDK using the active gemini-3.7-flash model. It handles orchestration and automatic semantic tool calling.
- **Speech-to-Text (STT):** Powered by a local Faster-Whisper installation running in int8 quantization on CPU. It features forced Spanish language detection and contextual keyword prompting.
- **Text-to-Speech (TTS):** Generates responses using edge-tts with high-quality natural voice synthesis, played back locally via macOS afplay.
- **Memory System:** Uses a local directory of Markdown files compatible with Obsidian, allowing unstructured and structured persistent notes.
- **User Interface (HUD):** A real-time web interface built with HTML5, CSS Grid, and WebSockets. It displays current logs, daily plans, system metrics, and accepts PTT microphone or terminal input.

## System Dependencies

To run the system, you need Python 3.9+ and macOS. The following local binary packages are required:

- **FFmpeg:** Needed by Faster-Whisper for audio processing. Can be installed via Homebrew:
  ```bash
  brew install ffmpeg
  ```
- **afplay:** Built-in macOS command-line audio player (no installation required).

## Installation

1. Clone the repository:
   ```bash
   git clone git@github.com:JhonHTipas21/Kairos.git
   cd Kairos
   ```

2. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure the environment variables in a `.env` file at the root of the project:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   KAIROS_VAULT_DIR=vault
   VOICE_NAME=es-MX-JorgeNeural
   ```

## Repository Structure

- `main.py`: Core server built with FastAPI, managing WebSockets, the audio buffer stream, Whisper transcription, TTS synthesis, and the Gemini client session.
- `config.py`: Module for loading and exporting environment configurations.
- `requirements.txt`: Python package dependencies.
- `hud/`: Client interface directory containing index.html, style.css, and app.js.
- `skills/`: Modular skill definitions scanned dynamically on startup:
  - `system.py`: Volume controls, battery status, screen locking, and screenshot capture.
  - `browser.py`: Web browsing, Google searches, and YouTube playback.
  - `spotify.py`: Controls for the macOS Spotify Desktop application.
  - `timer.py`: Alarms and delayed audio/visual reminders.
  - `vault.py`: Note reading and writing in the Obsidian vault.
  - `plan.py`: Daily schedule planner.
  - `metrics.py`: System performance telemetry logs.
  - `inbox.py`: Markdown note summaries.

## Usage

1. Start the local server:
   ```bash
   python3 main.py
   ```

2. Open the HUD dashboard in your web browser:
   ```
   http://localhost:8000/hud/index.html
   ```

3. Interaction:
   - **Voice (PTT):** Hold the space bar or click and hold "Iniciar Grabación" to speak, then release.
   - **Text:** Type directly into the terminal input box in the lower-right section.
