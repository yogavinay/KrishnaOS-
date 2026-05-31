# ⚙️ Mahabharata System - Comprehensive Setup Guide

Welcome to the **Mahabharata System** setup! This guide will walk you through everything you need to get your local multi-agent AI Operating System running perfectly.

---

## 📋 1. Prerequisites

Before starting, ensure you have the following installed on your machine:

- **OS:** Windows 10/11 (Preferred, due to some automation scripts, though core features work cross-platform).
- **Python:** [Python 3.10 or higher](https://www.python.org/downloads/) (Make sure to check "Add Python to PATH" during installation).
- **Git:** [Git for Windows](https://git-scm.com/downloads) (to clone the repository).
- **Ollama:** [Ollama](https://ollama.com/) (The core local LLM engine).
- **PostgreSQL (Optional but recommended):** A local PostgreSQL database server. If not available, the system can fallback to SQLite.

---

## 📥 2. Clone the Repository

Open your terminal or command prompt and run:

```bash
git clone https://github.com/yogavinay/KrishnaOS-.git
cd KrishnaOS-
```

---

## 📦 3. Install Dependencies

Install all required Python packages using `pip`. 

```bash
pip install -r requirements.txt
```

*(Note: If you run into issues with PyAudio during installation, you may need to install Visual Studio Build Tools first).*

---

## 🔑 4. Environment Configuration

The system relies on a `.env` file for API keys, model configuration, and database settings.

1. Locate the `.env.example` file in the root directory.
2. Duplicate it and rename the copy to `.env`.
3. Open `.env` in a text editor and fill in your details:

```env
# Ollama Configuration
OLLAMA_MODEL=qwen3:8b
OLLAMA_BASE_URL=http://localhost:11434/v1

# Enable Voice Output (Edge-TTS)
TTS_ENABLED=true
TTS_VOICE=en-US-GuyNeural

# External API Keys (Required for Arjuna Agent's Web Search)
TAVILY_API_KEY=your_tavily_api_key_here

# Database String (Update with your PostgreSQL credentials)
DATABASE_URL=postgresql://postgres:password@localhost:5432/mahabharata
```

---

## 🧠 5. Prepare Local AI Models (Ollama)

Before launching the system, you must ensure your local LLM is downloaded in Ollama. Open a new terminal window and run:

```bash
ollama run qwen3:8b
```
*(You can replace `qwen3:8b` with `llama3` or `mistral` depending on what you put in your `.env` file. Wait for the download to finish).*

---

## 🚀 6. Launching the System

You have a few ways to run the Mahabharata System based on your needs.

### Option A: Quick Start (Windows)
Simply double-click the **`startup.bat`** file in the main folder.
This script will:
- Check if Ollama is running (and start it if not).
- Launch the main system.
- Automatically open the Web Dashboard (http://localhost:8000) in your default browser.

### Option B: Terminal / CLI Execution
Run the system manually via the entry point:

```bash
# Standard Interactive Text Mode
python main.py

# Immersive Voice Mode (Listens via Microphone)
python main.py --voice

# API / Dashboard Only Mode
python main.py --api
```

### Option C: Windows Auto-Startup
If you want the AI council to boot up automatically every time you log into Windows:
1. Open PowerShell **as Administrator**.
2. Run the registration command:
```powershell
python main.py --register
```
*(This sets up `register_startup.ps1` to place a shortcut in your Windows Startup folder).*

---

## 🛠️ Troubleshooting

- **Database Errors?** If you don't have PostgreSQL installed, change the `DATABASE_URL` in your `.env` to `sqlite:///./mahabharata.db`.
- **Microphone not working in Voice Mode?** Ensure your default recording device is set correctly in Windows settings and grant microphone permissions to terminal/python.
- **Port 8000 in use?** If the dashboard fails to start, another program is likely using port 8000. You can modify the Uvicorn port in `main.py` if necessary.

---
**Enjoy your new Local Multi-Agent AI System!** 🕉️
