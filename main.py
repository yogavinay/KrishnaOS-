"""
🕉️ MAHABHARATA SYSTEM - Main Entry Point
Multi-Agent AI Operating System (Local-First with Ollama)

Agents:
  KRISHNA - Master Orchestrator (The Commander)
  ARJUNA  - Search & Knowledge (The Researcher)
  BHIMA   - System Operator (The Executor) — Full OS Access
  DHARMA  - Memory & Personality (The Soul)
  KARNA   - Coder & Engineer (The Builder)

Usage:
  python main.py              # Start with text mode
  python main.py --voice      # Start with voice mode
  python main.py --api        # Start API server only
  python main.py --register   # Register Windows startup
"""

import sys
import os
import threading
import argparse

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def start_api_server(krishna):
    """Start FastAPI server in a thread."""
    import uvicorn
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import FileResponse
    from fastapi.staticfiles import StaticFiles
    from api.routes import router, set_krishna

    app = FastAPI(
        title="MAHABHARATA SYSTEM",
        description="Multi-Agent AI Operating System (Local-First)",
        version="2.0.0"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router, prefix="/api")
    set_krishna(krishna)

    # Serve frontend
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")

    @app.get("/")
    async def serve_frontend():
        return FileResponse(os.path.join(frontend_dir, "index.html"))

    print("[API] 🌐 Starting FastAPI server on http://localhost:8000")
    print("[API] 🖥️  Dashboard at http://localhost:8000")
    print("[API] 📖 API Docs at http://localhost:8000/docs\n")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")


def main():
    parser = argparse.ArgumentParser(description="MAHABHARATA SYSTEM")
    parser.add_argument("--voice", action="store_true", help="Start in voice mode")
    parser.add_argument("--api", action="store_true", help="Start API server only")
    parser.add_argument("--register", action="store_true", help="Register Windows startup")
    parser.add_argument("--no-greeting", action="store_true", help="Skip startup greeting")
    args = parser.parse_args()

    # Register Windows startup
    if args.register:
        from core.krishna.startup import register_windows_startup
        register_windows_startup()
        return

    # Initialize KRISHNA and all agents
    from core.krishna.orchestrator import KrishnaOrchestrator
    krishna = KrishnaOrchestrator()
    krishna.initialize()

    # Startup greeting
    if not args.no_greeting:
        krishna.startup_greeting()

    if args.api:
        # API-only mode
        start_api_server(krishna)
    else:
        # Start API in background thread
        api_thread = threading.Thread(
            target=start_api_server, args=(krishna,), daemon=True
        )
        api_thread.start()

        # Start interactive loop
        krishna.voice_loop()

    # Shutdown
    krishna.shutdown()


if __name__ == "__main__":
    main()
