# 🕉️ MAHABHARATA SYSTEM

**MAHABHARATA SYSTEM** is a Multi-Agent AI Operating System designed to be a local-first, intelligent assistant powered by Ollama. 

It consists of a team of specialized AI agents working together under a master orchestrator, providing text, voice, and API-based interactions.

## 🤖 The Agents

The system is composed of five core agents, each with a specific domain of expertise:

- **👑 KRISHNA (Master Orchestrator):** The Commander. Manages the system, delegates tasks to other agents, and handles the main loop.
- **🏹 ARJUNA (Search & Knowledge):** The Researcher. Specializes in gathering information, web search (via Tavily), and processing knowledge.
- **💪 BHIMA (System Operator):** The Executor. Has full OS access, capable of desktop automation, and executing system-level commands.
- **📜 DHARMA (Memory & Personality):** The Soul. Manages long-term memory, personality persistence, and database interactions.
- **🛠️ KARNA (Coder & Engineer):** The Builder. Handles code generation, scripting, and technical problem-solving.

## 🚀 Features

- **Local-First AI:** Powered by local LLMs via Ollama (default: `qwen3:8b`).
- **Voice Interaction:** Supports speech-to-text using local Whisper models and high-quality text-to-speech using Edge-TTS.
- **RESTful API & Dashboard:** Includes a FastAPI-based backend and frontend dashboard.
- **Windows Startup Integration:** Can be registered to start automatically with Windows.
- **Modular Integrations:** Telegram bot, GitHub, and more.

## 🛠️ Tech Stack

- **LLM Engine:** Ollama (OpenAI-compatible client)
- **Voice:** Whisper (STT), Edge-TTS (TTS)
- **Backend:** FastAPI, Uvicorn, SQLAlchemy
- **Database:** PostgreSQL
- **Automation:** PyAutoGUI, psutil
- **Search:** Tavily API

## ⚙️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yogavinay/KrishnaOS-.git
   cd KrishnaOS-
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment:**
   - Copy `.env.example` to `.env`
   - Update the variables (e.g., `OLLAMA_MODEL`, `DATABASE_URL`, API keys).

4. **Ensure Services are Running:**
   - Make sure Ollama is installed and running locally.
   - Ensure your PostgreSQL database is accessible.

## 🎮 Usage

You can start the system in different modes using `main.py`:

```bash
# Start in standard interactive text mode
python main.py

# Start in voice interactive mode
python main.py --voice

# Start the API server and dashboard only (runs on http://localhost:8000)
python main.py --api

# Register the system to run on Windows startup
python main.py --register
```
