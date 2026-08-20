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
   python3 -m pip install -r requirements.txt
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
- `ruff.toml`: Code styling and linting configurations.
- `hud/`: Client interface directory containing index.html, style.css, and app.js.
- `skills/`: Modular skill definitions scanned dynamically on startup.
- `tests/`: Unit test suite.

---

## Detailed Skill Documentation

Kairós OS automatically registers all functions inside the `skills/` directory on startup. Below is the detailed catalog of available modules and their functions:

### 1. Google Workspace Integrations
- **google_auth.py (Authentication Helper):**
  - Handles the OAuth2 desktop application login flow. Saves credentials securely in `token.json` and refreshes access tokens automatically.
- **gcalendar.py (Google Calendar Skill):**
  - `list_upcoming_events(max_results)`: Lists upcoming calendar appointments with readable formatted dates.
  - `create_calendar_event(summary, start_time_str, end_time_str, description)`: Programmatically creates appointments on the primary Google Calendar.
- **gdrive.py (Google Drive Backup Skill):**
  - `backup_vault_to_drive()`: Zips the Obsidian vault, searches for or creates a "Kairos Backups" folder on the user's Drive, uploads the archive with a timestamp, and deletes the temporary local file.
- **gmail.py (Gmail Integration Skill):**
  - `list_unread_emails(max_results)`: Fetches a text summary of unread emails including the sender and the subject.
  - `send_gmail_message(to_email, subject, message_text)`: Sends emails using base64url encoded payloads.

### 2. Media Playback & Controls
- **spotify.py (macOS Spotify Desktop Controller):**
  - `open_spotify()`: Launches the Spotify Desktop application.
  - `control_spotify(action)`: Emits AppleScript commands to trigger play, pause, next track, or previous track.
  - `play_spotify_playlist_or_song(search_query)`: Automatically searches and plays a specific song, artist, or playlist.
- **browser.py (Web Navigation Skill):**
  - `open_web_url(url)`: Opens any website in the default browser.
  - `search_google(query)`: Launches a web browser tab searching for the query.
  - `play_youtube_video(search_query)`: Opens YouTube and plays the top video matching the query.

### 3. Local Memory & Organization
- **vault.py (Obsidian Storage Skill):**
  - `read_vault_file(relative_path)`: Reads markdown notes from the vault.
  - `write_vault_file(relative_path, content)`: Creates or updates markdown files, ensuring parent directories exist.
  - `search_vault_notes(keyword)`: Recursively scans all markdown notes to find occurrences of a keyword, returning line numbers and matching text snippets.
- **todo.py (Interactive Task Manager):**
  - `add_todo_item(task)`: Appends an uncompleted task line (`- [ ]`) to `todo.md`.
  - `list_todo_items()`: Reads `todo.md` and displays pending and completed tasks.
  - `complete_todo_item(task_keyword)`: Marks matching tasks as completed (`- [x]`).
  - `clear_completed_todos()`: Removes completed tasks from `todo.md`.
- **plan.py (Daily Scheduler Skill):**
  - `update_daily_plan(priorities)`: Overwrites the daily plan markdown schedule with the top priorities.
- **inbox.py (Inbox Summarizer Skill):**
  - `summarize_inbox()`: Summarizes quick notes in the inbox folder.

### 4. System & Information Utilities
- **system.py (macOS System Skill):**
  - `adjust_system_volume(volume_level)`: Changes macOS master output volume (0 to 100).
  - `get_battery_status()`: Retrieves battery percentage and remaining time.
  - `take_screenshot()`: Takes a system-wide screen capture and saves it in the user's Downloads directory.
  - `lock_macos_screen()`: Simulated lock action (AppleScript accessibility required).
- **metrics.py (Hardware Telemetry Skill):**
  - `log_system_metrics()`: Records real macOS system telemetry (CPU usage, RAM allocation, disk space, ping latency to 8.8.8.8) into `metricas/rendimiento.md`.
- **greeting.py (Contextual Welcome Skill):**
  - `get_systems_briefing()`: Generates a time-based greeting, battery status report, and hardware metrics summary in Spanish.
- **timer.py (Background Scheduler Skill):**
  - `set_alarm_timer(seconds, message)`: Sets a background thread that synthesis speech and logs alerts on WebSocket when the timer expires.
- **weather.py (Weather Skill):**
  - `get_current_weather(city_name)`: Fetches keyless real-time weather information for any city from wttr.in.
- **news.py (News Skill):**
  - `get_latest_news()`: Parses Google News RSS XML feeds to summarize the top 5 articles.
- **wikipedia.py (Wikipedia Skill):**
  - `search_wikipedia(query)`: Queries Wikipedia's REST API for a concise article extract.
- **persona.py (Voice Profile Skill):**
  - `change_voice_persona(persona_name)`: Switches TTS voice personalities dynamically (J.A.R.V.I.S. vs. F.R.I.D.A.Y.).

---

## Google Cloud Console OAuth2 Configuration

To use the Google Workspace skills:
1. Go to the **Google Cloud Console**, create a project, and enable the **Google Calendar API**, **Google Drive API**, and **Gmail API**.
2. Setup the OAuth consent screen and create an OAuth Client ID credential (type: Desktop Application).
3. Download the credentials JSON file, rename it to `credentials.json`, and place it in the root folder of the project.
4. On the first API call, a browser tab will automatically open asking for authorization. Once completed, a `token.json` file will be saved locally.

---

## DevOps & Quality Control

### Code Quality (Ruff)
The project utilizes **Ruff** for formatting and lint checks. Configuration is defined in `ruff.toml`.
- Run formatting:
  ```bash
  python3 -m ruff format .
  ```
- Run linter checks:
  ```bash
  python3 -m ruff check . --fix
  ```

### Unit Testing (pytest)
Test cases are stored in the `tests/` directory. Mock integrations verify that weather, calendar, and email tools run correctly without keys.
- Run tests:
  ```bash
  python3 -m pytest tests/
  ```

### CI/CD Workflow
A GitHub Actions workflow is configured in `.github/workflows/ci.yml`. It runs automatically on every push or pull request to the `main` branch to install dependencies and execute the unit tests.
